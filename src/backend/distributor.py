from collections import defaultdict
from loguru import logger

from src.utils import Database


class Distributor:
    """A distributor for webhook messages."""

    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

        self.webhooks = defaultdict(list)
        self.channel_map = defaultdict(list)
        self.discord_channels = {}

        bot.loop.run_until_complete(self.saturate_cache())

    def pick_hook(self, channel_id: int):
        hook = self.webhooks[channel_id].pop()
        self.webhooks[channel_id].insert(0, hook)
        return hook

    async def saturate_cache(self):
        """Saturate the internal cache with webhooks and channels."""
        logger.info("Starting cache saturation...")

        webhooks = await self.db.fetch_webhooks()
        for webhook in webhooks:
            self.webhooks[webhook.channel_id].append(webhook.hook)

        dchannels = await self.db.fetch_discord_channels()
        for channel in dchannels:
            self.channel_map[channel.linkr_channel].append(channel.id)
            self.discord_channels[channel.id] = channel

        logger.info(f"Cache saturated with {len(webhooks)} webhooks.")

    async def send(self, id: int, channel_id: int, data: dict):
        if channel_id not in self.channels:
            return

        await self.bot.wait_until_ready()

        return await self.bot.http_session.post(self.pick_hook(channel_id), json=data)

    async def broadcast(self, id: int, sender: int, channel: str, data: dict):
        if channel not in self.channel_map:
            return

        cids = self.channel_map[channel]

        for cid in cids:
            if cid == sender:
                continue

            await self.send(id, cid, data)
