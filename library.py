import requests
from jikanpy import Jikan
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from PIL import Image, ImageTk
from io import BytesIO
import re

jikan = Jikan()

load_dotenv()

MARKET_CODE = 'us'
scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user_id = sp.current_user()['id']

def search_anime(anime_title, page, parameters):
    print(f'Searching for page {page} of {anime_title}')
    return jikan.search('anime', anime_title, page=page, parameters=parameters)

def parse_track(track):
    info = re.split('"|by', track)
    title = info[1]
    artist = info[3].split('\xa0')[0][1:]
    return (title, artist)

def get_songs(anime):
    anime_res = jikan.anime(anime['mal_id'])
    # songs = anime_res['opening_themes'] + anime_res['ending_themes']
    ops = []
    eds = []
    
    for tr in anime_res['opening_themes']:
        ops.append(parse_track(tr))

    for tr in anime_res['ending_themes']:
        eds.append(parse_track(tr))

    return {'openings': ops, 'endings': eds}


async def set_image(anime, target, size=(50,70)):
    imgRes = requests.get(anime['image_url'])
    img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize(size))
    target.configure(image=img)
    target.image = img
    print(f'Image fetched for {anime["title"]}')

class Playlist():

    def __init__(self) -> None:
        self.playlist = set()

    def update_playlist(self, tr):
        if tr in self.playlist:
            self.playlist.remove(tr)
        else:
            self.playlist.add(tr)

