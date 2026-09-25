import argparse
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import cast

import constants
from config import Config


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Find and handle duplicate files between two directories."
    )

    _ = parser.add_argument(
        "--source", "-s",
        required=True,
        help="Path to the source directory. Files in this directory are treated as the reference set."
    )

    _ = parser.add_argument(
        "--target", "-t",
        required=True,
        help="Path to the target directory. Files here are checked for duplicates against the source directory."
    )

    _ = parser.add_argument(
        "--hashing_algorithm", "-a",
        choices=["md5", "sha1", "sha256"],
        default="md5",
        help="Hashing algorithm used to compute file digests (default: md5)."
    )

    _ = parser.add_argument(
        "--hashing_mode", "-m",
        choices=["full", "quick"],
        default="full",
        help="Hashing mode: 'full' hashes entire files; 'quick' hashes only the initial chunk for faster but less reliable comparison (default: full)."
    )

    _ = parser.add_argument(
        "--delete", "-d",
        action="store_true",
        help="Automatically delete duplicate files found in the target directory without confirmation."
    )

    _ = parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational logs and show only errors."
    )

    _ = parser.add_argument(
        "--failure-threshold", "-ft",
        type=int,
        default=0,
        metavar="0-100",
        help="Maximum allowed percentage of file processing failures before aborting (default: 0)."
    )

    return parser.parse_args()

def configure_logging(quiet: bool) -> None:
    logging.basicConfig(
        level=logging.ERROR if quiet else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

def cli_to_config() -> Config:
    args: Namespace = parse_args()

    # All types are checked in Config
    source: str = cast(str, args.source)
    target: str = cast(str, args.target)
    hashing_algorithm: str = cast(str, args.hashing_algorithm)
    hashing_mode: str = cast(str, args.hashing_mode)
    delete: bool = cast(bool, args.delete)
    quiet: bool = cast(bool, args.quiet)
    failure_threshold: int = cast(int, args.failure_threshold)

    configure_logging(quiet)

    try:
        return Config(
            source=source,
            target=target,
            hashing_algorithm=hashing_algorithm,
            hashing_mode=hashing_mode,
            delete=delete,
            quiet=quiet,
            failure_threshold=failure_threshold,
        )
    except ValueError as e:
        logging.error("Unable to process configuration: %s", e)
        sys.exit(constants.EXIT_CONFIG_ERROR)