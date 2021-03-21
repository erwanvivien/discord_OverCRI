# Needed for requests
import requests
# Needed to reed json
import json

# base64 encoding
import base64

ALL_LOGINS = [["erwan", "vivien"], ["hugo", "bois"],
              ["christophe", "terreaux"], ["vahan", "boghossian"],
              ["philippe", "lefebvre"], ["charlie", "brosse"],
              ["david", "horozian"], ["hugo", "houri"], ["zacharie", "constans"]]


def get_content(file):
    # Read file content
    try:
        file = open(file, "r")
        s = file.read()
        file.close()
    except:
        return ""
    return s


epita_username = get_content("epita_user")
epita_password = get_content("epita_pass")

user_pass = f"{epita_username}:{epita_password}".encode('utf-8')
base64auth = base64.b64encode(user_pass).decode('utf-8')

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
        log = e["login"].split('.')
        if len(log) == 2:
            logins.append(log)

    global ALL_LOGINS
    ALL_LOGINS = logins

    return prepa_people + ing_people
