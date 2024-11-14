import sqlite3
import threading

from settings import settings
from util.decorators import catch_exceptions


class Database(threading.Thread):
    def __init__(self, database_filename: str = settings["DATABASE"]) -> None:
        super(Database, self).__init__()
        self.conn = sqlite3.connect(database_filename, check_same_thread=False, timeout=120.0)
        self.cursor = self.conn.cursor()

    def fetch_all(self, table_name: str) -> tuple:
        """
        Fetch all data from table

        :yield: (id, profile) in a tuple
        """
        for article in self.cursor.execute(f'SELECT * FROM {table_name};').fetchall(): yield list(article)

    @catch_exceptions
    def insert_profile(self, record: tuple) -> bool:
        """
        insert a record to the accounts table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute('INSERT INTO profiles ([profile]) VALUES (?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    @catch_exceptions
    def insert_profile_id(self, record: tuple, table_name: str = 'profiles_ids') -> bool:
        """
        insert a record to the accounts table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :param table_name: name of the table to insert into
        :type table_name: str

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute(f'INSERT INTO {table_name} ([profile_id]) VALUES (?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    def delete_record(self, table_name: str, record_id: int) -> None:
        """ Delete a record from table """
        self.cursor.execute(f'DELETE FROM {table_name} WHERE id={record_id};')
        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def __del__(self) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
