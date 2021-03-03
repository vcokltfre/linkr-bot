from asyncio import get_event_loop
from asyncpg import create_pool
from os import getenv
from loguru import logger
from typing import List

from .models import Webhook


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        self.guilds = {}
        loop = get_event_loop()
        loop.run_until_complete(self.setup())

    async def setup(self):
        logger.info("Setting up database...")
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE", "linkr"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )
        logger.info("Database setup complete.")

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetch_webhooks(self) -> List[Webhook]:
        return [Webhook(d) for d in await self.fetch("SELECT * FROM Webhooks;")]
