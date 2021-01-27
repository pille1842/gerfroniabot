from ..db import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import sleep
from discord import Embed, Intents, VoiceChannel, FFmpegAudio
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import command
from discord.errors import Forbidden, HTTPException
from discord.ext.commands.errors import MissingPermissions
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown
from glob import glob
import logging
import os

COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument, MissingPermissions)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = os.getenv("PREFIX", "+")
        self.OWNER_IDS = os.getenv("OWNER_IDS").split(",")
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        self.log = logging.getLogger("gerfroniabot.bot")

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=self.PREFIX,
            owner_ids=self.OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            self.log.info(f"Cog {cog} loaded")
        self.log.info("Setup complete")

    def run(self, version):
        self.VERSION = version

        self.log.info("Running setup")
        self.setup()

        self.TOKEN = os.getenv("TOKEN")
        self.log.info("Running bot")
        super().run(self.TOKEN, reconnect=True)

    @command(name="badnerlied")
    async def badnerlied(self, ctx):
        self.log.info("Badnerlied was requested")
        if not self.voiceclient:
            voicechannel = self.get_channel(607935231894224908)
            textchannel = self.get_channel(int(os.getenv("BOTCONTROL_CHANNEL_ID")))
            self.voiceclient = await voicechannel.connect()
            audio_source = FFmpegAudio('../../data/badnerlied.mp3')
            if not self.voiceclient.is_playing():
                await self.voiceclient.play(audio_source, after=self.disconnect_voice)

    async def disconnect_voice(self, err):
        if self.voiceclient:
            await self.voiceclient.disconnect_voice()
            self.voiceclient = None


    async def on_connect(self):
        self.log.info("Bot connected")

    async def on_disconnect(self):
        self.log.warn("Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Da ist leider etwas schiefgelaufen.")

        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, IGNORE_EXCEPTIONS):
            pass
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f":stopwatch: Bitte warte {str(int(exc.retry_after / 60)) + ' Minuten' if exc.retry_after > 60 else str(int(exc.retry_after)) + ' Sekunden'}, bevor du diesen Befehl erneut benutzen kannst.")
        elif hasattr(exc, "original"):
            if isinstance(exc.original, HTTPException):
                await ctx.send("Konnte die Nachricht nicht absenden.")
            elif isinstance(exc.original, Forbidden):
                await ctx.send("Ich bin leider nicht berechtigt, das zu tun.")
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(int(os.getenv("GUILD_ID")))
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            self.log.info("Bot ready")
        else:
            self.log.info("Bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
