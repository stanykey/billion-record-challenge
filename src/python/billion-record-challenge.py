from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from sys import exit

from click import argument
from click import command
from click import echo


@dataclass(slots=True)
class Stats:
    min: float = float("inf")
    max: float = float("-inf")
    sum: float = 0.0
    count: int = 0

    def mean(self) -> float:
        return self.sum / self.count if self.count > 0 else 0.0

    def __str__(self) -> str:
        return f"{self.min:.1f}/{self.mean():.1f}/{self.max:.1f}"


def time_past_since(point: datetime) -> str:
    """Return a formatted string representing elapsed time since a given point."""
    current_time = datetime.now()
    delta = current_time - point

    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


def parse_temperature(value: str) -> float:
    """Parse the temperature."""
    return float(value)


def process_line(line: str, stats: dict[str, Stats]) -> None:
    """Parse the file record line."""
    city, _, value = line.partition(";")
    if city not in stats:
        stats[city] = Stats()
    record = stats[city]

    temperature = parse_temperature(value)

    if temperature < record.min:
        record.min = temperature

    if temperature > record.max:
        record.max = temperature

    record.sum += temperature
    record.count += 1


def process_measurements(source: Path) -> dict[str, Stats]:
    buffer_size = 4096 * 4096
    stats: dict[str, Stats] = dict()
    with source.open("r", encoding="utf-8", buffering=buffer_size) as file:
        for line in file:
            process_line(line, stats)

    return stats


def print_statistic(stats: dict[str, Stats]) -> None:
    with StringIO() as buffer:
        buffer.write("{")
        for key in sorted(stats.keys()):
            buffer.write(f"{key}={stats[key]}, ")
        buffer.write("}")

        print(buffer.getvalue())


@command("billion-record-challenge", options_metavar="")
@argument("source", type=Path)
def main(source: Path) -> None:
    """
    Read measurements from a CSV file and print statistics.
    The CSV file is expected to have the following format:

    \b
        <city>;<temperature>
        Example:
        Abha;5.0
        Abidjan;26.0
        Abéché;29.4
        Accra;26.4
        Addis Ababa;16.0
        Adelaide;17.3

    This program reads measurements from a CSV file, where each line represents a city and its temperature. The
    temperature is provided in Celsius. The program calculates and prints statistics for each city, including the
    minimum, average, and maximum temperature.
    """
    if not source.is_file():
        echo("source file is missing", err=True)
        exit(1)

    start_point = datetime.now()

    stats = process_measurements(source)
    print_statistic(stats)

    echo(f"The file was processed in {time_past_since(start_point)}")


if __name__ == "__main__":
    main()
