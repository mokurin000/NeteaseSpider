from functools import partial
import json
import os

from neteasespider import PLAYLIST_PATH
from neteasespider.utils import fit_qps
from neteasespider.api_helper import get_playlist


def main():
    playlists = []
    for file in os.listdir(PLAYLIST_PATH):
        file_path = os.path.join(PLAYLIST_PATH, file)
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
        print(f"Start fetching {playlist_id}...")
        playlist_data = fit_qps(0.5, partial(get_playlist, playlist_id))
        with open(output_path, "w+", encoding="utf-8") as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
