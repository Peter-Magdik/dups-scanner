import sqlite3

class Database:
    def __init__(self, connection: sqlite3.Connection):
        self.con = connection
        self.cur = connection.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                hash TEXT, 
                file_size INTEGER, 
                source INTEGER CHECK(source IN (0,1)));
        """)

        self.con.commit()

    def insert(self, files: list[tuple[str, str, int, bool]]) -> None:
        self.cur.executemany(
            "INSERT OR IGNORE INTO files (file_path, hash, file_size, source) VALUES (?, ?, ?, ?)",
            files
        )
        self.con.commit()
    
    def find_dupes(self) -> list[tuple[str, str]]:
        self.cur.execute("""
            SELECT
                s.file_path AS source_path,
                t.file_path AS target_path
            FROM files s
            JOIN files t
            ON s.hash = t.hash
            AND s.file_size = t.file_size
            WHERE s.source = 1
            AND t.source = 0;

        """)
        return self.cur.fetchall()

    def count(self) -> int:
        return self.cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]