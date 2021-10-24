from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


APP_NAME: str = "docker-compose-watcher"
EXIT_OK: int = 0
EXIT_NOTFOUND: int = 1


class DockerComposeYmlHandler(FileSystemEventHandler):
    """
    Because watchdog fire on_modified twice ,
    I add hack with MIN_TIME_BETWEEN_MODIFIED_EVENTS
    """

    MIN_TIME_BETWEEN_MODIFIED_EVENTS = 5

    def __init__(self, files: list[str]) -> None:
        self.files: list[str] = files
        self.event_times: dict[str:int] = {}
        super().__init__()

    def on_any_event(self, event):
        pass

    def on_modified(self, event):
        if event.src_path not in self.files:
            return
        self.event_times["event.src_path"] = time.time()
        if (
            self.event_times.get(event.src_path, 0) - time.time()
        ) > DockerComposeYmlHandler.MIN_TIME_BETWEEN_MODIFIED_EVENTS:
            return
        print(f"on_modified {event.src_path} {event.event_type}")


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
    current_dir = os.getcwd()
    file_for_watch = Path(current_dir).joinpath(args.file)
    if not file_for_watch.exists() or not file_for_watch.is_file():
        logger.error(f"{file_for_watch} not found")
        parser.print_help()
        return EXIT_NOTFOUND
    observer = Observer()
    observer.schedule(
        DockerComposeYmlHandler(
            [
                file_for_watch.as_posix(),
            ]
        ),
        current_dir,
        recursive=False,
    )
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return EXIT_OK
    finally:
        observer.stop()
        observer.join()
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
