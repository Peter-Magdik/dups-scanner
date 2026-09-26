import sqlite3
from typing import cast


class Database:
    def __init__(self, connection: sqlite3.Connection):
        self.con: sqlite3.Connection = connection
        self.cur: sqlite3.Cursor = connection.cursor()
        _ = self.cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                file_size INTEGER, 
                source INTEGER CHECK(source IN (0,1)));
        """)

        self.con.commit()

    def insert(self, files: list[tuple[str, str, int, bool]]) -> None:
        _ = self.cur.executemany(
            "INSERT OR IGNORE INTO files (file_path, file_size, source) VALUES (?, ?, ?)",
            files
        )
        self.con.commit()
    
    def find_dupes(self) -> list[tuple[str, str]]:
        _ = self.cur.execute("""
            SELECT
                s.file_path AS source_path,
                t.file_path AS target_path
            FROM files s
            JOIN files t
            s.file_size = t.file_size
            WHERE s.source = 1
            AND t.source = 0;

        """)
        return self.cur.fetchall()

    def count(self) -> int:
        """
        Return the total number of files stored in the database.

        Returns:
        
            `int`: The number of files.

            Returns `-1` if the count query returns no row.
        """

        row: tuple[int] | None = cast(
            tuple[int] | None,
            self.cur.execute("SELECT COUNT(*) FROM files").fetchone()
        )

        if row is None:
            return -1

        result: int = row[0]
        return result