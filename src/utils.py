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
    pass


async def get_login(self, message, args):
    if not args:
        return await disc.error_message(message,
                                        title="Bad usage", desc="Not arguments were given")
    users = cri.search_login(args[0])
    for u in users:
        print(u)
        print()


async def get_random(self, message, args):
    pass


async def search(self, message, cmd, args):
    # Contains the commands inside the args
    pass

if not os.path.exists("db"):
    os.mkdir("db")
    f = open(LOG_FILE, "w")
    f.close()
