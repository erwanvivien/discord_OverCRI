import discord
from discord.ext import commands
import datetime

import discord_utils as disc
import cri
import utils

ERRORS = []
DISC_LNK_DEV = "https://discord.com/api/oauth2/authorize?client_id=819549722422673448&permissions=2147544064&scope=bot%20applications.commands"
DISC_LNK = "https://discord.com/api/oauth2/authorize?client_id=819549623172726824&permissions=2147544064&scope=bot%20applications.commands"
token = utils.get_content("token")

CMDS = {
    # Link to a wallet
    "!!group": utils.get_group_random,
    "!!login": utils.get_login,
    "!!random": utils.get_random,
    "!!": utils.search,
    "!!map": utils.map,
    "!!mappings": utils.mappings,
    "!!define": utils.define,
}


# cri.get_all_users()


class Client(discord.Client):
    async def on_ready(self):
        print(f'[OverCRI] Logged on as {self.user}')
        print(f"invite link: ↓\n{DISC_LNK}")
        print('==============================================================================================')
        print()

        # await disc.report(self, "Started", "Started successfully !")

    async def on_message(self, message):
        if message.author.id in utils.BOT_IDS:        # Doesn't do anything if it's a bot message
            return

        split = message.content.split(' ', 1)  # separate command from args
        cmd = split[0].lower()
        args = split[1].split(' ') if len(split) > 1 else []

        # Get Discord Nick if existant or discord Name
        name = disc.author_name(message.author, False)

        # Runs command if it's a known command
        if cmd != "!!" and cmd in CMDS:
            utils.log("on_message", "Command execution",
                      f"{name} from discord {message.guild.id} issued {cmd} command. <{args}>")

            await CMDS[cmd](self, message, args)
        elif cmd.startswith("!!"):
            args = [cmd[2:]] + args
            utils.log("on_message", "Command execution",
                      f"{name} from discord {message.guild.id} issued !! command. <{args}>")
            await CMDS['!!'](self, message, args)


client = Client()

# Needed for async work
# client.loop.create_task(cron())
client.run(token)
