"""NOT A MODULE"""

# pylint: disable=consider-using-dict-items

import os

from InquirerPy import inquirer
from yt_dlp import YoutubeDL  # type: ignore


type Preset = dict[str, str | int | bool | list | dict | tuple | Preset]
PRESETS: dict[str, Preset] = {
    "_default": {
        "concurrent_fragment_downloads": 3,
        # "external_downloader": {
        #     "default": "aria2c"
        # },
        "merge_output_format": "mkv",
        "outtmpl": {
            "default": os.getcwd().replace("\\", "/")
            + r"/%(webpage_url_domain)s/%(uploader_id)s/"
            r"[%(upload_date>%Y-%m-%d)s] [%(id)s] %(title)s.%(ext)s"
        },
        "postprocessors": [
            {
                "add_chapters": True,
                "add_infojson": "if_exists",
                "add_metadata": True,
                "key": "FFmpegMetadata",
            }
        ],
        "ratelimit": 6250000,  # 6.25 MBps
        "restrictfilenames": True,
        "writeannotations": True,
        "writedescription": True,
        "writeinfojson": True,
    },
    "_audio-only": {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "0",
            },
        ],
    },
    "youtube": {},
    "youtube-audio": {
        "_inherits": ["_audio-only"],
    },
    "twitch": {
        "throttledratelimit": 1000000,  # 1 MBps
    },
    "twitch-audio": {
        "_inherits": ["_audio-only", "twitch"],
    },
    "kick": {
        "outtmpl": {
            "default": os.getcwd().replace("\\", "/")
            + r"/%(webpage_url_domain)s/%(channel)s/"
            r"[%(upload_date>%Y-%m-%d)s] [%(id)s] %(title)s.%(ext)s"
        },
    },
    "kick-audio": {
        "_inherits": ["_audio-only", "kick"],
    },
    "bunny": {
        "concurrent_fragment_downloads": 4,
        "cookiesfrombrowser": ("firefox", os.environ["BROWSER_PROFILE"], None, None),
        "http_headers": {
            "Referer": "https://iframe.mediadelivery.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0)"
            "Gecko/20100101 Firefox/140.0"
        },
        "nopart": True,
        "outtmpl": {
            "default": os.getcwd().replace("\\", "/")
            + r"/[%(upload_date>%Y-%m-%d)s] %(title)s.%(ext)s"
        },
        "ratelimit": 8250000, # 8.25 MBps
    },
}

PRESET_NAMES = [k for k in PRESETS if not k.startswith("_")]


def clear():
    return os.system("cls" if os.name == "nt" else "clear")


def construct_presets():
    for key in PRESET_NAMES:
        preset = PRESETS["_default"].copy()

        inherited: list[str] = PRESETS[key].get("_inherits", [])  # type: ignore
        for p in inherited:
            preset |= PRESETS[p]
        preset |= PRESETS[key]

        preset.pop("_inherits", None)
        PRESETS[key] = preset


def main():
    clear()
    construct_presets()

    preset: str = inquirer.select(  # type: ignore
        message="Select yt-dlp preset:",
        choices=PRESET_NAMES,
        default=PRESET_NAMES[0],
    ).execute()

    if preset in ["youtube-audio", "kick-audio"]:
        print(
            f"WARNING: {preset.split("-")[0].upper()} does not support audio-only streams, "
            "so the full highest-quality video will be downloaded."
        )

    options = PRESETS[preset]

    ratelimit: str = inquirer.text(  # type: ignore
        message="Enter a custom rate limit (in bytes/s), "
        f"or leave blank for default ({options["ratelimit"]}):"
    ).execute()
    if ratelimit != "":
        options["ratelimit"] = int(ratelimit.strip())

    url_text = ""
    if "twitch" in preset or "kick" in preset:
        url_text = "VOD "
    elif "youtube" in preset:
        url_text = "video "

    url_string: str = inquirer.text(  # type: ignore
        message=f"Enter {url_text}URLs (comma seperated):",
    ).execute()
    if not url_string or len(url_string) == 0:
        print("No URLs provided. Exiting.")
        return

    urls = url_string.split(",")
    with YoutubeDL(options) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    main()
