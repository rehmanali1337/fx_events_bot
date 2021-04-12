import sqlite3
from models.models import Event
import os
import subprocess


class DB:
    def __init__(self):
        self.db_name = 'events.db'
        self.conn = sqlite3.connect(self.db_name, isolation_level=None)
        subprocess.call(['chmod', '777', self.db_name])
        self.cur = self.conn.cursor()
        self.table_name = 'events'
        self.cur.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} (event_id, event_name, date, time, currency, link, impact)")

    def get_events_by_date(self, date):
        self.cur.execute(f'SELECT * FROM {self.table_name} WHERE date = ?',
                         (date,))
        return self.cur.fetchall()

    def event_exists(self, event_id):
        self.cur.execute(f'SELECT * FROM {self.table_name} WHERE event_id = ?',
                         (event_id,))
        return True if self.cur.fetchone() is not None else False

    def add_event(self, event: Event):
        self.cur.execute(f'INSERT INTO {self.table_name} VALUES (?,?,?,?,?,?,?)',
                         (event.id, event.title, event.date, event.time, event.currency,
                          event.link, event.impact))
