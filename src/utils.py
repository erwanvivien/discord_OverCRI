# Needed for requests
import requests
# Needed to reed json
import json

# Needed to open files
import os
# Needed to read date
import datetime

# Own wrapper around discord API
import discord_utils as disc
# Own wrapper around CRI API
import cri

import random

LOG_FILE = "db/log"

forbiden_slugs = []

BOT_IDS = []
DEV_IDS = [289145021922279425]


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


CMD_FILE_CONTENT = get_content("CMD_MAP").split('\n')
CMD_MAP = {line.split(": ")[0]: line.split(": ")[1]
           for line in CMD_FILE_CONTENT if line}


async def get_group_random(self, message, args):
    global forbiden_slugs
    group_slug = ""
    if not args:
        groups = cri.all_groups()
        if "detail" in groups:
            return await disc.send_message(message, title=groups["detail"], desc="")

        group = random.choices(groups)
        group = group[0]

        group_slug = group["slug"]
    else:
        group_slug = args[0]

    if group_slug in forbiden_slugs:
        return await get_group_random(self, message, args)

    group_members = cri.members_group(group_slug)
    if "detail" in group_members:
        return await disc.send_message(message, title=groups["detail"], desc="")

    if not group_members:
        forbiden_slugs += [group_slug]
        return await get_group_random(self, message, args)

    member = random.choices(group_members)
    member = member[0]

    login = member["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    await message.channel.send(image)
    if not args:
        await message.channel.send(f"`Login: {login}`\n`Group: {group_slug}`")


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

    users = cri.search_login(login)

    fname = users["first_name"]
    sname = users["last_name"]
    login = users["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    year = int(datetime.datetime.now().year / 100) * 100
    year += int(users["uid"] / 1000)

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`\n`Promo {year}`")


async def fart(self, message, args):
    await disc.send_file(message, "assets/reverbed_fart.mp3")
    await message.delete()


async def poop(self, message, args):
    await disc.send_file(message, "assets/poop.png")
    await message.delete()


async def search(self, message, args):
    if not args:
        return await disc.error_message(
            message, desc="Please provide at least one arg after !! command")
    if len(args) == 1:
        if args[0] in CMD_MAP:
            await disc.send_file(message, CMD_MAP[args[0]])
            return await message.delete()

if not os.path.exists("db"):
    os.mkdir("db")
    f = open(LOG_FILE, "w")
    f.close()
