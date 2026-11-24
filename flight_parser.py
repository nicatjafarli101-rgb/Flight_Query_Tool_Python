
"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB125"
FIRST_NAME = "Nicat"
LAST_NAME = "Jafarli"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """

    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", metavar="FILE")
    group.add_argument("-d", metavar="FOLDER")
    group.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE", default="db.json")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return error.code

    if (args.i or args.d) and not args.a:
        parser.print_usage(sys.stderr)
        print("Error: -a is required with -i or -d", file=sys.stderr)
        return 2

    if args.j and args.o != "db.json":
        parser.print_usage(sys.stderr)
        print("Error: -o cannot be used with -j", file=sys.stderr)
        return 2

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)

    handler = None

    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or not all(
                isinstance(record, dict) for record in db
            ):
                raise ValueError("JSON database must be an array of objects")

        else:
            if args.i:
                paths = [args.i]

            else:
                if not os.path.isdir(args.d):
                    raise ValueError("input folder does not exist")

                paths = sorted(
                    os.path.join(args.d, name)
                    for name in os.listdir(args.d)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                )

                if not paths:
                    raise ValueError("folder contains no CSV files")

            airports = load_airports(args.a)

            log_path = os.path.join(
                os.path.dirname(os.path.abspath(args.o)),
                "errors.log"
            )

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            with open(args.o, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, (dict, list)):
                raise ValueError("query file must contain an object or array")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_"
                f"{timestamp}.json"
            )

            response_path = os.path.join(args.r, response_name)

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)

        return 0

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
