from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from typing import Optional
import logging
import os

def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            # Show optional params with [brackets], required arguments with <chevrons>
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_aliases} {params}```"

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=int(os.getenv("HELP_COMMANDS_PER_PAGE", 5)))

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title="Hilfe",
            description="Übersicht aller Befehle dieses Bots",
            colour=self.ctx.author.colour
        )
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset} - {min(len_data, offset + self.per_page - 1)} von {len_data} Befehlen.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append(((entry.brief or "Keine Zusammenfassung verfügbar"), syntax(entry)))

        return await self.write_page(menu, fields)

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("gerfroniabot.help")
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(
            title=f"Hilfe zu `{command}`",
            description=syntax(command),
            colour=ctx.author.colour
        )
        embed.add_field(name="Zusammenfassung", value=(command.brief or "Keine Zusammenfassung verfügbar"), inline=False)
        embed.add_field(name="Beschreibung", value=("Keine Beschreibung" if command.help is None else command.help.replace("\n", " ")), inline=False)
        await ctx.send(embed=embed)

    @command(name="hilfe", aliases=["help", "h"], brief="Zeige eine Übersicht aller Befehle oder Hilfe zu einem bestimmten Befehl")
    async def show_help(self, ctx, cmd: Optional[str]):
        """
        Wird `hilfe` ohne Parameter aufgerufen, zeigt es eine Übersicht aller Befehle an.
        Wenn als Parameter `cmd` der Name eines Befehls übergeben wird, dann wird zu diesem Befehl
        eine ausführlichere Hilfe angezeigt.

        Die Hilfe zu einem Befehl zeigt zunächst eine Kurzform der Befehlssyntax. Dabei wird der
        Hauptname des Befehls und alle Aliase, unter denen er ebenfalls aufgerufen werden kann,
        getrennt durch | angezeigt. Erforderliche Parameter werden in <Pfeilklammern> dargestellt.
        Optionale Parameter werden in <eckigen> Klammern dargestellt:

        ```
        befehl|kurzform|kurzform2 <erforderlicher_Parameter> [optionaler_Parameter]
        ```

        Es folgt die Kurzzusammenfassung der Funktion des Befehls sowie eine ausführliche
        Beschreibung.
        """
        if cmd is None:
            menu = MenuPages(
                source=HelpMenu(ctx, list(self.bot.commands)),
                delete_message_after=True,
                timeout=120.0
            )
            await menu.start(ctx)
        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("Diesen Befehl kenne ich nicht.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")
            self.log.info("Help cog ready")

def setup(bot):
    bot.add_cog(Help(bot))
