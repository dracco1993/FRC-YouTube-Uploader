from consts import tba
from FRC_Uploader import FRC_Uploader


def get_new_matches():
    # Get the list of matches from TBA
    matches = tba.event_matches(FRC_Uploader._event_code)
    new_matches = []
    for match in matches:
        if match["comp_level"] == "qm":
            new_matches.append(match["match_number"])
    return new_matches
