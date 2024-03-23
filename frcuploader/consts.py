#!/usr/bin/env python3
import os

import pkg_resources
import tbapy

__version__ = pkg_resources.require("FRCUploader")[0].version

# Default Variables
DEBUG = True  # DON'T COMMIT THIS LINE IF TRUE
DEFAULT_TAGS = "{}, frcuploader, FIRST, omgrobots, FRC, FIRST Robotics Competition, robots, Robotics, {game}"
MATCH_TYPE = ("qm", "qf", "sf", "f1m")
DEFAULT_DESCRIPTION = """Footage of the {event_name} is courtesy of {team}.

Red Alliance  ({red1}, {red2}, {red3}) - {redscore}
Blue Alliance ({blue3}, {blue2}, {blue1}) - {bluescore}

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/{event_code}

Follow us on Twitter (@{twit}) and Facebook ({fb}).

For more information and future event schedules, visit our website: {weblink}

Thanks for watching!"""

NO_TBA_DESCRIPTION = """Footage of the {event_name} Event is courtesy of {team}.

Follow us on Twitter (@{twit}) and Facebook ({fb}).

For more information and future event schedules, visit our website: {weblink}

Thanks for watching!"""

CREDITS = """

Uploaded with FRC-YouTube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""

VALID_PRIVACY_STATUSES = ("public", "unlisted", "private")

GAMES = {
    "2024": "FIRST CRESCENDO presented by Haas, FIRST CRESCENDO, FIRST CRESCENDO, Crescendo",
    "2023": "FIRST ENERGIZE: Charged Up, Charged Up, CHARGED UP",
    "2022": "Rapid React, RAPID REACT",
    "2021": "FIRST Rise: Infinite Recharge, Rise: INFINITE RECHARGE, INFINITE RECHARGE",
    "2020": "FIRST Rise: Infinite Recharge, Rise: INFINITE RECHARGE, INFINITE RECHARGE",
    "2019": "FIRST Destination: Deep Space, Destination: Deep Space, Deep Space",
    "2018": "FIRST Power Up, FIRST POWER UP",
    "2017": "FIRST Steamworks, FIRST STEAMworks",
    "2016": "FIRST Stronghold",
    "2015": "Recycle Rush",
    "2014": "Aerial Assist",
    "2013": "Ultimate Ascent",
}

# Extra Stuff
abbrv = "frc"
short_name = "frcuploader"
long_name = "FRC YouTube Uploader"
row_range = "Data!A1:G1"
first_run = True
stop_thread = False
response = None
status = None
error = None
sleep_minutes = 600
retry = 0
youtube = None
tba = tbapy.TBA("i60ceyqM8KSe94CMb5OQm19OxZUghZ8oDfjHMwnoUPztvC4g87KBBlWGtN4vkLdN")
trusted = False
sizes = ("bytes", "KB", "MB", "GB", "TB")
cerem = (
    "None",
    "Opening Ceremonies",
    "Alliance Selection",
    "Closing Ceremonies",
    "Highlight Reel",
)

frc_folder = os.path.join(os.path.expanduser("~"), ".frcuploader")
yt_accounts_folder = os.path.join(frc_folder, "accounts")
youtube_oauth_file = os.path.join(frc_folder, "frc-oauth2-youtube.json")
os.makedirs(yt_accounts_folder, exist_ok=True)

queue_values = os.path.join(frc_folder, "frc_queue_values.txt")
form_values = os.path.join(frc_folder, "frc_form_values.json")
log_file = os.path.join(frc_folder, "frc_log.txt")
split_file = os.path.join(frc_folder, "split_matches.txt")
rec_formats = (".ts", ".mkv", ".avi", ".mp4", ".flv", ".mov")

event_code = "2024inpla"
