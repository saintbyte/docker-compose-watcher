from __future__ import annotations

import argparse
import logging
import os
import subprocess
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
    On linux:
    Because watchdog fire on_modified twice ,
    I add hack with MIN_TIME_BETWEEN_MODIFIED_EVENTS
    """

    MIN_TIME_BETWEEN_MODIFIED_EVENTS = 5

    def __init__(self, files: list[str]) -> None:
        self.files: list[str] = files
        self.event_times: dict[str:float] = {}
        super().__init__()

    def on_any_event(self, event):
        pass

    def on_modified(self, event):
        if event.src_path not in self.files:
            return
        if (
            time.time() - self.event_times.get(event.src_path, 0)
        ) < DockerComposeYmlHandler.MIN_TIME_BETWEEN_MODIFIED_EVENTS:
            self.event_times[event.src_path] = time.time()
            return
        self.event_times[event.src_path] = time.time()
        print(f"on_modified {event.src_path} {event.event_type}")
        result = subprocess.run(
            [
                "docker-compose",
                "config",
                "--file",
                event.src_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(result.stdout.decode("utf-8").split("\n"))
        print(result.stderr.decode("utf-8").split("\n"))


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
