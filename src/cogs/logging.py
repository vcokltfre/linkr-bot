from discord.ext import commands

from loguru import logger

from src.bot import Bot


class Logging(commands.Cog):
    """Event logging for Linkr."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        logger.info("Connected to the Discord gateway.")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Internal cache is ready.")


def setup(bot: Bot):
    bot.add_cog(Logging(bot))
