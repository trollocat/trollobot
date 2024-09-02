import os
import requests
from ossapi import Ossapi
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("OSU_CLIENT_ID")
client_secret = os.getenv("OSU_CLIENT_SECRET")

api = Ossapi(int(client_id), client_secret)

print(api.user("trollocat").username)
print(api.user(12092800, mode="osu").username)
print(api.beatmap(221777).id)

catboy_url = "https://catboy.best"


def download_beatmap_osu_file(beatmap_id):
    res = requests.get(f"{catboy_url}/osu/{beatmap_id}")
    # returns 200, 404, or 500 according to docs
    if res.status_code == 404:
        print(f"Unable to find map ({beatmap_id})")
        return
    elif res.status_code == 500:
        print(
            f"The api returned a server error for map ({beatmap_id})")
        return
    return res.text


print(download_beatmap_osu_file(3411955))
