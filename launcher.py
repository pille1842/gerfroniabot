from lib.bot import Bot
from dotenv import load_dotenv, find_dotenv
import logging
import os

VERSION = "0.2.0"

load_dotenv(find_dotenv())
logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"), format="%(levelname)s %(asctime)s [%(name)s] %(message)s")

bot = Bot()
bot.run(VERSION)
