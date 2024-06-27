import json
from time import sleep

from .ncmapi import ncmapi

DEBUG = False

from datetime import datetime
from functools import partial

from utils import fit_qps


def get_playlist(pid: int):
    data = ncmapi.playlist_detail_v3(pid, limit=0)
    track_ids = data["trackIds"]
    details = data["tracks"]
    # Only fetch tracks manually if not appears in response.
    if not details:
        for music in track_ids:
            music_id = music["id"]

            detail = fit_qps(0.5, partial(ncmapi.song_detail, music_id))
            details.append(detail)

        data["tracks"] = details

    if DEBUG:
        with open(f"data_{pid}.json", "w+", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return data


if __name__ == "__main__":
    print(get_playlist(68688301))
