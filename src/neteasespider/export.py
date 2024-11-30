import json
import os

import pandas as pd


def extract_metainfo(data: dict) -> dict:
    playlist_id = data["id"]
    playlist_name = data["name"]
    playlist_play_count = data["playCount"]
    playlist_sub_count = data["subscribedCount"]
    playlist_creator = data["creator"]["nickname"]
    playlist_share_count = data["shareCount"]
    playlist_comment_count = data["commentCount"]
    return {
        "playlist_id": playlist_id,
        "playlist_name": playlist_name,
        "playlist_play_count": playlist_play_count,
        "playlist_sub_count": playlist_sub_count,
        "playlist_creator": playlist_creator,
        "playlist_share_count": playlist_share_count,
        "playlist_comment_count": playlist_comment_count,
    }


def extract_tracks(data: dict) -> list[dict]:
    tracks = data["tracks"]
    playlist_id = data["id"]
    result = []
    for track in tracks:
        track_id = track["id"]
        track_name = track["name"]
        result.append(
            {
                "playlist_id": playlist_id,
                "track_id": f"{track_id}",
                "track_name": f'"{track_name}"',
                "artist": f'"{track["artists"][0]["name"]}"',
            }
        )
    return result


def main():
    playlists = []
    data_dir = "output"
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        if not os.path.isfile(file_path):
            continue
        if not file_path.endswith(".json"):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        playlists.append(data)
    track_info = []
    for playlist in playlists:
        track_info.extend(extract_tracks(playlist))
    playlist_data = list(map(extract_metainfo, playlists))
    pd.DataFrame(playlist_data, dtype=str).to_excel(
        "playlist.xlsx",
        index=False,
    )
    pd.DataFrame(track_info, dtype=str).to_excel(
        "track_info.xlsx",
        index=False,
    )


if __name__ == "__main__":
    main()
