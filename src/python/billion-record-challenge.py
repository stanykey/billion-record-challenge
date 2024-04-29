from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from sys import exit

from click import argument
from click import command
from click import echo


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


def process_measurements(source: Path) -> dict[bytes, Stats]:
    buffer_size = 4096 * 4096
    registry: dict[bytes, Stats] = dict()
    with source.open("rb", buffering=buffer_size) as file:
        for line in file:
            process_line(line, registry)

    return registry


def print_statistic(registry: dict[bytes, Stats]) -> None:
    result = ", ".join(
        f"{station.decode()}={stats.minimum:.1f}/{stats.mean:.1f}/{stats.maximum:.1f}"
        for station, stats in sorted(registry.items())
    )
    print("{", result, "}", sep="")


@command("billion-record-challenge", options_metavar="")
@argument("source", type=Path)
def main(source: Path) -> None:
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

    registry = process_measurements(source)
    print_statistic(registry)

    echo(f"The file was processed in {time_past_since(start_point)}")


if __name__ == "__main__":
    main()
