import os
import os.path
import subprocess

from frcuploader import consts
from frcuploader.forms import FRC_Uploader

MATCH_TOTAL_TIME = 15 + 5 + 135

SECONDS_BEFORE_MATCH = 5
SECONDS_AFTER_MATCH = 5
SECONDS_BEFORE_SCORE = 7
SECONDS_AFTER_SCORE = 23

# TODO: THIS
stream_file = f"{consts.frc_folder}/stream.mp4"
output_folder = f"{consts.frc_folder}/videos"

match_split_list = []


def init_splitter():
    # Check if the file exists
    try:
        with open(consts.split_file) as file:
            # If it does, load the matches
            for line in file:
                match_split_list.append(line.strip())
    except FileNotFoundError:
        # If it doesn't, create the file
        with open(consts.split_file, "w") as file:
            pass


def check_splitter():
    split_new_matches()


def split_new_matches():
    print("Getting new matches...")

    # Get the list of matches from TBA
    # TODO: figure out how to use the event code from FRC_Uploader.get_event_code()
    matches = consts.tba.event_matches(consts.event_code)
    for match in matches:
        # Check if the match has been played
        if match["actual_time"] is None:
            continue

        if not has_been_split(match):
            split_match(match)


def has_been_split(match):
    return match["key"] in match_split_list


def split_match(match):
    # Split the match
    match_key = match["key"]
    print(f"Splitting match: {match_key}")
    match_split_list.append(match_key)

    # Save the match to the file
    with open(consts.split_file, "a") as file:
        file.write(f"{match_key}\n")

    # Get the stream start time
    # stream_start_time = 1710708155 # debug for 2024incol
    stream_start_time = get_stream_start_time(stream_file)

    # Get the match start time
    match_start_seconds = match["actual_time"] - stream_start_time
    match_end_seconds = match_start_seconds + MATCH_TOTAL_TIME
    post_result_seconds = match["post_result_time"] - stream_start_time

    # print("Match start time: ", match_start_seconds)
    # print("Match end time: ", match_end_seconds)
    # print("Post result time: ", post_result_seconds)

    time_segments = [
        [
            format_seconds(match_start_seconds - SECONDS_BEFORE_MATCH),
            format_seconds(match_end_seconds + SECONDS_AFTER_MATCH),
        ],
        [
            format_seconds(post_result_seconds - SECONDS_BEFORE_SCORE),
            format_seconds(post_result_seconds + SECONDS_AFTER_SCORE),
        ],
    ]

    output_file_name = f"{output_folder}/{match_key}.mp4"

    print("Output file name: ", output_file_name)
    print(time_segments)
    clip_from_stream(stream_file, output_file_name, time_segments)


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


def get_stream_start_time(input_video):
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
        open(f"{consts.frc_folder}/temp/concatenate.txt", "w").close()
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
                f"{consts.frc_folder}/temp/{output_filename}",
            ]
            subprocess.check_output(cmd)

            with open(f"{consts.frc_folder}/temp/concatenate.txt", "a") as myfile:
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
        subprocess.check_output(cmd).decode("utf-8").strip()
