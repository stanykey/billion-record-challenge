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


def time_past_since(point: datetime) -> str:
    """Return a formatted string representing elapsed time since a given point."""
    current_time = datetime.now()
    delta = current_time - point

    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


def print_statistic(stats: dict[str, Stats]) -> None:
    with StringIO() as buffer:
        buffer.write("{")
        for key in sorted(stats.keys()):
            record = stats[key]
            buffer.write(f"{key}={record.min}/{record.mean():.1f}/{record.max}, ")
        buffer.write("}")
        print(buffer.getvalue())


def process_measurements(source: Path) -> None:
    buffer_size = 4096 * 4096
    stats: dict[str, Stats] = dict()
    with source.open("r", encoding="utf-8", buffering=buffer_size) as file:
        for row in file:
            city, _, temperature_str = row.partition(";")

            if city not in stats:
                stats[city] = Stats()
            record = stats[city]

            temperature = float(temperature_str)

            if temperature < record.min:
                record.min = temperature

            if temperature > record.max:
                record.max = temperature

            record.sum += temperature
            record.count += 1

    print_statistic(stats)


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
    process_measurements(source)
    echo(f"The file was processed in {time_past_since(start_point)}")


if __name__ == "__main__":
    main()
