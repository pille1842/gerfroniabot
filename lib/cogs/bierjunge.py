from datetime import datetime, timedelta
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType, command, cooldown, has_permissions
from discord.ext.commands.errors import MissingPermissions
import os
import logging

class Bierjunge(Cog):
    BJ_LEVELS = ["Bierjunge", "Doktor", "Papst", "kleiner Ozean", "großer Ozean"]

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("gerfroniabot.bierjunge")
        self.QUARANTINE_CHANNEL_ID = int(os.getenv("QUARANTINE_CHANNEL_ID"))
        self.MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
        self.bierjungen = {}
        self.bierverschiss = []
        self.bierkrank = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("bierjunge")
            self.log.info("Bierjunge cog ready")

    @command(name="bierjunge", aliases=["bj"], brief="Hänge einem Mitglied einen Bierjungen an")
    @cooldown(1, 5*60, BucketType.user)
    async def declare_bierjunge(self, ctx, member: Member):
        """
        Erwähne ein Mitglied, um ihm einen Bierjungen anzuhängen. Dein Gegner hat 10 Bierminuten
        Zeit, um die Forderung mit dem Befehl `hängt` anzunehmen oder mit `doppelt` zu verdoppeln, andernfalls
        fährt er in den Bierverschiss. Du kannst niemandem einen Bierjungen anhängen, wenn du oder dein Gegner
        schon in ein anderes Bierduell verwickelt sind. Wenn du dich mit `bierkrank` für bierkrank oder
        bierimpotent erklärt hast, oder wenn du dich im Bierverschiss befindest, kannst du ebenfalls nicht an
        Bierduellen teilnehmen.
        """
        if member.bot:
            await ctx.send(f":beer: Du kannst Bots keinen Bierjungen anhängen. Sie können sich nicht wehren.")
            return
        if ctx.author in self.bierverschiss:
            await ctx.send(f":beer: Du kannst niemanden zum Bierjungen herausfordern, da du im Bierverschiss bist.")
            return
        if ctx.author in self.bierkrank:
            await ctx.send(f":cup_with_straw: Du kannst keine Bierduelle eingehen, da du dich bierkrank gemeldet hast.")
            return
        if member in self.bierkrank:
            await ctx.send(f":cup_with_straw: Du kannst {member.display_name} keinen Bierjungen anhängen, da er bierkrank gemeldet ist.")
            return
        if member in self.bierverschiss:
            await ctx.send(f":beer: Du kannst {member.display_name} nicht zum Bierjungen herausfordern, da er im Bierverschiss ist.")
            return
        for party_a, party_b, bj_level in self.bierjungen.keys():
            if party_a == member or party_b == member:
                await ctx.send(f":beer: Du kannst {member.display_name} keinen Bierjungen anhängen, da er bereits in einen Bierskandal involviert ist.")
                return
            elif party_a == ctx.author or party_b == ctx.author:
                await ctx.send(f":beer: Du kannst {member.display_name} keinen Bierjungen anhängen, da du selbst bereits in einen Bierskandal involviert bist.")
                return
        await ctx.send(f":beer: {ctx.author.display_name} hat {member.mention} einen Bierjungen angehängt! {member.display_name} muss innerhalb"
                    f" von 5 Bierminuten mit {os.getenv('PREFIX')}hängt antworten, sonst wird er zum ersten Mal getreten.")

        self.bot.scheduler.add_job(
            self.send_kick,
            trigger='interval',
            args=[ctx, ctx.author, member, 0],
            minutes=3,
            end_date=datetime.now()+timedelta(minutes=10)
        )
        self.bierjungen[ctx.author, member, 0] = {"num_of_kicks": 0}

    @command(name="hängt", aliases=["ht"], brief="Nimm einen geforderten Bierjungen an")
    async def bierjunge_haengt(self, ctx):
        """
        Wenn du mit `bierjunge` zu einem Bierjungen aufgefordert wurdest oder dein Gegner mit `doppelt` deine
        Forderung verdoppelt hat, kannst du mit `hängt` das Duell annehmen.
        """
        for party_a, party_b, bj_level in self.bierjungen.keys():
            if party_b == ctx.author:
                await ctx.send(f":beer: Du hast die Forderung \"{self.BJ_LEVELS[bj_level]}\" von {party_a.mention} angenommen. Prost!")
                self.bierjungen.pop((party_a, party_b, bj_level))
                return
        await ctx.send(f":beer: Du wurdest zu keinem Bierjungen herausgefordert.")

    @command(name="doppelt", aliases=["dp"], brief="Verdoppele einen geforderten Bierjungen")
    async def haengt_doppelt(self, ctx):
        """
        Wenn du mit `bierjunge` zu einem Bierduell herausgefordert wurdest, kannst du statt mit `hängt` das
        Duell anzunehmen auch mittels `doppelt` die Biermenge verdoppeln. Die Verdopplungsstufen entsprechen
        dem Teutonenkomment: Nach dem Bierjungen kommt der Doktor (2 Bier), dann der Papst (4 Bier), der
        kleine Ozean (8 Bier) und der große Ozean (16 Bier). Nach dem großen Ozean ist keine weitere Verdopplung
        möglich. Wenn du eine Forderung verdoppelst, wird dein Gegner der Geforderte und kann wiederum mit
        `hängt` annehmen oder mit `doppelt` verdoppeln.
        """
        for party_a, party_b, bj_level in self.bierjungen.keys():
            if party_b == ctx.author:
                if bj_level > 3:
                    await ctx.send(f":beer: Du kannst nicht mehr verdoppeln, da es sich bereits um einen großen Ozean handelt."
                                   f" Nimm ihn mit {os.getenv('PREFIX')}hängt an oder du fährst in den Bierverschiss.")
                    return

                await ctx.send(f":beer: {ctx.author.display_name} hat die Forderung von {party_a.mention} verdoppelt."
                               f" Der {self.BJ_LEVELS[bj_level]} ist jetzt ein {self.BJ_LEVELS[bj_level+1]}."
                               f" {party_a.mention}, du bist jetzt der Geforderte und musst innerhalb von"
                               f" 5 Bierminuten mit {os.getenv('PREFIX')}hängt antworten."
                               f" Ansonsten fährst du in den Bierverschiss.")

                self.bierjungen.pop((party_a, party_b, bj_level))
                self.bierjungen[party_b, party_a, bj_level + 1] = {"num_of_kicks": 0}
                self.bot.scheduler.add_job(
                    self.send_kick,
                    trigger='interval',
                    args=[ctx, party_b, party_a, bj_level],
                    minutes=3,
                    end_date=datetime.now()+timedelta(minutes=10)
                )
                return
        await ctx.send(f":beer: Gegen dich besteht keine Forderung, die du verdoppeln könntest.")

    @command("bierverschiss", aliases=["bv"], brief="Schicke ein Mitglied in den Bierverschiss")
    @has_permissions(manage_guild=True)
    async def send_to_bierverschiss(self, ctx, member: Member):
        """
        Mit diesem Befehl kannst du ein Mitglied in den Bierverschiss schicken. Dieser Befehl erfordert
        Server-Verwaltungsrechte. Wenn du ein Mitglied in den Bierverschiss schickst, werden alle ausstehenden
        Bierduelle des Mitglieds für beendet erklärt.
        """
        if member in self.bierverschiss:
            await ctx.send(f":beer: {member.display_name} ist bereits im Bierverschiss.")
            return

        await ctx.send(f":beer: {ctx.author.display_name} hat {member.mention} in den Bierverschiss geschickt.")
        await member.edit(voice_channel=self.bot.guild.get_channel(self.QUARANTINE_CHANNEL_ID))
        self.bierverschiss.append(member)
        await self.remove_all_bierjungen(ctx, member)

    @send_to_bierverschiss.error
    async def send_to_bierverschiss_error(self, ctx, exc):
        if isinstance(exc, MissingPermissions):
            await ctx.send("Du musst Verwaltungsrechte für den Server haben, um diesen Befehl benutzen zu können.")
        else:
            raise exc

    @command("bierehrlich", aliases=["be"], brief="Hole ein Mitglied aus dem Bierverschiss")
    async def get_from_bierverschiss(self, ctx, member: Member):
        """
        Mit diesem Befehl kannst du ein anderes Mitglied aus dem Bierverschiss auspauken. Du kannst dich
        nicht selbst aus dem Bierverschiss auspauken.
        """
        if ctx.author == member:
            await ctx.send(f":beer: Du kannst dich nicht selbst aus dem Bierverschiss auspauken!")
            return

        if member not in self.bierverschiss:
            await ctx.send(f":beer: {member.display_name} ist nicht im Bierverschiss.")
            return

        await ctx.send(f":beer: Wer ist bierehrlich? {member.mention}! Was ist {member.display_name}? Bierehrlich!")
        self.bierverschiss.remove(member)

    @command("listebv", aliases=["lsbv"], brief="Zeige alle Mitglieder im Bierverschiss")
    async def list_bierverschiss(self, ctx):
        """
        Dieser Befehl zeigt eine Bierschissertafel an, auf der alle Mitglieder verzeichnet sind,
        die sich momentan im Bierverschiss befinden.
        """
        if not self.bierverschiss:
            await ctx.send(":beer: Es befindet sich derzeit niemand im Bierverschiss.")
            return
        embed = Embed(title="Bierschissertafel", description="Die folgenden Mitglieder sind im Bierverschiss.")
        embed.add_field(name="Name", value=", ".join(m.display_name for m in self.bierverschiss))
        await ctx.send(embed=embed)

    @command("bierkrank", aliases=["bk"], brief="Erkläre dich selbst für bierkrank oder bierimpotent")
    async def make_bierkrank(self, ctx):
        """
        Wenn du kein Bier zuhause hast oder aus anderen Gründen keines trinken kannst oder willst,
        kannst du dich für bierkrank erklären. Du kannst dann nicht zu Bierduellen herausgefordert werden.
        Wenn du dich für bierkrank erklärst, werden alle ausstehenden Duelle sofort beendet.
        """
        if ctx.author in self.bierkrank:
            await ctx.send(f":cup_with_straw: Du bist bereits bierkrank gemeldet.")
            return

        await ctx.send(f":cup_with_straw: {ctx.author.display_name} hat sich für bierkrank erklärt.")
        self.bierkrank.append(ctx.author)
        if ctx.author in self.bierverschiss:
            self.bierverschiss.remove(ctx.author)
            await ctx.send(f":beer: {ctx.author.display_name} wurde automatisch aus dem Bierverschiss entfernt.")
        await self.remove_all_bierjungen(ctx, ctx.author)

    @command("biergesund", aliases=["bg"], brief="Erkläre deine Bierkrankheit für beendet")
    async def make_biergesund(self, ctx):
        """
        Wenn du wieder trinken willst und für Bierduelle bereitstehst, kannst du dich mit diesem Befehl
        selbst aus der Liste der Bierkranken austragen.
        """
        if ctx.author in self.bierkrank:
            await ctx.send(f":cup_with_straw: {ctx.author.display_name} hat sich aus der Liste der Bierkranken ausgetragen.")
            self.bierkrank.remove(ctx.author)
        else:
            await ctx.send(f":cup_with_straw: Du bist nicht bierkrank gemeldet.")

    @command("listebk", aliases=["lsbk"], brief="Zeige alle bierkranken Mitglieder")
    async def list_bierkrank(self, ctx):
        """
        Dieser Befehl zeigt eine Bierkrankentafel an, auf der alle Mitglieder verzeichnet sind,
        die momentan bierkrank gemeldet sind.
        """
        if not self.bierkrank:
            await ctx.send(":cup_with_straw: Es befindet sich derzeit niemand im Bierverschiss.")
            return
        embed = Embed(title="Bierkrankentafel", description="Die folgenden Mitglieder sind bierkrank gemeldet.")
        embed.add_field(name="Name", value=", ".join(m.display_name for m in self.bierkrank))
        await ctx.send(embed=embed)

    async def send_kick(self, ctx, party_a, party_b, bj_level):
        bj = self.bierjungen[party_a, party_b, bj_level]
        if bj is None:
            return
        num_of_kicks = bj["num_of_kicks"]
        if num_of_kicks == 0:
            await ctx.send(f":beer: {party_b.mention}, ich trete dich zum ersten Mal!"
                           f" Antworte mit {os.getenv('PREFIX')}hängt oder du landest bald im Bierverschiss!")
            self.bierjungen[party_a, party_b, bj_level]["num_of_kicks"] = 1
        elif num_of_kicks == 1:
            await ctx.send(f":beer: {party_b.mention}, ich trete dich zum **zweiten** Mal!"
                           f" Antworte mit {os.getenv('PREFIX')}hängt oder du landest sehr bald im Bierverschiss!")
            self.bierjungen[party_a, party_b, bj_level]["num_of_kicks"] = 2
        elif num_of_kicks == 2:
            await ctx.send(f":beer: {party_b.mention} fährt hiermit wegen versäumter Annahme der Forderung \"{self.BJ_LEVELS[bj_level]}\""
                           f" von {party_a.mention} in den ersten Bierverschiss.")
            self.bierjungen.pop((party_a, party_b, bj_level))
            self.bierverschiss.append(party_b)

    async def remove_all_bierjungen(self, ctx, member):
        for party_a, party_b, bj_level in self.bierjungen:
            if party_a == member or party_b == member:
                await ctx.send(f":beer: Der {self.BJ_LEVELS[bj_level]} zwischen {party_a.display_name} und {party_b.display_name} wurde abgebrochen.")
                self.bierjungen.pop((party_a, party_b, bj_level))
                return

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member in self.bierverschiss and after.channel is not None and after.channel.id != self.QUARANTINE_CHANNEL_ID:
            await member.move_to(self.bot.guild.get_channel(self.QUARANTINE_CHANNEL_ID))
            await self.bot.guild.get_channel(self.MAIN_CHANNEL_ID).send(f":poop: **{member.display_name} hat versucht, aus dem Bierverschiss auszubrechen!**")

def setup(bot):
    bot.add_cog(Bierjunge(bot))
