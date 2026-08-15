"""NOT A MODULE"""

import os
import pyperclip
import sys

from loguru import logger
from pathlib import Path


def get_game_path() -> Path:
    logger.info(
        "Enter a value to override the default, or leave empty to use the default."
    )

    game_path = os.environ.get("LEAF_CLIENT_GAME_PATH", "")
    if len(game_path) > 0:
        logger.info(
            "LEAF_CLIENT_GAME_PATH environment variable detected."
            " I will use this as the default value unless you set a new one."
        )
    else:
        game_path = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid"

    in_game_path = input("Project Zomboid game path ({}): ".format(game_path))
    if len(in_game_path) > 0:
        game_path = in_game_path.strip()

    return Path(game_path)


def get_mod_ids() -> list[str]:
    modids = []
    if len(sys.argv) == 1 or sys.argv[1] == "":
        logger.info("Enter a list of mod ids (separated by semicolon)")
        for m in input("$: ").strip().split(";"):
            if len(m) > 0:
                modids.append(m)
    else:
        for m in sys.argv[1].strip().split(";"):
            if len(m) > 0:
                modids.append(m)
        logger.info("Found mod list in first script arg!")

    if len(modids) <= 0:
        logger.error("Mod ids list was empty despite asking explicitly for a list.")
        return []

    return modids


def clear():
    return os.system("cls" if os.name == "nt" else "clear")


def main():
    clear()

    input_mod_ids = get_mod_ids()
    logger.debug("Input mod ids: {}", input_mod_ids)
    if len(input_mod_ids) <= 0:
        logger.error("Input mod id list was empty.")
        return

    game_path = get_game_path()
    logger.debug("game_path = {}", game_path)
    workshop_path = game_path.parent.parent.joinpath("workshop/content/108600")
    logger.debug("workshop_path = {}", workshop_path)

    if not workshop_path.exists():
        logger.error("Steam workshop path () doesn't exist!")
        return

    workshopid_modid_map: dict[str, list[str]] = {}
    for dir in workshop_path.iterdir():
        workshop_id = dir.stem.strip()
        if workshop_id in workshopid_modid_map:
            logger.warning("Workshop id {} already exists in map, skipping...")
            continue

        logger.debug("Workshop id: {}", workshop_id)

        mod_ids = []
        for submod in dir.joinpath("mods").iterdir():
            modid = ""

            logger.debug("Reading mod.info file")
            modinfo = submod.joinpath("mod.info")
            if not modinfo.exists:
                logger.warning("mod.info file doesn't exist, skipping submod")
                continue

            with open(modinfo, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.startswith("id="):
                        modid = line.split("=")[1].strip()
                        logger.debug("Found id= line in mod.info with value: {}", modid)
                        break

            if modid not in input_mod_ids:
                logger.debug(
                    "submod {} was not in the input mod ids, skipping...", submod
                )
                continue

            mod_ids.append(modid)
        
        if len(mod_ids) <= 0:
            logger.debug("No mod ids for this workshop mod match the input mod id list.")
            continue

        logger.debug(
            "Found mod with workshop id {} and mod ids [{}]",
            workshop_id,
            ",".join(mod_ids),
        )
        workshopid_modid_map[workshop_id] = mod_ids

    workshop_ids_str = ";".join(list(workshopid_modid_map.keys()))
    # mod_ids_str = ";".join(list(workshopid_modid_map.values()))

    logger.debug("Copying map to clipboard")
    pyperclip.copy(workshop_ids_str)
    logger.info(
        "The complete list of workshop ids is now copied to your clipboard!"
        " I will also display the list below for your convenience."
    )

    print("\nWorkshop IDs:\n{}".format(workshop_ids_str))


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        logger.critical(e)
