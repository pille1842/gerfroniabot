from discord.ext.commands import Cog
from discord import Embed, Colour
from datetime import datetime
import logging
import os

class Guestbook(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('gerfroniabot.guestbook')
        self.GUESTBOOK_CHANNEL_ID = int(os.getenv("GUESTBOOK_CHANNEL_ID"))
        self.QUARANTINE_CHANNEL_ID = int(os.getenv("QUARANTINE_CHANNEL_ID"))
        self.MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
        self.guestbook_channel = None
        self.main_channel = None
        self.sessions = {}

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("guestbook")
            self.log.info("Guestbook cog ready")

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.bot.ready:
            return
        if not self.guestbook_channel:
            self.log.debug("Fetching guestbook channel")
            self.guestbook_channel = self.bot.guild.get_channel(self.GUESTBOOK_CHANNEL_ID)
            self.log.debug("Guestbook channel: %s", self.guestbook_channel)
        if not self.main_channel:
            self.log.debug("Fetching main channel")
            self.main_channel = self.bot.guild.get_channel(self.MAIN_CHANNEL_ID)
            self.log.debug("Main channel: %s", self.main_channel)

        self.log.debug("Voice state update for member %s", member)
        self.log.debug("Voice state before is %s", before)
        self.log.debug("Voice state after is %s", after)
        if before.channel is None:
            before_id = None
        else:
            before_id = before.channel.id
        if after.channel is None:
            # Member logged off. Check if he was the last one, then delete the session
            if before_id is not None:
                self.log.debug("# of members in channel: %d", len(before.channel.members))
                if len(before.channel.members) == 0:
                    # Delete the session and return
                    self.log.debug("Deleting session %s", before_id)
                    del self.sessions[before_id]
                    return
        else:
            after_id = after.channel.id
        if before_id != after_id:
            if after_id == self.QUARANTINE_CHANNEL_ID:
                self.log.debug("Ignoring voice status change because after channel is quarantine channel")
                # Don't keep a guestbook for the quarantine channel
                return
            found_session = None
            self.log.debug("Checking all sessions: %s", self.sessions)
            # Member has joined a channel.
            for channel_id in self.sessions:
                self.log.debug("Checking session %s", channel_id)
                session = self.sessions[channel_id]
                self.log.debug("Session content: %s", session)
                for session_member in session["participants"]:
                    if session_member.id == member.id:
                        # Found him! Already a member of this session
                        self.log.debug("Member %s already a participant of session %s, returning", member, channel_id)
                        return
                self.log.debug("Comparing %s == %s", channel_id, after.channel.id)
                if channel_id == after.channel.id:
                    # Found the session! Save it
                    found_session = channel_id
                    self.log.debug("Found the right session: %s", found_session)

            # At this point, either there is no session or the member is not part of it.
            # If there is no session, create one and add the member to it.
            # Then post a message to the guestbook channel.
            if found_session is None:
                self.log.debug("Creating new session")
                session = {
                    "participants": [member],
                    "message_id": None,
                    "date": datetime.now(),
                    "channel_name": after.channel.name
                }
                self.log.debug(session)
                found_session = after.channel.id
                self.sessions[found_session] = session
                message = await self.guestbook_channel.send(embed=self.create_guestbook_embed(after.channel.name, datetime.utcnow(), [member]))
                self.sessions[found_session]["message_id"] = message.id
            else:
                self.log.debug("Updating existing session %s", found_session)
                if len(self.sessions[found_session]["participants"]) == 1:
                    # This is a new session where only the second member joined. Inform everyone!
                    await self.main_channel.send(content=":microphone2: **Im Kanal %s findet ein Sprachchat statt!**" % after.channel.name)
                self.sessions[found_session]["participants"].append(member)
                self.log.debug("Participants of session %s: %s", found_session, ", ".join(["{member.name}" for member in self.sessions[found_session]["participants"]]))
                message = await self.guestbook_channel.fetch_message(self.sessions[found_session]["message_id"])
                self.log.debug("Fetched existing message: %s", message)
                await message.edit(embed=self.create_guestbook_embed(self.sessions[found_session]["channel_name"], self.sessions[found_session]["date"], self.sessions[found_session]["participants"]))
        else:
            self.log.debug("Channel before and channel after are the same, doing nothing")

    def create_guestbook_embed(self, channel, date, participants):
        embed = Embed(
            title=":book: Stammtisch im Kanal %s" % channel,
            description=f"",
            timestamp=date,
            colour=Colour.dark_grey()
        )

        fields = [("Teilnehmer", "\n".join([f"{member.name}" for member in participants]), False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        return embed

def setup(bot):
    bot.add_cog(Guestbook(bot))
