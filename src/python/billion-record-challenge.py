from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from sys import exit

from click import argument
from click import command
from click import echo

BUFFER_SIZE: int = 8192 * 8192


@dataclass
class Stats:
    city: str
    min_temperature: float = float("inf")
    max_temperature: float = float("-inf")
    sum: float = 0.0
    count: int = 0

    def average(self) -> float:
        return self.sum / self.count if self.count > 0 else 0.0


def time_past_since(point: datetime) -> str:
    """Return a formatted string representing elapsed time since a given point."""
    current_time = datetime.now()
    delta = current_time - point

    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


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

    stats: dict[str, Stats] = dict()
    with source.open("r", encoding="utf-8", buffering=BUFFER_SIZE) as file:
        record_processed = 0
        for row in file:
            city, _, temperature_str = row.partition(";")

            record = stats.setdefault(city, Stats(city))

            temperature = float(temperature_str)
            record.min_temperature = min(record.min_temperature, temperature)
            record.max_temperature = max(record.max_temperature, temperature)
            record.sum += temperature
            record.count += 1

            record_processed += 1
            if record_processed > 0 and record_processed % 50_000_000 == 0:
                echo(f"Process {record_processed:,} measurements in {time_past_since(start_point)}")

    for record in sorted(stats.values(), key=lambda item: item.city):
        print(f"{record.city}/{record.min_temperature}/{record.max_temperature}/{record.average():.1f}")

    echo(f"The file was processed in {time_past_since(start_point)}")


if __name__ == "__main__":
    main()
