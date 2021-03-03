from loguru import logger

from src.utils import Database


class Distributor:
    """A distributor for webhook messages."""

    def __init__(self, bot):
        self.db: Database = bot.db

        self.channels = {}

        bot.loop.run_until_complete(self.saturate_cache())

    async def saturate_cache(self):
        """Saturate the internal cache with webhooks and channels."""
        logger.info("Starting cache saturation...")

        webhooks = await self.db.fetch_webhooks()
        print(webhooks)
        logger.info(f"Cache saturated with {len(webhooks)} webhooks")
