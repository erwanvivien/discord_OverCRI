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


async def get_group_random(self, message, args):
    if not args:
        return await disc.error_message(message,
                                        title="Bad usage", desc="No gradu were given")

    group_slug = ""
    if not args:
        groups = cri.all_groups()
        if "detail" in groups:
            return await disc.send_message(message, title=groups["detail"], desc="")

        group = random.choices(groups)
        group_slug = group["slug"]
    else:
        group_slug = args[0]

    group_members = cri.members_group(group_slug)
    if "detail" in group_members:
        return await disc.send_message(message, title=groups["detail"], desc="")

    member = random.choices(group_members)[0]

    login = member["login"]
    image = f"https://photos.cri.epita.fr/thumb/{login}"

    await message.channel.send(image)
    if not args:
        await message.channel.send(f"`Group {group_slug}`")


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

    year = 2023
    for u in users["groups_history"]:
        if u["is_current"]:
            year = u["graduation_year"]

    await message.channel.send(image)
    await message.channel.send(f"`{fname} {sname}`\n`Promo {year}`")


async def get_random(self, message, args):
    pass


async def search(self, message, cmd, args):
    # Contains the commands inside the args
    pass

if not os.path.exists("db"):
    os.mkdir("db")
    f = open(LOG_FILE, "w")
    f.close()
