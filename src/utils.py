# Needed for requests
import requests
# Needed to reed json
import json

# Needed to open files
import os
# Needed to read date
import datetime

import discord

# Own wrapper around discord API
import discord_utils as disc
# Own wrapper around CRI API
import cri

import random

from jaro import jaro_Winkler
from unidecode import unidecode

LOG_FILE = "db/log"
MAP_FILE = "db/CMD_MAP"

forbiden_slugs = []

BOT_IDS = [819549722422673448, 819549623172726824]
DEV_IDS = [289145021922279425]

diff_promo = [
    cri.GROUP_SLUGS["ing3"],
    cri.GROUP_SLUGS["ing2"],
    cri.GROUP_SLUGS["ing1"],
    cri.GROUP_SLUGS["spe"],
    cri.GROUP_SLUGS["sup"],
]


def get_content(file):
    # Read file content
    try:
        file = open(file, "r")
        s = file.read()
        file.close()
    except Exception as error:
        log("get_content", error, f"error reading file {file}")
        return ""
    return s


def log(fctname, error, message):
    """
    Pretty printer for logs
    """

    now = datetime.datetime.now()
    log = f"[{now}]: " + \
        str(error) + '\n' + ('+' * 4) + (' ' * 4) + \
        fctname + (" " * (20-len(fctname))) + \
        ': ' + message + '\n'

    print(log)

    f = open(LOG_FILE, "a+")

    f.write(log)
    f.close()


CMD_INDEX_URL = 0
CMD_INDEX_DESC = 1

CMD_FILE_CONTENT = get_content(MAP_FILE).split('\n')
CMD_FILE_CONTENT = [e for e in CMD_FILE_CONTENT if e]

CMD_MAP = {}

for e in CMD_FILE_CONTENT:
    cmds = e.split(": ")
    CMD_MAP[cmds[0]] = [cmds[1], cmds[2]]


def full_slug(sub_group):
    sub_group = sub_group.lower()
    if sub_group in cri.GROUP_SLUGS:
        return cri.GROUP_SLUGS[sub_group]
    if sub_group.isnumeric():
        now = datetime.datetime.now()
        year, month = now.year, now.month
        if month >= 9:  # Checks if we are in september or more
            year += 1

        diff = int(sub_group) - year
        print(diff, len(diff_promo))

        if diff < 0 or diff >= len(diff_promo):
            return sub_group

        print(diff_promo)
        print(diff_promo[diff])

        return diff_promo[diff]

    return sub_group


async def get_group_random(self, message, args):
    if not args:
        return await disc.error_message(message,
                                        title="Bad usage", desc="No group-slug were given")

    if args[0] == "help":
        help_strings = [
            f"`{k}" + (" " * (12 - len(str(k)))) + f">` {v}" for k, v in cri.GROUP_SLUGS.items()]
        help_msg = "\n".join(help_strings)

        print(help_msg)

        return await disc.send_message(message,
                                       title="Different groups:", desc=help_msg)

    group = full_slug(args[0])  # Gets the actual group slug

    users = cri.members_group(group)
    if not users or "detail" in users:
        return await disc.error_message(message,
                                        title="Error", desc="This slug was not found. Check [https://cri.epita.fr/search/](https://cri.epita.fr/search/) to know all group slugs")

    user = random.choices(users)[0]
    user = cri.search_login(user["login"])

    fname = user["first_name"]
    sname = user["last_name"]
    login = user["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    year = 2000  # We assume this bot will be old-school by 2100
    year += int(user["uid"] / 1000)

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`")


async def get_login(self, message, args):
    if not args:
        return await disc.error_message(message,
                                        title="Bad usage", desc="No login were given")

    users = cri.search_login(args[0])
    if "detail" in users:
        return await disc.send_message(message, title=users["detail"], desc="")

    fname = users["first_name"]
    sname = users["last_name"]
    login = users["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    year = int(datetime.datetime.now().year / 100) * 100
    year += int(users["uid"] / 1000)

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`\n`Promo {year}`")


async def get_random(self, message, args):
    rdm = random.choices(cri.ALL_LOGINS)[0]

    login = ".".join(rdm)
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    user = cri.search_login(login)

    fname = user["first_name"]
    sname = user["last_name"]
    login = user["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    year = int(datetime.datetime.now().year / 100) * 100
    year += int(user["uid"] / 1000)

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`\n`Promo {year}`")


def double_jaro(args, login):
    jaro = jaro_Winkler(args[0], login[0])
    if len(args) >= 2:
        jaro += jaro_Winkler(args[1], login[1])
    else:
        jaro *= 2
    return jaro


async def search(self, message, args):
    # No args
    if not args or not args[0]:
        return

    # One args probably means it an instant reply with file
    # Or it's a login
    if len(args) == 1:
        if args[0] in CMD_MAP:
            try:
                await message.delete()
            except discord.Forbidden:
                await disc.error_message(message, title="Missing permission", desc="Please give the bot the permission to delete messages\n" +
                                         "This can be at the global level (if you have remove some permission to the BOT)\n" +
                                         "Or at the channel level, see if there are no conflicts between your permissions.")

            path = CMD_MAP[args[0]][CMD_INDEX_URL]
            if path.split('.')[-1] == "txt":
                await message.channel.send(get_content(path))
            else:
                await disc.send_file(message, CMD_MAP[args[0]][CMD_INDEX_URL])
            return
        elif args[0].count(".") == 1:
            return await get_login(self, message, args)

    # Else we parse the Database of logins
    # Makes the assumption that the first one is the best one
    args[0] = unidecode(args[0])
    if len(args) >= 2:
        args[1] = unidecode(args[1])

    best_idx = 0
    best_jaro = double_jaro(args, cri.ALL_LOGINS[0])

    len_logins = len(cri.ALL_LOGINS)
    for i in range(1, len_logins):
        jaro = double_jaro(args, cri.ALL_LOGINS[i])
        if jaro > best_jaro:
            best_jaro = jaro
            best_idx = i

    log("search", "PERSON = JARO", f"{cri.ALL_LOGINS[i]}: {best_jaro}")
    if best_jaro < 0.1:
        return

    login = ".".join(cri.ALL_LOGINS[best_idx])
    user = cri.search_login(login)

    fname = user["first_name"]
    sname = user["last_name"]
    login = user["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    year = int(datetime.datetime.now().year / 100) * 100
    year += int(user["uid"] / 1000)

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`\n`Promo {year}`")


async def map(self, message, args):
    if not args:
        return await disc.error_message(message, desc="Please provide a name to this file")

    bind_to = args[0]
    if bind_to == '--force':
        return await disc.error_message(message, desc="Please provide a name different from --force")
    if bind_to in CMD_MAP and not "--force" in args:
        return await disc.error_message(message, title="This mapping already exists", desc="pass --force to overwrite this file")

    msg = await disc.send_message(message, title="Starting to download", desc="")

    if bind_to in CMD_MAP:
        os.remove(CMD_MAP[bind_to][CMD_INDEX_URL])

    if message.attachments:
        # attach_id = message.attachments[0].id # Unsued ID
        attach_name = message.attachments[0].filename
        attach_url = message.attachments[0].url

        extension = attach_name.split('.')[-1]
        response = requests.get(attach_url)

        content = response.content
    else:
        if len(args) <= 1:
            return await disc.edit_message(msg, title="Error", desc="No text nor attachments were found")
        extension = "txt"
        content = str.encode(" ".join(args[1:]))

    filename = f"assets/{bind_to}.{extension}"

    file = open(filename, "wb")
    file.write(content)
    file.close()

    if bind_to in CMD_MAP:
        CMD_MAP[bind_to] = [filename, CMD_MAP[bind_to][1]]
    else:
        CMD_MAP[bind_to] = [filename, '']

    tmp_map = [
        f"{k}: {v[CMD_INDEX_URL]}: {v[CMD_INDEX_DESC]}" for k, v in CMD_MAP.items()]
    new_cmd_map = "\n".join(tmp_map)

    file = open(MAP_FILE, "w")
    file.write(new_cmd_map)
    file.close()

    await disc.edit_message(msg, title="Success !", desc=f"{bind_to} has been bound.")


async def unmap(self, message, args):
    if not args:
        return await disc.error_message(message, desc="Please provide a valid mapping to delete")

    mapping = args[0]
    if not mapping in CMD_MAP:
        return await disc.error_message(message, desc="Please provide a valid mapping to delete")

    os.remove(CMD_MAP[mapping][CMD_INDEX_URL])
    del CMD_MAP[mapping]

    tmp_map = [
        f"{k}: {v[CMD_INDEX_URL]}: {v[CMD_INDEX_DESC]}" for k, v in CMD_MAP.items()]
    new_cmd_map = "\n".join(tmp_map)

    file = open(MAP_FILE, "w")
    file.write(new_cmd_map)
    file.close()

    await disc.send_message(message, title="Success !", desc=f"The mapping {mapping} has been deleted")


async def mappings(self, message, args):
    msg = ""
    for k, v in CMD_MAP.items():
        msg += f"`{k}`: {v[CMD_INDEX_DESC]}\n"

    await disc.send_message(message, title="Mappings", desc=msg)


async def define(self, message, args):
    if not args:
        return await disc.error_message(message, desc="Please provide a mapping to define")

    if not args[0] in CMD_MAP:
        return await disc.error_message(message, desc="Please provide a mapping that exist")
    if len(args) <= 1:
        return await disc.error_message(message, desc="Please provide a message for this mapping")

    CMD_MAP[args[0]][CMD_INDEX_DESC] = " ".join(args[1:])

    tmp_map = [
        f"{k}: {v[CMD_INDEX_URL]}: {v[CMD_INDEX_DESC]}" for k, v in CMD_MAP.items()]
    new_cmd_map = "\n".join(tmp_map)

    file = open(MAP_FILE, "w")
    file.write(new_cmd_map)
    file.close()

    await disc.send_message(message, title="Success !", desc=f"The mapping {args[0]} has been defined to {CMD_MAP[args[0]][CMD_INDEX_DESC]}")


async def help(self, message, args):
    await message.channel.send(embed=disc.HELP_EMBED)


async def ban(self, message, args):
    if not message.author.id in DEV_IDS:
        return
    if not args or len(args) < 1:
        return
    if not args[0].startswith("<@!"):
        return

    user_id = int(args[0][3:-1])

    member = await self.fetch_user(user_id)
    print(member)
    print(type(member))

    members = message.guild.fetch_members(limit=None)
    print(members)

    member = message.guild.get_member(member.id)
    print(user_id)
    print(member)
    print(type(member))

    print()

    # try:
    #     private_channel = await member.dm_channel()
    #     print(private_channel)
    #     await member.kick(reason="bruh")
    # except Exception as e:
    #     print("ERROR")
    #     print(e)
    #     return


async def choffix(self, message, args):
    await disc.send_file(message, "assets/____choffix.png")


if not os.path.exists("db"):
    os.mkdir("db")
    f = open(LOG_FILE, "w")
    f.close()
