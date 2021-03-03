from discord.ext import commands
from discord import Intents

from aiohttp import ClientSession
from typing import Optional
from loguru import logger


class Bot(commands.Bot):
    """A subclassed version of commands.Bot with additional features."""

    def __init__(self, *args, **kwargs):
        logger.info("Starting Linkr...")
        intents = Intents.all()

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            *args,
            **kwargs,
        )

        self.http_session: Optional[ClientSession]

    def load_extensions(self, *exts):
        """Load a set of extensions."""
        for ext in exts:
            try:
                self.load_extension(ext)
                logger.info(f"Successfully loaded extension {ext}")
            except Exception:
                logger.error(f"Failed to load extension {ext}", exc_info=True)

    async def login(self, *args, **kwargs) -> None:
        """Create the aiohttp ClientSession before logging in."""

        self.http_session = ClientSession()
        await self.db.setup()

        await super().login(*args, **kwargs)
