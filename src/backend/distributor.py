from collections import defaultdict
from loguru import logger

from src.utils import Database


class Distributor:
    """A distributor for webhook messages."""

    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

        self.channels = defaultdict(list)

        bot.loop.run_until_complete(self.saturate_cache())

    def pick_hook(self, channel_id: int):
        hook = self.channels[channel_id].pop()
        self.channels[channel_id].insert(0, hook)
        return hook

    async def saturate_cache(self):
        """Saturate the internal cache with webhooks and channels."""
        logger.info("Starting cache saturation...")

        webhooks = await self.db.fetch_webhooks()
        for webhook in webhooks:
            self.channels[webhook.channel_id].append(webhook.hook)

        logger.info(f"Cache saturated with {len(webhooks)} webhooks")

    async def send(self, channel_id: int, data: dict):
        if channel_id not in self.channels:
            return

        await self.bot.wait_until_ready()

        return await self.bot.http_session.post(self.pick_hook(channel_id), json=data)
