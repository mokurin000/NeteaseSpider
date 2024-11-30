import json
from functools import partial

from neteasespider.utils import fit_qps

from neteasespider.api_helper.ncmapi import ncmapi

DEBUG = False


def get_playlist(pid: int):
    data = ncmapi.playlist_detail_v3(pid, limit=0)
    track_ids = data["trackIds"]
    details = data["tracks"]
    # Only fetch tracks manually if not appears in response.
    if not details:
        for music in track_ids:
            music_id = music["id"]
            print(f" - fetching details for music {music_id}...")

            detail = fit_qps(0.5, partial(ncmapi.song_detail, music_id))
            details.append(detail)

        data["tracks"] = details

    if DEBUG:
        with open(f"data_{pid}.json", "w+", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return data


if __name__ == "__main__":
    print(get_playlist(68688301))
