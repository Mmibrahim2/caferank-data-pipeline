import argparse
import json
import logging

from caferank.config import Settings
from caferank.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="CafeRank ETL")
    parser.add_subparsers(dest="command", required=True).add_parser("run")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.command == "run":
        print(json.dumps(run(Settings.from_env())))


if __name__ == "__main__":
    main()

