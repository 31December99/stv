# -*- coding: utf-8 -*-

import re
import aiosqlite
import logging

# LOG
logging.basicConfig(level=logging.INFO)


class Database:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.file_name)
        return self.db

    async def insert_video(self, table: str, title: str, poster_id: str, bot_url: str) -> bool:
        try:
            await self.db.execute(f"INSERT OR IGNORE INTO {table} (title,poster_id,bot_url)"
                                  f" VALUES (?,?,?)",
                                  (title, poster_id, bot_url,))
            return True
        except (aiosqlite.IntegrityError, Exception) as e:
            print(e)
            return False

    async def create_table(self, table: str):
        page_table = f"""CREATE TABLE IF NOT EXISTS {table} (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                        title       TEXT,
                        poster_id    TEXT,
                        bot_url     TEXT
                    );"""

        await self.db.execute(page_table)

    async def load_table(self, table = 'stv', id_start=0):
        cursor = await self.db.execute(f"SELECT title, bot_url FROM {table} WHERE id>?", (id_start,))
        return [item for item in await cursor.fetchall()]

    async def load_last_id(self, table: str) -> int:
        cursor = await self.db.execute(f"SELECT poster_id FROM {table} ORDER BY poster_id DESC LIMIT 1")
        last_id = await cursor.fetchone()
        return int(last_id[0]) if last_id is not None else 0

    async def close(self):
        await self.db.close()
