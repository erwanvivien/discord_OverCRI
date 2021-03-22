# Needed for requests
import requests
# Needed to reed json
import json

# base64 encoding
import base64
from unidecode import unidecode


ALL_LOGINS = [["erwan", "vivien"], ["hugo", "bois"],
              ["christophe", "terreaux"], ["vahan", "boghossian"],
              ["philippe", "lefebvre"], ["charlie", "brosse"],
              ["david", "horozian"], ["hugo", "houri"], ["zacharie", "constans"]]
ALL_USERS = []

GROUP_SLUGS = {
    # Sup
    "s1": "prepa-sup-s1",
    "s1#": "prepa-sup-s1s",
    "s2": "prepa-sup-s2",
    "s2#": "prepa-sup-s2s",

    # Spe
    "s3": "prepa-spe-s3",
    "s3#": "prepa-spe-s3s",
    "s4": "prepa-spe-s4",

    # Ing
    "s5":  "ing-ing1-s5",
    "s6":  "ing-ing1-s6",
    "s7":  "ing-ing2-s7",
    "s8":  "ing-ing2-s8",
    "s9":  "ing-ing3-s9",
    "s10": "ing-ing3-s10",

    # Promos
    "spe": "prepa-spe",
    "sup": "prepa-sup",
    "ing1": "ing-ing1",
    "ing2": "ing-ing2",
    "ing3": "ing-ing3",

    # Labos
    "3ie":  "labo-3ie",
    "lrde": "labo-lrde",
    "lse":  "labo-lse",
    "seal": "labo-seal",

    # Departments
    "de": "ing-de",
    "scola": "ing-scolarite",
    "scolarite": "ing-scolarite",

    # Campuses
    "lyon": "lyn",
    "paris": "prs",
    "rennes": "rns",
    "strasbourd": "stg",
    "toulouse": "tls",

    # Assistants
    "acdc": "prepa-assistants-acdc",
    "acu": "ing-assistants-acu",
    "asm": "prepa-assistants-asm",
    "yaka": "prepa-assistants-yaka",
    "assistants": "ing-assistants",
}


def get_content(file):
    # Read file content
    try:
        file = open(file, "r")
        s = file.read()
        file.close()
    except:
        return ""
    return s


# My cri.epita.fr credentials
epita_username = get_content("epita_user")
epita_password = get_content("epita_pass")

# Basic Auth
user_pass = f"{epita_username}:{epita_password}".encode('utf-8')
base64auth = base64.b64encode(user_pass).decode('utf-8')

# Basic Auth Header
auth = {
    "Authorization": f"Basic {base64auth}",
    "accept": "application/json",
}

base_url = "https://cri.epita.fr/api/v2"

# CAMPUS


def all_campus():
    r = requests.get(f"{base_url}/campus/", headers=auth)
    return r.json()


def specific_campus(slug):
    r = requests.get(f"{base_url}/campus/{slug}/", headers=auth)
    return r.json()

# GROUPS


def all_groups():
    r = requests.get(
        f"{base_url}/groups/?kind=semester&private=false", headers=auth)
    return r.json()


def specific_group(slug):
    r = requests.get(f"{base_url}/groups/{slug}/", headers=auth)
    return r.json()


def history_group(slug):
    r = requests.get(f"{base_url}/groups/{slug}/history", headers=auth)
    return r.json()


def members_group(slug):
    r = requests.get(f"{base_url}/groups/{slug}/members/", headers=auth)
    return r.json()

# USERS


def all_users():
    r = requests.get(f"{base_url}/users/", headers=auth)
    return r.json()


def self_user():
    r = requests.get(f"{base_url}/users/me/", headers=auth)
    return r.json()


def search_user(logins=None, uids=None, emails=None, firstnames=None,
                lastnames=None, graduationyears=None, groups=None):

    request = "?"
    if logins:
        request += "logins="
        request += ",".join(logins) + "&"
    if uids:
        request += "uids="
        request += ",".join(uids) + "&"
    if emails:
        request += "emails="
        request += ",".join(emails) + "&"
    if firstnames:
        request += "first_names="
        request += ",".join(firstnames) + "&"
    if lastnames:
        request += "last_names="
        request += ",".join(lastnames) + "&"
    if lastnames:
        request += "last_names="
        request += ",".join(lastnames) + "&"
    if graduationyears:
        request += "graduation_years="
        request += ",".join(graduationyears) + "&"
    if groups:
        request += "groups="
        request += ",".join(groups) + "&"

    # remove last '&'
    request = request[:-1]

    # Check if nothing was passed
    if request == "?":
        return []

    r = requests.get(f"{base_url}/users/search/", headers=auth)
    return r.json()


def search_login(login):
    r = requests.get(f"{base_url}/users/{login}/", headers=auth)
    return r.json()


def get_all_users():
    prepa_people = members_group("prepa")
    ing_people = members_group("ing")

    all_people = prepa_people + ing_people

    logins = []
    for e in all_people:
        # remove all accents
        login = unidecode(e["login"])
        # split in First/Last name
        login = login.split('.')
        if len(login) == 2:
            logins.append(login)

    # Update the global var that stocks the names
    global ALL_LOGINS
    ALL_LOGINS = logins

    global ALL_USERS
    ALL_USERS = all_people

    # Returns the json if needed
    return all_people
