"""NOT A MODULE"""

# pylint: disable=consider-using-dict-items

import os

from InquirerPy import inquirer
from yt_dlp import YoutubeDL  # type: ignore


type Preset = dict[str, str | int | bool | list | dict | Preset]
PRESETS: dict[str, Preset] = {
    "_default": {
        "concurrent_fragment_downloads": 3,
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
        "ratelimit": 6250000,  # 50 Mbps
        "writeannotations": True,
        "writedescription": True,
        "writeinfojson": True,
        "merge_output_format": "mkv",
    },
    "youtube": {},
    "youtube-audio": {
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "0",
            },
        ],
    },
    "twitch": {
        "throttledratelimit": 1000000,  # 1 Mbps
    },
    "twitch-audio": {
        "throttledratelimit": 2000000,  # 2 Mbps
        "format": "(bestaudio[acodec^=opus]/bestaudio)/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "0",
            },
        ],
    },
    "kick": {
        "outtmpl": {
            "default": os.getcwd().replace("\\", "/")
            + r"/%(webpage_url_domain)s/%(channel)s/"
            r"[%(upload_date>%Y-%m-%d)s] [%(id)s] %(title)s.%(ext)s"
        },
    },
    "kick-audio": {
        "outtmpl": {
            "default": os.getcwd().replace("\\", "/")
            + r"/%(webpage_url_domain)s/%(channel)s/"
            r"[%(upload_date>%Y-%m-%d)s] [%(id)s] %(title)s.%(ext)s"
        },
        "format": "(bestaudio[acodec^=opus]/bestaudio)/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "0",
            },
        ],
    },
}
PRESET_NAMES = [k for k in PRESETS if k != "_default"]


def clear():
    return os.system("cls" if os.name == "nt" else "clear")


def main():
    clear()

    # Merge default preset with others.
    for key in PRESETS:
        if key == "_default" or PRESETS[key].get("no_defaults"):
            continue
        PRESETS[key] = PRESETS["_default"] | PRESETS[key]

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
