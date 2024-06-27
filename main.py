from functools import partial
import json
import os

from api_helper import get_playlist
from utils import fit_qps


def main():
    playlists = []
    for file in os.listdir("spider"):
        file_path = os.path.join("spider", file)
        if not os.path.isfile(file_path):
            continue
        if not file_path.endswith(".json"):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        playlists.extend(data)

    os.makedirs(name="output", exist_ok=True)
    for playlist_id in playlists:
        output_path = os.path.join("output", f"{playlist_id}.json")
        if os.path.isfile(output_path):
            print(f"Skipping {playlist_id} because existing.")
            continue
        playlist_data = fit_qps(0.5, partial(get_playlist, playlist_id))
        with open(output_path, "w+", encoding="utf-8") as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
