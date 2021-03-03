from os import getenv
from dotenv import load_dotenv

from src.bot import Bot

load_dotenv()

bot = Bot()

bot.load_extensions(
    "jishaku",
    "src.cogs.logging",
)

bot.run(getenv("TOKEN"))
