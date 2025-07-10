"""Converts a list of Steam workshop items into a Steam collection."""

import os
import re
import time
from enum import Enum

from InquirerPy import inquirer
from steam.webauth import WebAuth
from steam.enums.common import EResult, EWorkshopFileType

STEAM_COMMUNITY_DOMAIN = "steamcommunity.com"


class Endpoints(Enum):
    COLLECTION_EDIT = f"https://{STEAM_COMMUNITY_DOMAIN}/sharedfiles/managecollection"
    COLLECTION_ADD = f"https://{STEAM_COMMUNITY_DOMAIN}/sharedfiles/addchild"


def clear():
    return os.system("cls" if os.name == "nt" else "clear")


def main():
    clear()

    username: str = inquirer.text(  # type: ignore
        message="Steam username:",
        validate=lambda t: len(t) > 0,
        invalid_message="Username is invalid.",
    ).execute()
    username = username.strip()

    client = WebAuth(username)
    client.cli_login()

    assert client.logged_on
    clear()
    print(f"Logged in as {client.username} ({client.steam_id})!")

    session = client.session

    collection_id: str = inquirer.text(  # type: ignore
        message="Collection ID to add items to:",
        validate=lambda text: text.isdigit() and len(text) > 0,
        invalid_message="Collection ID must be a positive integer.",
    ).execute()
    collection_id = collection_id.strip()

    # Send a request to the collection page to ensure it exists.

    res = session.get(f"{Endpoints.COLLECTION_EDIT.value}/?id={collection_id}")
    res.raise_for_status()

    if "error_ctn" in res.text:
        print("Steam returned an error when trying to check the collection!")

        err_str = re.search(r"<div id=\"message\">\s*.+\s*.+\s*.+\s*.+\s*<h3>(.+)</h3>", res.text)
        if err_str and len(err_str.groups()) > 0:
            print(f"  - Reason: {err_str.group(0)}")

        session.close()
        return

    workshop_ids_str: str = inquirer.text(  # type: ignore
        message="Workshop IDs to add to the collection (comma-separated):",
        validate=lambda text: len(text) > 0,
        invalid_message="Workshop IDs cannot be empty.",
    ).execute()
    workshop_ids_str = workshop_ids_str.strip().replace(";", ",").replace("/", ",")
    workshop_ids = workshop_ids_str.split(",")

    print(f"Adding {len(workshop_ids)} items to the collection {collection_id}.")
    proceed = inquirer.confirm(  # type: ignore
        message="Proceed?", default=True
    ).execute()

    if proceed is False:
        print("Operation aborted.")
        session.close()
        return

    # Send the requests to add all the items to the collection.

    before = time.time()
    for workshop_id in workshop_ids:
        workshop_id = workshop_id.strip()
        res = session.post(
            Endpoints.COLLECTION_ADD.value,
            data="&".join(
                f"{k}={v}"
                for k, v in {
                    "id": collection_id,
                    "childid": workshop_id,
                    "sessionid": client.sessionID,
                }.items()
            ),
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
        )
        res.raise_for_status()

        json: dict = res.json()
        json_success = int(json.get("success", EResult.Invalid.value))
        json_html = str(json.get("html"))
        json_filetype = int(json.get("fileType", EWorkshopFileType.Community.value))

        if json_success != EResult.OK.value:
            print("Failed to add item to collection.")
            print(f"Reason: Expected success to be OK but got {EResult(json_success).name}")
            break
        elif json_html == "None":
            print("Failed to add item to collection.")
            print("Reason: html is None")
            break

        mod_id_re = re.search(r"Mod ID:\s*([^\"]+)\"", json_html)
        mod_id = mod_id_re.group(1) if mod_id_re else "unknown"

        item_type = "item" if json_filetype != EWorkshopFileType.Collection.value else "collection"
        print(f"Added {item_type} {mod_id} ({workshop_id}) to collection {collection_id}.")
    after = time.time()

    print(f"Adding all workshop items to collection took {(after - before):.2f}s")
    session.close()


if __name__ == "__main__":
    main()
