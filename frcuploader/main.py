#!/usr/bin/env python3

import threading
import time
from sys import argv, exit

import pyforms_lite

from frcuploader.splitter import *

from . import consts
from .forms import *
from .playlistToTBA import main as pttmain
from .updatePlaylistThumbnails import main as uptmain
from .updateTBA import main as utmain
from .youtube import *


def video_splitting_worker():
    print("Splitter worker thread started")
    init_splitter()
    while True:
        check_splitter()
        time.sleep(3)


def main():
    try:
        if os.path.isfile(consts.youtube_oauth_file) or not len(
            os.listdir(consts.yt_accounts_folder)
        ):
            consts.youtube = get_youtube_service()
        elif len(os.listdir(consts.yt_accounts_folder)):
            pyforms_lite.start_app(YouTubeSelector, geometry=(200, 200, 330, 100))
            consts.youtube = get_youtube_service()
    except Exception as e:
        print(e)
        print("There was an issue with getting Google Credentials")
        sys.exit(1)
    if len(argv) > 1:
        if "-p" in argv:
            pttmain()
            exit(0)
        elif "-u" in argv:
            utmain()
            exit(0)
        elif "-t" in argv:
            uptmain()
            exit(0)
        else:
            print("Not a valid option")
            print("Valid options include [-p|-u|-t]")
            print("-p will load playlistToTBA")
            print("-u will load updateTBA")
            print("-t will load updatePlaylistThumbnails")
            exit(0)
    try:
        thread = threading.Thread(target=video_splitting_worker)
        thread.start()
        pyforms_lite.start_app(FRC_Uploader, geometry=(100, 100, 900, 600))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
