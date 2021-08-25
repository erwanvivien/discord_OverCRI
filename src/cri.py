# Needed for requests
import requests
# Needed to reed json
import json

# base64 encoding
import base64
from unidecode import unidecode

from threading import Thread, Lock
import numpy as np


ALL_LOGINS = [["erwan", "vivien"], ["hugo", "bois"],
              ["christophe", "terreaux"], ["vahan", "boghossian"],
              ["philippe", "lefebvre"], ["charlie", "brosse"],
              ["david", "horozian"], ["hugo", "houri"], ["zacharie", "constans"]]

ALL_LOGINS = [{"last_name": e[1], "first_name": e[0],
               "login": ".".join(e)} for e in ALL_LOGINS]

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
    "sup": "prepa-sup",
    "spe": "prepa-spe",
    "ing1": "ing-ing1",
    "ing2": "ing-ing2",
    "ing3": "ing-ing3",

    # Labos
    "3ie":  "labo-3ie",
    "lrde": "labo-lrde",
    "lse":  "labo-lse",
    "seal": "labo-seal",

    # Tracks
    "riemann": "ing-ing1-riemann",
    "shannon": "ing-ing1-shannon",
    "tanenbaum": "ing-ing1-tanenbaum",

    # Majeures
    "csi": "ing-csi",
    "gistre": "ing-gistre",
    "gitm": "ing-gitm",
    "image": "ing-image",
    "mit": "ing-mit",
    "rdi": "ing-rdi",
    "sante": "ing-sante",
    "scia": "ing-scia",
    "sigl": "ing-sigl",
    "srs": "ing-srs",
    "tcom": "ing-tcom",

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
    "yaka": "ing-assistants-yaka",
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
    try:
        return r.json()
    except:
        return []


def specific_campus(slug):
    r = requests.get(f"{base_url}/campus/{slug}/", headers=auth)
    try:
        return r.json()
    except:
        return []

# GROUPS


def all_groups():
    r = requests.get(
        f"{base_url}/groups/?kind=semester&private=false", headers=auth)
    try:
        return r.json()
    except:
        return []


def specific_group(slug):
    r = requests.get(f"{base_url}/groups/{slug}/", headers=auth)
    try:
        return r.json()
    except:
        return []


def history_group(slug):
    r = requests.get(f"{base_url}/groups/{slug}/history", headers=auth)
    try:
        return r.json()
    except:
        return []


def members_group(slug, status_code=None):
    if status_code and status_code[0] != 200:
        return []

    r = requests.get(f"{base_url}/groups/{slug}/members/", headers=auth)
    if status_code:
        status_code[0] = r.status_code
    try:
        return r.json()
    except:
        return []

# USERS


def all_users():
    r = requests.get(f"{base_url}/users/", headers=auth)
    try:
        return r.json()
    except:
        return []


def self_user():
    r = requests.get(f"{base_url}/users/me/", headers=auth)
    try:
        return r.json()
    except:
        return []


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
    try:
        return r.json()
    except:
        return []


def search_login(login):
    r = requests.get(f"{base_url}/users/{login}/", headers=auth)
    try:
        return r.json()
    except:
        return []


mutex = Lock()


def format_logins(lst, index, results, known_logins):
    # print(lst, index)
    for e in lst:
        # remove all accents
        login_str = unidecode(e["login"])

        if login_str in known_logins:
            results.append({"first_name": known_logins[login_str][0],
                            "last_name": known_logins[login_str][1],
                            "login": login_str})
            continue

        # split in First/Last name
        login = login_str.split('.')
        if len(login) == 2:
            results.append({"last_name": login[1],
                            "first_name": login[0], "login": login_str})

            mutex.acquire()
            try:
                known_logins[login_str] = [login[0], login[1]]
            finally:
                mutex.release()
        else:
            r = requests.get(e["url"], headers=auth)
            if r.status_code != 200:
                return

            r = r.json()
            if not "last_name" in r or not "first_name" in r:
                continue
            last_name = unidecode(r["last_name"]).lower()
            first_name = unidecode(r["first_name"]).lower()

            print({"last_name": last_name,
                   "first_name": first_name, "login": login_str})
            results.append({"last_name": last_name,
                            "first_name": first_name, "login": login_str})
            mutex.acquire()
            try:
                known_logins[login_str] = [first_name, last_name]
            finally:
                mutex.release()


def get_all_users():
    all_people = []
    try:
        status_code = [200]
        # If cri is down, we can't sum the list as it's dicts
        teachers = members_group("teachers", status_code=status_code)
        # print(teachers, status_code[0])
        administratives = members_group(
            "administratives", status_code=status_code)
        # print(administratives, status_code[0])
        guests = members_group("guests", status_code=status_code)
        # print(guests, status_code[0])
        wheel = members_group("wheel", status_code=status_code)
        # print(wheel, status_code[0])
        ing = members_group("ing", status_code=status_code)
        # print(ing, status_code[0])
        prepa = members_group("prepa", status_code=status_code)
        # print(prepa, status_code[0])
        inter = members_group("inter", status_code=status_code)
        # print(inter, status_code[0])

        all_people = [] + teachers + administratives + \
            guests + wheel + ing + prepa + inter

    except Exception as inst:
        print(inst)
        return None

    if not all_people:
        return None

    all_people = np.array(all_people)

    logins = []

    THREADS = 4
    results = [[] for _ in range(THREADS)]
    threads = [None] * THREADS

    splitted_all_people = np.array_split(all_people, THREADS)

    known_logins = {}
    with open("./db/logins.json", 'r') as logins_file:
        try:
            known_logins = json.load(logins_file)
        except:
            pass

    try:
        for i, lst in enumerate(splitted_all_people):
            threads[i] = Thread(target=format_logins,
                                args=(lst, i, results[i], known_logins))
            threads[i].start()

        for i in range(THREADS):
            threads[i].join()

        with open("./db/logins.json", 'w') as logins_file:
            json.dump(known_logins, logins_file)

        logins = np.concatenate(results)

    except Exception as inst:
        print(inst)

    # Update the global var that stocks the names

    global ALL_LOGINS
    ALL_LOGINS = logins if logins.size != 0 else ALL_LOGINS

    # Returns the json if needed
    return all_people
