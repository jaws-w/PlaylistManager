import requests
from jikanpy import Jikan
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyPKCE

from PIL import Image, ImageTk
from io import BytesIO
import re

jikan = Jikan()

load_dotenv()

MARKET_CODE = "us"
scope = "playlist-modify-private"
SPOTIPY_CLIENT_ID = "baffaf7266d04894a474288165840d28"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

spPKCE = SpotifyPKCE(
    client_id=SPOTIPY_CLIENT_ID, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope
)

sp = spotipy.Spotify(auth_manager=spPKCE)
# user_id = sp.current_user()['id']


# def search_anime(anime_title, page, parameters):
#     print(f"Searching for page {page} of {anime_title}")
#     return jikan.search("anime", anime_title, page=page, parameters=parameters)


def search_anime(anime_title: str, page, parameters):
    api_endpoint = "http://staging.jikan.moe/v4/anime"
    query = f"?q={anime_title}&sfw&page={page}"

    resp = requests.get(api_endpoint + query)
    print(resp.json())
    return resp.json()


def parse_track(track):
    info = re.split('"|by', track)
    title = info[1]
    artist = info[3].split("\xa0")[0][1:]
    return (title, artist)


def get_songs(anime):
    anime_res = jikan.anime(anime["mal_id"])
    ops = []
    eds = []

    for tr in anime_res["opening_themes"]:
        ops.append(parse_track(tr))

    for tr in anime_res["ending_themes"]:
        eds.append(parse_track(tr))

    return {"openings": ops, "endings": eds}


async def set_image(anime, target, size=(50, 70)):
    imgRes = requests.get(anime["images"]['jpg']['image_url'])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    target.configure(image=img)
    target.image = img
    print(f'Image fetched for {anime["title"]}')


def search_spotify(song, artist):
    if "(" in song and ")" in song:
        song = re.search(r"\((.*?)\)", song, re.UNICODE).group(1)
        print(song)
        if "（" in song and "）" in song:
            song = re.sub("（.*?）", "", song, re.UNICODE)
    query = f"{song} {artist}"
    print(query)
    res = sp.search(query, type="track", market=MARKET_CODE, limit=50)

    # if res["tracks"]["total"] == 0:
    #     query = re.sub("[^a-zA-Z0-9 \n\.]", " ", query)
    #     res = sp.search(query, type="track", market=MARKET_CODE)
    tracks = [SpotifyTrack(song) for song in res["tracks"]["items"]]
    return (res["tracks"]["previous"], res["tracks"]["next"], tracks)


class Playlist:
    def __init__(self) -> None:
        self.playlist = set()

    def update_playlist(self, tr):
        if tr in self.playlist:
            self.playlist.remove(tr)
        else:
            self.playlist.add(tr)


class SpotifyTrack:
    def __init__(self, track) -> None:
        self.track_title = track["name"]
        self.album_name = track["album"]["name"]
        self.album_cover = track["album"]["images"][0]
        self.duration = SpotifyTrack.ms_to_min_sec(track["duration_ms"])
        self.artists = [artist["name"] for artist in track["artists"]]
        self.preview_url = track["preview_url"]

    def ms_to_min_sec(duration):
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    async def load_preview(self):
        pass

    async def load_album_cover(self):
        pass
