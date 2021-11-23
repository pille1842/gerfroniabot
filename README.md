# GerfroniaBot
This is a Discord bot developed for the Gerfronia guild.

It uses [discord.py](https://discordpy.readthedocs.io/en/stable/) and its design is heavily based on the excellent
[Ultimate Discord Bot](https://www.youtube.com/playlist?list=PLESMQx4LeD3NmTZ8D1qwQwwSp67kznl-K) YouTube series
from StartupTechTutorials.

## Setup
To set up this bot for your own guild, do the following:

### Clone the repository
Clone the repository to a place of your liking:

```bash
$ git clone https://github.com/pille1842/gerfroniabot
```

### Install requirements
This bot requires Python 3 and has been tested with Python 3.9.2 and Python 3.8.10 on Ubuntu and Debian systems.

The `requirements.txt` file contains a list of all Python packages this bot relies on. You can install all the
requirements with the following command:

```bash
$ pip install -r requirements.txt
```

### Copy the .env.example file and adjust settings
Copy or rename the `.env.example` file to `.env` in the bot's main directory. This file will contain all your settings.
For obtaining some of the settings, particularly the IDs of your guild and channel IDs, I recommend turning on developer
options in your Discord settings.

```bash
# Access token for your bot's account, see e.g. https://www.writebots.com/discord-bot-token/
TOKEN=
# ID of your guild (with developer options enabled, right click on your guild name -> Copy ID)
GUILD_ID=
# User IDs of your bot's owner(s)
OWNER_IDS=
# ID of a channel where bot control messages should be sent
BOTCONTROL_CHANNEL_ID=
# Prefix on which the bot should listen in this guild (+ by default, but change this to anything you like)
PREFIX=+
# Default loglevel for logging messages (note: DEBUG is very noisy!)
LOGLEVEL=INFO
# How many commands should be shown per page on bot help screens
HELP_COMMANDS_PER_PAGE=5
# ID of a channel where the bot will automatically keep a guestbook for voice chats
GUESTBOOK_CHANNEL_ID=
# ID of the main channel of your guild (voice chat notifications will be sent here)
MAIN_CHANNEL_ID=
```

### Run launcher.py to test your bot
From the bot's main directory, run `launcher.py` to confirm that everything is working correctly:

```bash
$ python launcher.py
```

### Enable a systemd service for your bot
An example systemd service file is provided as `gerfroniabot.service`. Copy this file to `~/.config/systemd/user/`
and put in the correct paths to your bot's location on disk.

You can then start this service by issuing:

```bash
$ systemctl --user start gerfroniabot.service
```

To see if any errors occurred, run `systemctl --user status gerfroniabot.service` or look at all the log
messages with``journalctl --user --unit=gerfroniabot.service`.

If you want to permanently enable your bot and have it start running automatically together with the system,
you first need to enable lingering (so that systemd will start your user services even if you are not currently
logged into the system):

```bash
$ sudo systemctl enable-linger $USER
```

Then, enable the bot with the following command:

```bash
$ systemctl --user enable gerfroniabot.service
```

## License
This bot is licensed under the MIT license, see file `LICENSE`.
