import base64
import datetime
import os
import os.path
import subprocess

import requests_oauthlib
import tbapy

FOLDER = "videos"
EVENT_KEY = "2024incol"

MATCH_TOTAL_TIME = 15 + 3 + 135

MATCH_BEFORE_SECONDS = 5
MATCH_AFTER_SECONDS = 5
SCORE_BEFORE_SECONDS = 3
SCORE_AFTER_SECONDS = 3

TBA_AUTH_KEY = "i60ceyqM8KSe94CMb5OQm19OxZUghZ8oDfjHMwnoUPztvC4g87KBBlWGtN4vkLdN"
tba = tbapy.TBA(TBA_AUTH_KEY)

def get_duration(input_video):
    cmd = [
        "ffprobe",
        "-i",
        input_video,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-sexagesimal",
        "-of",
        "csv=p=0",
    ]
    return subprocess.check_output(cmd).decode("utf-8").strip()


def get_start_time(input_video):
    return int(os.path.getctime(input_video))


def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def clip_from_stream(input_video, output_video, time_segments):
    if len(time_segments) == 1:
        time = time_segments[0]
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_video,
            "-ss",
            time[0],
            "-to",
            time[1],
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            output_video,
        ]
        subprocess.check_output(cmd)
    else:
        open(f"{FOLDER}/concatenate.txt", "w").close()
        for idx, time in enumerate(time_segments):
            output_filename = f"output{idx}.mp4"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_video,
                "-ss",
                time[0],
                "-to",
                time[1],
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                f"{FOLDER}/{output_filename}",
            ]
            subprocess.check_output(cmd)

            with open(f"{FOLDER}/concatenate.txt", "a") as myfile:
                myfile.write(f"file {output_filename}\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-i",
            f"{FOLDER}/concatenate.txt",
            "-c",
            "copy",
            output_video,
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()

        # TODO: Add some error handling here
        # print(output)


def main():
    # test()

    # Pull the list of matches from TBA
    matches = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{EVENT_KEY}/matches/simple",
        headers={
            "X-TBA-Auth-Key": TBA_AUTH_KEY,
        }
    ).json()
    print(matches)


def test():
    stream_start_time = get_start_time(f"{FOLDER}/stream.mp4")
    print(f"Stream start time: {stream_start_time}")

    # Time of match start in seconds since stream start
    match_start_time = (
        stream_start_time + 10 # Pull from API
    ) - stream_start_time

    # Time of match end in seconds since stream start
    match_end_time = (
        match_start_time + MATCH_TOTAL_TIME
    )

    post_result_time = (stream_start_time + 180) - stream_start_time  # Pull from API

    time_segments = [
        [
            format_seconds(match_start_time - MATCH_BEFORE_SECONDS),
            format_seconds(match_end_time + MATCH_AFTER_SECONDS),
        ],
        [
            format_seconds(post_result_time - SCORE_BEFORE_SECONDS),
            format_seconds(post_result_time + SCORE_AFTER_SECONDS),
        ],
    ]
    print(time_segments)
    # clip_from_stream(f"{FOLDER}/stream.mp4", f"{FOLDER}/asdf.mp4", time_segments)


if __name__ == "__main__":
    main()
