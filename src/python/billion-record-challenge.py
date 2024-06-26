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
    min: int
    max: int
    sum: int
    count: int

    @property
    def minimum(self) -> float:
        return self.min * 0.1

    @property
    def maximum(self) -> float:
        return self.max * 0.1

    @property
    def mean(self) -> float:
        if self.count == 0:
            return 0.0

        return self.sum / self.count * 0.1


def time_past_since(point: datetime) -> str:
    """Return a formatted string representing elapsed time since a given point."""
    current_time = datetime.now()
    delta = current_time - point

    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


class Statistics:
    __slots__ = "_data"

    def __init__(self) -> None:
        self._data: dict[bytes, Stats] = dict()

    def find(self, key: bytes) -> Stats | None:
        return self._data.get(key, None)

    def items(self) -> tuple[tuple[str, Stats], ...]:
        return tuple((key.decode(encoding="utf-8", errors="ignore"), data) for key, data in self._data.items())

    def __setitem__(self, key: bytes, value: Stats) -> None:
        self._data[key] = value

    def __getitem__(self, key: bytes) -> Stats:
        return self._data[key]

    def __contains__(self, key: bytes) -> bool:
        return key in self._data

    def __ior__(self, other: "Statistics") -> "Statistics":  # the `Self` is unavailable for Pypy (it was added in 3.11)
        for key, data in other._data.items():
            if key in self._data:
                record = self._data[key]
                record.min = min(record.min, data.min)
                record.max = max(record.max, data.max)
                record.sum += data.sum
                record.count += data.count
            else:
                self._data[key] = data

        return self


def parse_temperature(x: bytes) -> int:
    """Parse the temperature (specific float) from a bytes array as an integer."""

    # The ASCII offset for '0' is 48.
    match len(x):
        case 5:  # b"-99.9"
            return -100 * (x[1] - 48) - 10 * (x[2] - 48) - (x[4] - 48)
        case 4:
            if x[0] == 45:  # b"-9.9"
                return -10 * (x[1] - 48) - (x[3] - 48)
            else:  # b"99.9"
                return 100 * (x[0] - 48) + 10 * (x[1] - 48)
        case _:  # b"9.9"
            return 10 * (x[0] - 48) + (x[2] - 48)


def parse_line(line: bytes) -> tuple[bytes, int]:
    index = line.index(b";")
    return line[:index], parse_temperature(line[index + 1 : -1])


def process_line(line: bytes, registry: Statistics) -> None:
    station, temperature = parse_line(line)
    if record := registry.find(station):
        record.min = min(record.min, temperature)
        record.max = max(record.max, temperature)
        record.sum += temperature
        record.count += 1
    else:
        registry[station] = Stats(temperature, temperature, temperature, 1)


def gather(registries: Iterable[Statistics]) -> Statistics:
    merged = Statistics()
    for registry in registries:
        merged |= registry
    return merged


def process_chunk(source: Path, start_byte: int, end_byte: int) -> Statistics:
    offset = (start_byte // ALLOCATIONGRANULARITY) * ALLOCATIONGRANULARITY
    length = end_byte - offset
    registry = Statistics()
    with source.open("rb") as file, mmap(file.fileno(), length, access=ACCESS_READ, offset=offset) as mmapped_file:
        mmapped_file.seek(start_byte - offset)
        for line in iter(mmapped_file.readline, b""):
            process_line(line, registry)

    return registry


def process_measurements(source: Path, pool_size: int) -> Statistics:
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


def print_statistic(registry: Statistics) -> None:
    result = ", ".join(
        f"{station}={stats.minimum:.1f}/{stats.mean:.1f}/{stats.maximum:.1f}"
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
