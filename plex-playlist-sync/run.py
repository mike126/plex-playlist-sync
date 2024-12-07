import logging
import os
import sys
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from utils.deezer import deezer_playlist_sync
from utils.helperClasses import UserInputs
from utils.spotify import spotify_playlist_sync

# Logging config
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Read ENV variables
userInputs = UserInputs(
    plex_url=os.getenv("PLEX_URL", ""),
    plex_token=os.getenv("PLEX_TOKEN", ""),
    write_missing_as_csv=os.getenv("WRITE_MISSING_AS_CSV", "0") == "1",
    append_service_suffix=os.getenv("APPEND_SERVICE_SUFFIX", "1") == "1",
    add_playlist_poster=os.getenv("ADD_PLAYLIST_POSTER", "1") == "1",
    add_playlist_description=os.getenv("ADD_PLAYLIST_DESCRIPTION", "1") == "1",
    append_instead_of_sync=os.getenv("APPEND_INSTEAD_OF_SYNC", False) == "1",
    wait_seconds=int(os.getenv("SECONDS_TO_WAIT", 86400)),
    spotipy_client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
    spotipy_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", ""),
    spotipy_use_oauth=os.getenv("SPOTIFY_USE_OAUTH", "0") == "1",
    spotipy_redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", ""),
    spotify_user_id=os.getenv("SPOTIFY_USER_ID", ""),
    deezer_user_id=os.getenv("DEEZER_USER_ID", ""),
    deezer_playlist_ids=os.getenv("DEEZER_PLAYLIST_ID", ""),
)

while True:
    logging.info("Starting playlist sync")

    if userInputs.plex_url and userInputs.plex_token:
        try:
            plex = PlexServer(userInputs.plex_url, userInputs.plex_token)
        except:
            logging.error("Plex Authorization error")
            break
    else:
        logging.error("Missing Plex Authorization Variables")
        break

    ########## SPOTIFY SYNC ##########

    logging.info("Starting Spotify playlist sync")

    SP_AUTHSUCCESS = False

    if (
        userInputs.spotipy_client_id
        and userInputs.spotipy_client_secret
        and userInputs.spotify_user_id
    ):
        try:
            if userInputs.spotipy_use_oauth:
                sp = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                        userInputs.spotipy_client_id,
                        userInputs.spotipy_client_secret,
                        redirect_uri=userInputs.spotipy_redirect_uri,
                        scope="playlist-read-private",
                    )
                )
            else:
                sp = spotipy.Spotify(
                    auth_manager=SpotifyClientCredentials(
                        userInputs.spotipy_client_id,
                        userInputs.spotipy_client_secret,
                    )
                )
            SP_AUTHSUCCESS = True
        except:
            logging.info("Spotify Authorization error, skipping spotify sync")

    else:
        logging.info(
            "Missing one or more Spotify Authorization Variables, skipping"
            " spotify sync"
        )

    if SP_AUTHSUCCESS:
        spotify_playlist_sync(sp, plex, userInputs)

    logging.info("Spotify playlist sync complete")

    ########## DEEZER SYNC ##########

    logging.info("Starting Deezer playlist sync")
    dz = deezer.Client()
    deezer_playlist_sync(dz, plex, userInputs)
    logging.info("Deezer playlist sync complete")

    logging.info("All playlist(s) sync complete")
    logging.info("sleeping for %s seconds" % userInputs.wait_seconds)

    time.sleep(userInputs.wait_seconds)
