import logging
import os
import sqlite3
import sys
from sqlite3 import Connection
from typing import Literal

import constants
from config import Config
from database import Database
from hashing import FileHasher
from scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)


class Controller:
    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self._total_files_scanned: int = 0
        self._unprocessable_files: int = 0

    def _unprocessable_file(self) -> None:
        self._unprocessable_files += 1
        if (
            self._unprocessable_files / self._total_files_scanned * 100
            > self.config.failure_threshold
        ):
            logger.error(msg="Maximum file processing failure threshold exceeded.")
            sys.exit(constants.EXIT_FILE_ERROR)

    def run(self) -> None:
        logger.info(msg="Starting scan")

        try:
            source_files: list[str] = FileScanner.scan(path=self.config.source)
            target_files: list[str] = FileScanner.scan(path=self.config.target)
            self._total_files_scanned = len(source_files) + len(target_files)
            logger.info(
                "Found %d files in source dir and %d files in target dir",
                len(source_files),
                len(target_files),
            )
        except FileNotFoundError as e:
            logger.error("Directory error: %s", e)
            sys.exit(constants.EXIT_FILE_ERROR)
        except (PermissionError, OSError) as e:
            logger.error("OS-level error: %s", e)
            sys.exit(constants.EXIT_UNEXPECTED)

        insert_source_files: tuple[tuple[str, int, Literal[True]], ...] = (
            tuple((path, os.path.getsize(path), True) for path in source_files)
        )

        insert_target_files: tuple[tuple[str, int, Literal[False]], ...] = (
            tuple((path, os.path.getsize(path), False) for path in target_files)
        )

        connection: Connection = sqlite3.connect(":memory:")
        db: Database = Database(connection)

        try:
            db.insert(files=insert_source_files)
            db.insert(files=insert_target_files)

            files_count: int = db.count()

            logger.info("Inserted %d records into memory DB", files_count)
        except sqlite3.Error:
            logger.critical(msg="Insertion into DB was unsuccessful")
            sys.exit(constants.EXIT_DB_ERROR)

        try:
            duplicates: list[tuple[str, str]] = db.find_dupes()
        except sqlite3.Error:
            logger.critical(msg="Execution of DB query was unsuccessful")
            sys.exit(constants.EXIT_DB_ERROR)

        hasher: FileHasher = FileHasher(algorithm=self.config.hashing_algorithm)

        for source_path, target_path in duplicates:
            logger.info(msg=f"Duplicate: {source_path} <-> {target_path}")
            if (
                self.config.delete
                or input("[INPUT]\tDelete second file? (y/N): ").lower() == "y"
            ):
                try:
                    os.remove(path=target_path)
                except (PermissionError, OSError) as e:
                    logger.error(msg=f"Failed to delete {target_path}: {e}")
