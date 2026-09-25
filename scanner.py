import os


class FileScanner:
    @staticmethod
    def scan(path: str, recursive: bool = True) -> list[str]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        scanned_files: list[str] = []

        for file_name in os.listdir(path):
            full_path: str = os.path.join(path, file_name)
            if os.path.isdir(s=full_path):
                if recursive:
                    scanned_files.extend(FileScanner.scan(path=full_path))
            else:
                scanned_files.append(full_path)
        
        return scanned_files