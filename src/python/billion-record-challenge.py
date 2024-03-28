from pathlib import Path
from sys import exit

from click import argument
from click import command
from click import echo


@command("billion-record-challenge", options_metavar="")
@argument("file", type=Path)
def main(file: Path) -> None:
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
    if not file.is_file():
        echo("source file is missing", err=True)
        exit(1)


if __name__ == "__main__":
    main()
