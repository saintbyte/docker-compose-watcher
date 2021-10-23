#!/usr/bin/env python3
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="docker-compose-watcher", usage="%(prog) [options]"
    )
    parser.add_argument("-f", "--file", default="")
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
