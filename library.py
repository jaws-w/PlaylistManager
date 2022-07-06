import requests
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import sys
import vlc

from PIL import Image, ImageTk
from io import BytesIO
import re

import customtkinter as ctk
import tkinter as tk
import os


MARKET_CODE = "us"
# scope = "playlist-modify-public playlist-modify-private"
scope = "playlist-read-private playlist-modify-public playlist-modify-private"
SPOTIPY_CLIENT_ID = "baffaf7266d04894a474288165840d28"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

spPKCE = SpotifyPKCE(
    client_id=SPOTIPY_CLIENT_ID, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope
)

sp = spotipy.Spotify(auth_manager=spPKCE)
user_id = sp.current_user()["id"]
print(user_id)


def log_out_spotify():
    os.remove(".cache")


class Scrollable:
    def __init__(self, master, root):
        self.master = master
        self.root = root
        self.scroll_canvas = ctk.CTkCanvas(
            master=master, bg="#343638", bd=0, highlightthickness=0
        )
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scroll_canvas.scroll_enabled = False

        self.v = tk.Scrollbar(master=master, orient="vertical")
        self.v.pack(side=tk.RIGHT, fill=tk.Y)
        self.v.config(command=self.scroll_canvas.yview)

        self.scroll_canvas.configure(yscrollcommand=self.v.set)

        self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
        self.w = self.scroll_canvas.create_window(
            (0, 0), window=self.innerFrame, anchor="nw"
        )
        self.innerFrame.bind("<Configure>", self.canvasConfigure)
        self.scroll_canvas.bind("<Configure>", self.frameWidth)

        self.scroll_canvas.bind(
            "<Enter>",
            lambda event: root.on_scrollable_enter(self.scroll_canvas, event),
        )
        self.scroll_canvas.bind("<Leave>", root.on_scrollable_leave)

    def frameWidth(self, event):
        self.scroll_canvas.itemconfig(self.w, width=event.width)

    def canvasConfigure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def toggle_scroll(self):
        self.master.update()
        outer_height = self.master.winfo_height()
        inner_height = self.innerFrame.winfo_height()
        print(outer_height, " ", inner_height)
        if inner_height <= outer_height and self.v.winfo_ismapped():
            print("within limits")
            self.v.pack_forget()
            self.scroll_canvas.scroll_enabled = False
            self.root.on_scrollable_leave()
        elif inner_height > outer_height:
            print("exceeded")
            self.v.pack(side=tk.RIGHT, fill=tk.Y)
            if not self.scroll_canvas.scroll_enabled:

                self.scroll_canvas.scroll_enabled = True
                self.root.on_scrollable_enter(self.scroll_canvas)
            else:
                self.scroll_canvas.scroll_enabled = True


def search_anime(anime_title: str, page: int):
    api_endpoint = "http://staging.jikan.moe/v4/anime"
    query = f"?q={anime_title}&sfw&page={page}"

    resp = requests.get(api_endpoint + query)
    # print(resp.json())
    return resp.json()


def parse_track(track):
    info = re.split('"+|by', track)
    title = info[1]
    artist = info[3].split("(")[0].strip()
    print(f"{title} by {artist}")
    if title == "" or artist == "":
        print(f"parsing {track} failed")
        raise ValueError

    return (title, artist)


def get_songs(anime):
    api_endpoint = f'https://api.jikan.moe/v4/anime/{anime["mal_id"]}/themes'
    resp = requests.get(api_endpoint)
    if resp.status_code != 200:
        return {"openings": [], "endings": []}
    resp_js = resp.json()
    ops = []
    eds = []
    for tr in resp_js["data"]["openings"]:
        try:
            ops.append(parse_track(tr))
        except ValueError:
            pass
    for tr in resp_js["data"]["endings"]:
        try:
            eds.append(parse_track(tr))
        except ValueError:
            pass
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
    res = sp.search(query, type="track", market=MARKET_CODE, limit=25)

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
    )


def get_playlist(id):
    return sp.playlist(id)


def addPlaylist(spotify_playlist, final_playlist):
    print(spotify_playlist["id"])
    items = [track.id for track in final_playlist]
    print(items)
    sp.playlist_add_items(playlist_id=spotify_playlist["id"], items=items)


class Playlist:
    def __init__(self) -> None:
        self.playlist = dict()
        self.results = dict()
        self.playlistPage = None
        self.animePage = None

    def update_playlist(self, tr, update_buttons=True):
        if tr in self.playlist.keys():
            self.playlist[tr][0].destroy()
            self.playlist[tr][1].destroy()
            del self.playlist[tr]
            try:
                del self.results[tr]
            except KeyError:
                print(f"{tr} has not been cached")
        else:
            track_frame = self.playlistPage.playlistFm.add_song_button(tr)
            self.playlist[tr] = track_frame

        self.playlistPage.update()
        if update_buttons:
            self.animePage.update_buttons()


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


class MediaPlayer:
    def __init__(self) -> None:
        self.player = vlc.MediaPlayer()

        self.currentlyPlaying = ""

    def play(self, url):
        # print(self.player.is_playing())
        if url == self.currentlyPlaying and self.player.is_playing():
            self.currentlyPlaying = ""
            self.player.stop()
            return

        self.currentlyPlaying = url
        media = vlc.Media(url)
        self.player.stop()
        self.player.set_media(media)
        self.player.play()

    def stop(self):
        self.currentlyPlaying = ""
        self.player.stop()


async def load_album_cover(searchFrame, track, size):
    target = searchFrame.album_img
    imgRes = requests.get(track.album_cover["url"])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    target.configure(image=img)
    target.image = img
    print(f"Image fetched for {track.track_title}")
    searchFrame.update()


async def setButtonCover(btn, track, size=(70, 70)):
    imgRes = requests.get(track.album_cover["url"])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    btn.configure(image=img, compound=tk.TOP, borderwidth=0)
    btn.image = img
    btn.update()


def load_song_album(cover, track, size):
    imgRes = requests.get(track.album_cover["url"])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    cover.configure(image=img)
    cover.image = img
    print(f"Image fetched for {track.track_title}")
