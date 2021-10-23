#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
from pathlib import Path

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

APP_NAME = "docker-compose-watcher"
EXIT_OK = 0
EXIT_NOTFOUND = 1


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage=f"{APP_NAME} [options]",
        description="Docker-compose watcher - Watch and restart if docker-compose.yml changed",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="docker-compose.yml",
        help="docker-compose.yml file",
    )

    return parser


def main() -> int:
    logger = logging.getLogger(APP_NAME)
    parser = get_parser()
    args = parser.parse_args()
    file_for_watch = Path(os.getcwd()).joinpath(args.file)
    if not file_for_watch.exists() or not file_for_watch.is_file():
        logger.error(f"{file_for_watch} not found")
        parser.print_help()
        return EXIT_NOTFOUND
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, file_for_watch, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
