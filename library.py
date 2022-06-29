import requests
from jikanpy import Jikan
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyPKCE

from PIL import Image, ImageTk
from io import BytesIO
import re

import customtkinter as ctk
import tkinter as tk

import os

# jikan = Jikan()

load_dotenv()

MARKET_CODE = "us"
scope = "playlist-read-private playlist-modify-public playlist-modify-private"
SPOTIPY_CLIENT_ID = "baffaf7266d04894a474288165840d28"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

spPKCE = SpotifyPKCE(
    client_id=SPOTIPY_CLIENT_ID, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope
)

sp = spotipy.Spotify(auth_manager=spPKCE)
user_id = sp.current_user()["id"]
print(sp.current_user())


def log_out_spotify():
    os.remove(".cache")


def create_scroll_canvas(master):
    scroll_canvas = ctk.CTkCanvas(
        master=master, bg="#343638", bd=0, highlightthickness=0
    )
    scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    v = tk.Scrollbar(master=master, orient="vertical")
    v.pack(side=tk.RIGHT, fill=tk.Y)
    v.config(command=scroll_canvas.yview)

    scroll_canvas.configure(yscrollcommand=v.set)

    scroll_canvas.bind_all(
        "<MouseWheel>", lambda event: on_vertical(scroll_canvas, event)
    )

    innerFrame = ctk.CTkFrame(master=scroll_canvas)
    w = scroll_canvas.create_window((0, 0), window=innerFrame, anchor="nw")
    innerFrame.bind("<Configure>", lambda event: canvasConfigure(scroll_canvas, event))
    scroll_canvas.bind("<Configure>", lambda event: frameWidth(scroll_canvas, w, event))

    scroll_canvas.bind_all(
        "<MouseWheel>", lambda event: on_vertical(scroll_canvas, event)
    )

    return scroll_canvas, innerFrame


def frameWidth(scroll_canvas, w, event):
    scroll_canvas.itemconfig(w, width=event.width)


def canvasConfigure(scroll_canvas, event):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))


# enable trackpad/mousewheel scrolling
def on_vertical(scroll_canvas, event):
    scroll_canvas.yview_scroll(-1 * event.delta, "units")


# def search_anime(anime_title, page, parameters):
#     print(f"Searching for page {page} of {anime_title}")
#     return jikan.search("anime", anime_title, page=page, parameters=parameters)


def search_anime(anime_title: str, page: int):
    api_endpoint = "http://staging.jikan.moe/v4/anime"
    query = f"?q={anime_title}&sfw&page={page}"

    resp = requests.get(api_endpoint + query)
    # print(resp.json())
    return resp.json()


def parse_track(track):
    info = re.split('"+|by', track)
    title = info[1]
    artist = info[3].split("\xa0")[0][1:]
    return (title, artist)


# def get_songs(anime):
#     anime_res = jikan.anime(anime["mal_id"])
#     ops = []
#     eds = []

#     for tr in anime_res["opening_themes"]:
#         ops.append(parse_track(tr))

#     for tr in anime_res["ending_themes"]:
#         eds.append(parse_track(tr))

#     return {"openings": ops, "endings": eds}


def get_songs(anime):
    api_endpoint = f'https://api.jikan.moe/v4/anime/{anime["mal_id"]}/themes'
    resp = requests.get(api_endpoint)
    if resp.status_code != 200:
        return {"openings": [], "endings": []}
    resp_js = resp.json()
    ops = []
    eds = []
    for tr in resp_js["data"]["openings"]:
        ops.append(parse_track(tr))
    for tr in resp_js["data"]["endings"]:
        eds.append(parse_track(tr))
    return {"openings": ops, "endings": eds}


async def set_image(anime, target, size=(50, 70)):
    imgRes = requests.get(anime["images"]["jpg"]["image_url"])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    target.configure(image=img)
    target.image = img
    print(f'Image fetched for {anime["title"]}')
    target.update()


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


def get_user_playlists():
    return sp.current_user_playlists()


def new_playlist(title):
    return sp.user_playlist_create(
        user_id,
        name=title,
        public=False,
        collaborative=False,
        # description="hi",
    )


def get_playlist(id):
    return sp.playlist(id)


def addPlaylist(spotify_playlist, final_playlist):
    # spotify_playlist = sp.user_playlist_create(
    #     user_id,
    #     name="testing playlist",
    #     public=False,
    #     collaborative=False,
    #     description="hi",
    # )
    print(spotify_playlist["id"])
    items = [track.id for track in final_playlist]
    print(items)
    sp.playlist_add_items(playlist_id=spotify_playlist["id"], items=items)


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
        self.id = track["id"]

    def ms_to_min_sec(duration):
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    async def load_preview(self):
        pass

    async def load_album_cover(self):
        pass
