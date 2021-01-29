from aiohttp import request
from discord import Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, has_permissions, cooldown
from discord.ext.commands.errors import MissingPermissions
from random import choice, randint
import logging

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("gerfroniabot.fun")

    @command(name="hallo", aliases=["hi"], brief="Grüße den Benutzer des Befehls")
    async def say_hello(self, ctx):
        """
        Wird dieser Befehl aufgerufen, antwortet er mit einem von mehreren möglichen Grüßen
        und erwähnt den aufrufenden Benutzer.
        """
        await ctx.send(f"{choice(('Hallo', 'Hi', 'Hey', 'Huhu', 'Servus'))} {ctx.author.mention}!")

    @command(name="würfel", aliases=["w"], brief="Wirf einen oder mehrere Würfel")
    @cooldown(3, 60.0, BucketType.user)
    async def roll_dice(self, ctx, num_of_dice: int, size_of_die: int):
        """
        Dieser Befehl erwartet zwei Parameter: `num_of_dice`, die Anzahl der Würfel, die geworfen
        werden sollen (muss eine Ganzzahl größer 0 und kleiner 26 sein); `size_of_die`, die Anzahl
        der Seiten der Würfel (also die maximale Augenzahl; muss eine Ganzzahl größer 1 und kleiner
        101 sein).

        Die Würfe werden in folgender Form ausgegeben: `n1 + n2 + n3 + ... = summe`.
        """
        if num_of_dice < 1 or num_of_dice > 25:
            await ctx.send(":game_die: Ich kann nicht weniger als 1 oder mehr als 25 Würfel auf einmal werfen.")
            return

        if size_of_die < 2 or size_of_die > 100:
            await ctx.send(":game_die: Diese Würfelgröße wird nicht unterstützt.")
            return

        rolls = [randint(1, size_of_die) for i in range(num_of_dice)]
        await ctx.send(":game_die: " + " + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @command(name="echo", aliases=["sag"], brief="Wiederhole, was geschrieben wurde")
    @has_permissions(manage_guild=True)
    async def echo_message(self, ctx, *, message):
        """
        Löscht die Originalnachricht, mit der der Befehl aufgerufen wurde, und gibt ihren Text
        wieder (Echo). Dieser Befehl kann nur von Mitgliedern mit der Berechtigung "Server verwalten"
        verwendet werden.
        """
        await ctx.message.delete()
        await ctx.send(message)

    @echo_message.error
    async def echo_message_error(self, ctx, exc):
        if isinstance(exc, MissingPermissions):
            await ctx.send("Du musst Verwaltungsrechte für den Server haben, um diesen Befehl benutzen zu können.")
        else:
            raise exc

    @command(name="fux", aliases=["fuchs"], brief="Zeige ein süßes Fuchsenbild")
    @cooldown(1, 60.0, BucketType.user)
    async def send_fox(self, ctx):
        """
        Dieser Befehl antwortet mit einem zufällig ausgewählten Bild eines Fuchsen. Grüße
        gehen raus an die API: https://randomfox.ca/floof/.
        """
        async with request("GET", "https://randomfox.ca/floof/") as response:
            if response.status == 200:
                data = await response.json()
                image_link = data["image"]
                embed = Embed(title=":fox_face: Zufallsfux", colour=ctx.author.colour)
                embed.set_image(url=image_link)
                await ctx.send(embed=embed)
            else:
                await ctx.send(":fox_face: Ich konnte leider keinen Zufallsfux generieren.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")
            self.log.info("Fun cog ready")

def setup(bot):
    bot.add_cog(Fun(bot))
