import hashlib
import logging
from _hashlib import HASH


class FileHasher:
    def __init__(self, algorithm: str = "md5") -> None:
        if algorithm.lower() in ("md5", "sha1", "sha256"):
           self.algorithm: str = algorithm.lower()
        else:
            logging.warning("Invalid hashing algorithm type %s, defaulting to md5", algorithm)
            self.algorithm = "md5"
    
    def quick_hash(self, file_path: str, hashing_chunk_size: int = 1_048_576) -> str | None:
        """
        Hashes chunk of file in **file_path** provided by loading chunk of size specified with **hashing_chunk_size**.
        **Returns** hash of specified type in form of **str**.
        """

        hasher: HASH = hashlib.new(name=self.algorithm)
        try:
            with open(file=file_path, mode="rb") as f:
                hasher.update(f.read(hashing_chunk_size))
        except PermissionError:
            logging.warning("Permission denied for %s, excluding file from list", file_path)
            return None
        except Exception as e:
            logging.warning("Unexpected error while reading %s: %s", file_path, e)
            return None

        return hasher.hexdigest()
    
    def full_hash(self, file_path: str, chunk_size: int = 1_048_576) -> str:
        """
        Hashes whole file in **file_path** provided by loading chunks of size specified with **chunk_size** until none left.
        **Returns** hash of specified type in form of **str**.
        """

        hasher: HASH = hashlib.new(name=self.algorithm)

        with open(file=file_path, mode="rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()