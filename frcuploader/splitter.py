from frcuploader import consts
from frcuploader.forms import FRC_Uploader

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
            # Split the match
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
    pass
