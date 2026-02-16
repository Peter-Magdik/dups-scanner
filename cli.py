import argparse
import logging
from config import Config
import constants
import sys

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find and handle duplicate files between two directories."
    )

    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Path to the source directory. Files in this directory are treated as the reference set."
    )

    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Path to the target directory. Files here are checked for duplicates against the source directory."
    )

    parser.add_argument(
        "--hashing_algo", "-a",
        choices=["md5", "sha1", "sha256"],
        default="md5",
        help="Hashing algorithm used to compute file digests (default: md5)."
    )

    parser.add_argument(
        "--hashing_mode", "-m",
        choices=["full", "quick"],
        default="full",
        help="Hashing mode: 'full' hashes entire files; 'quick' hashes only the initial chunk for faster but less reliable comparison (default: full)."
    )

    parser.add_argument(
        "--delete", "-d",
        action="store_true",
        help="Automatically delete duplicate files found in the target directory without confirmation."
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational logs and show only errors."
    )

    parser.add_argument(
        "--failure-threshold", "-ft",
        type=float,
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
    args = parse_args()
    
    configure_logging(args.quiet)
    
    try:
        return Config(**vars(args))
    except ValueError as e:
        logging.error("Unable to process configuration: %s", e)
        sys.exit(constants.EXIT_CONFIG_ERROR)