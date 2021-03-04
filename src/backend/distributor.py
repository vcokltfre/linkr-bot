from collections import defaultdict
from asyncio import Lock, sleep
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

        self.locks = {}

        bot.loop.run_until_complete(self.saturate_cache())

    def pick_hook(self, channel_id: int):
        hook = self.webhooks[channel_id].pop()
        self.webhooks[channel_id].insert(0, hook)
        return hook

    def get_network_channel(self, channel_id: int):
        if channel_id not in self.discord_channels:
            return
        return self.discord_channels[channel_id].linkr_channel

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
        if channel_id not in self.webhooks:
            return

        await self.bot.wait_until_ready()

        data["username"] = data["username"] + f" | #{hex(id)[2:]}"
        data["allowed_mentions"] = {"parse": []}

        hook = self.pick_hook(channel_id)
        lock = self.locks.get(hook)
        if not lock:
            lock = Lock(loop=self.bot.loop)
            self.locks[hook] = lock

        if not hook.endswith("?wait=true"):
            hook += "?wait=true"

        await lock.acquire()
        lastresp = None
        for i in range(3):
            response = lastresp = await self.bot.http_session.post(hook, json=data, headers={"X-RateLimit-Precision":"millisecond"})

            headers = response.headers
            status = response.status

            reset_after = float(headers["X-RateLimit-Reset-After"])
            if headers["X-RateLimit-Remaining"] == 0 and status != 429:
                # Depleted the current ratelimit bucket
                logger.warning(f"Ratelimit on channel {channel_id} has been depleted, it's lock will release after {reset_after}s.")
                self.bot.loop.call_later(reset_after, lock.release())

            if 200 <= status < 300:
                lock.release()
                return response

            if status == 404:
                logger.error(f"Received 404 while sending message {id} to channel {channel_id}.")
                lock.release()
                raise Exception() # TODO: Remove the webhook immediately, it doesn't exist anymore
            elif status == 429:
                if not headers.get("Via"):
                    logger.error(f"Ratelimited by cloudflare when sending message {id} to channel {channel_id}")
                    lock.release()
                    raise Exception() # CF banned
                logger.error(f"Ratelimited while sending message {id} to channel {channel_id}, sleeping for {reset_after}s")
                await sleep(reset_after)

        logger.error(f"Failed to send to channel {channel_id} on {id} 3 times: {await lastresp.text()}")
        lock.release()

    async def broadcast(self, id: int, sender: int, channel: str, data: dict):
        if channel not in self.channel_map:
            return

        cids = self.channel_map[channel]

        for cid in cids:
            if cid == sender:
                continue

            await self.send(id, cid, data)

        logger.info(f"Successfully broadcast message {id} on channel {channel} [Sender: {sender}]")
