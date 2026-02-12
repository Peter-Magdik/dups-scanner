import os
import sys
import logging

import sqlite3

import constants
from config import Config
from scanner import FileScanner
from hashing import FileHasher
from database import Database

class Controller:
    def __init__(self, config: Config) -> None: 
        self.config = config
        self._total_files_scanned = 0
        self._unprocessable_files = 0
    
    def _unprocessable_file(self):
        self._unprocessable_files += 1
        if (self._unprocessable_files / self._total_files_scanned * 100 > self.config.failure_threshold):
            logging.error("Maximum file processing failure treshold exceeded.")
            sys.exit(constants.EXIT_FILE_ERROR)


    def _hash_files(self, file_list, hasher_func, source_flag) -> list[str]:
        results = []
        for path in file_list:
            hash_val = hasher_func(path)
            if not hash_val:
                logging.warning("Cannot get hash of %s, skipping this file", path)
                self._unprocessable_file()
                continue
            try:
                size = os.path.getsize(path)
            except OSError as e:
                logging.warning("Cannot get size of %s: %s, skipping this file", path, e)
                self._unprocessable_file()
                continue
            results.append((path, hash_val, size, source_flag))
        return results


    def run(self):
        logging.info("Starting duplicate scan")
        
        try:
            source_files = FileScanner.scan(self.config.source)
            target_files = FileScanner.scan(self.config.target)
            self._total_files_scanned = len(source_files) + len(target_files)
            logging.info("Found %d files in source dir and %d files in target dir", len(source_files), len(target_files))
        except FileNotFoundError as e:
            logging.error("Directory error: %s", e)
            sys.exit(constants.EXIT_FILE_ERROR)
        except Exception as e:
            logging.error("Unexpected error: %s", e)
            sys.exit(constants.EXIT_UNEXPECTED)

        hasher = FileHasher(self.config.hashing_algo)
        hf = hasher.quick_hash if self.config.hashing_mode == "quick" else hasher.full_hash

        hashed_source_files = self._hash_files(source_files, hf, True)
        hashed_target_files = self._hash_files(target_files, hf, False)


        connection = sqlite3.connect(":memory:")
        db = Database(connection)
        
        try:
            db.insert(hashed_source_files)
            db.insert(hashed_target_files)

            files_count = db.count()

            logging.info("Inserted %d records into memory DB", files_count)
        except Exception as e:
            logging.critical("Insertion into DB was unsuccessful: %s", e)
            sys.exit(constants.EXIT_DB_ERROR)

        try:
            duplicates = db.find_dupes()
        except Exception as e:
            logging.critical("Exececution of DB query was unsuccessful: %s", e)
            sys.exit(constants.EXIT_DB_ERROR)

        for source_path, target_path in duplicates:
            logging.info("Duplicate: %s <-> %s", source_path, target_path)
            if self.config.delete or input(f"[INPUT]\tDelete second file? (y/N): ").lower() == "y":
                try:
                    os.remove(target_path)
                except Exception as e:
                    logging.error("Failed to delete %s: %s", target_path, e)