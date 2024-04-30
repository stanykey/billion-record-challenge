from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from mmap import ACCESS_READ
from mmap import ALLOCATIONGRANULARITY
from mmap import mmap
from multiprocessing import Pool
from os import cpu_count
from pathlib import Path
from sys import exit

from click import argument
from click import command
from click import echo
from click import option


@dataclass(slots=True)
class Stats:
    min: float
    max: float
    sum: float
    count: int

    @property
    def minimum(self) -> float:
        return self.min

    @property
    def maximum(self) -> float:
        return self.max

    @property
    def mean(self) -> float:
        if self.count == 0:
            return 0.0

        return self.sum / self.count


def time_past_since(point: datetime) -> str:
    """Return a formatted string representing elapsed time since a given point."""
    current_time = datetime.now()
    delta = current_time - point

    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


def parse_line(line: bytes) -> tuple[bytes, float]:
    station, _, value = line.partition(b";")
    return station, float(value)


def process_line(line: bytes, registry: dict[bytes, Stats]) -> None:
    station, temperature = parse_line(line)
    if station in registry:
        record = registry[station]

        if record.min > temperature:
            record.min = temperature

        if record.max < temperature:
            record.max = temperature

        record.sum += temperature
        record.count += 1
    else:
        registry[station] = Stats(temperature, temperature, temperature, 1)


def gather(registries: Iterable[dict[bytes, Stats]]) -> dict[bytes, Stats]:
    merged: dict[bytes, Stats] = {}
    for registry in registries:
        for station, stats in registry.items():
            if station in merged:
                record = merged[station]
                record.min = min(record.min, stats.min)
                record.max = max(record.max, stats.max)
                record.sum += stats.sum
                record.count += stats.count
            else:
                merged[station] = stats

    return merged


def process_chunk(source: Path, start_byte: int, end_byte: int) -> dict[bytes, Stats]:
    offset = (start_byte // ALLOCATIONGRANULARITY) * ALLOCATIONGRANULARITY
    length = end_byte - offset
    registry: dict[bytes, Stats] = {}
    with source.open("rb") as file, mmap(file.fileno(), length, access=ACCESS_READ, offset=offset) as mmapped_file:
        mmapped_file.seek(start_byte - offset)
        for line in iter(mmapped_file.readline, b""):
            process_line(line, registry)

    return registry


def process_measurements(source: Path, pool_size: int) -> dict[bytes, Stats]:
    chunks = []
    file_size = source.stat().st_size
    base_chunk_size = file_size // pool_size

    with source.open("rb") as file, mmap(file.fileno(), length=0, access=ACCESS_READ) as mmapped_file:
        start_byte = 0
        for _ in range(pool_size):
            end_byte = min(start_byte + base_chunk_size, file_size)
            end_byte = mmapped_file.find(b"\n", end_byte)
            end_byte = end_byte + 1 if end_byte != -1 else file_size

            chunks.append((source, start_byte, end_byte))

            start_byte = end_byte

    with Pool(processes=pool_size) as pool:
        results = pool.starmap(process_chunk, chunks)

    return gather(results)


def print_statistic(registry: dict[bytes, Stats]) -> None:
    result = ", ".join(
        f"{station.decode()}={stats.minimum:.1f}/{stats.mean:.1f}/{stats.maximum:.1f}"
        for station, stats in sorted(registry.items())
    )
    print("{", result, "}", sep="")


@command("billion-record-challenge", options_metavar="")
@argument("source", type=Path)
@option("--pool-size", default=cpu_count(), type=int, help="Number of CPUs to use", show_default=True)
def main(source: Path, pool_size: int) -> None:
    """
    Read measurements from a CSV file and print statistics.
    The CSV file is expected to have the following format:

    \b
        <station>;<temperature>
        Example:
        Abha;5.0
        Abidjan;26.0
        Abéché;29.4
        Accra;26.4
        Addis Ababa;16.0
        Adelaide;17.3

    This program reads measurements from a CSV file, where each line represents a station and its temperature. The
    temperature is provided in Celsius. The program calculates and prints statistics for each station, including the
    minimum, average, and maximum temperature.
    """
    if not source.is_file():
        echo("source file is missing", err=True)
        exit(1)

    start_point = datetime.now()

    registry = process_measurements(source, pool_size)
    print_statistic(registry)

    echo(f"The file was processed in {time_past_since(start_point)}")


if __name__ == "__main__":
    main()
