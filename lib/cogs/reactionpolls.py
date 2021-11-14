from datetime import datetime, timedelta
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
import logging

class Reactionpolls(Cog):
    NUMBERS = [
        "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
    ]

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("gerfroniabot.reactionpolls")
        self.polls = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reactionpolls")
            self.log.info("Reactionpolls cog ready")

    @command(name="umfrage", aliases=["umf"], brief="Erstelle eine offene Umfrage")
    async def make_poll(self, ctx, minutes: int, question: str, *options):
        """
        Erstelle eine offene Umfrage, auf die alle anderen Mitglieder mit Emojis reagieren können, um abzustimmen.
        Der erste Parameter ist die Dauer in Minuten, nach der der Bot das Ergebnis bekanntgeben wird. Der zweite
        Parameter, der gegebenenfalls in "Anführungszeichen" gesetzt werden muss, wenn er Leerzeichen enthält, ist
        die Frage, die du den Mitgliedern stellen möchtest. Alle weiteren Parameter (durch Leerzeichen getrennt)
        werden als Antwortmöglichkeiten hinzugefügt. Du kannst höchstens zehn Optionen angeben.
        """
        if minutes < 1 or minutes > 120:
            await ctx.send(":ballot_box_with_check: Die Umfragedauer muss zwischen 1 und 120 Minuten liegen.")
            return

        if len(options) > 10:
            await ctx.send(":ballot_box_with_check: Du kannst nicht mehr als 10 Antwortmöglichkeiten festlegen.")
            return

        embed = Embed(
            title=f":ballot_box_with_check: {question}",
            description=f"Umfrage von {ctx.author.display_name}",
            timestamp=datetime.utcnow(),
            colour=ctx.author.colour
        )

        run_until = datetime.now() + timedelta(minutes=minutes)

        fields= [("Antwortmöglichkeiten", "\n".join([f"{self.NUMBERS[idx]} {option}" for idx, option in enumerate(options)]), False),
                 ("Hilfe", f"Reagiere mit der entsprechenden Zahl auf diese Nachricht, um abzustimmen. "
                           f"Die Umfrage läuft bis {run_until.strftime('%H:%M')} Uhr.", False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        message = await ctx.send(embed=embed)

        for emoji in self.NUMBERS[:len(options)]:
            await message.add_reaction(emoji)

        self.polls.append(message.id)
        self.bot.scheduler.add_job(self.complete_poll, "date", run_date=run_until, args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)
        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f":ballot_box_with_check: Die Abstimmung ist beendet. Option {most_voted.emoji} hat mit {most_voted.count-1} Stimmen gewonnen.")


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.polls:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            for reaction in message.reactions:
                if (not payload.member.bot
                    and payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)

def setup(bot):
    bot.add_cog(Reactionpolls(bot))
