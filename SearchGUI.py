from doctest import master
import tkinter as tk
import customtkinter as ctk

import re
from jikanpy import Jikan
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


SHOW_SEARCH_RESULTS = 10
jikan = Jikan()

# load_dotenv()

# MARKET_CODE = 'us'
# scope = "playlist-modify-private"
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
# user_id = sp.current_user()['id']

import AnimeSearch

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class AnimeResult(ctk.CTkFrame):
    def __init__(self, anime, *args, bg_color=None, fg_color="default_theme", border_color="default_theme", border_width="default_theme", corner_radius="default_theme", width=200, height=200, overwrite_preferred_drawing_method: str = None, **kwargs):
        super().__init__(*args, bg_color=bg_color, fg_color=fg_color, border_color=border_color, border_width=border_width, corner_radius=corner_radius, width=width, height=height, overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs)

        self.anime = anime
        titleText = ctk.CTkLabel(master=self, text=anime['title'])
        titleText.pack()


def searchAnime():
    print('button pressed')
    anime_title = searchBar.get()
    if anime_title != '':
        print(anime_title)

        page_num = 1

        searchFm.pack(pady=50)

        animesList = ctk.CTkFrame(master=app, bg_color='red')
        animesList.pack(fill=tk.BOTH, expand=True)

        
        if anime_title != anime_title_old:
            for child in animesList.winfo_children():
                child.destroy()
        anime_title_old = anime_title

        search_result = jikan.search('anime', anime_title, page=page_num)

        for anime in search_result['results']:
            animeFrame = AnimeResult(master=animesList, anime=anime)
            animeFrame.pack()
        


app = ctk.CTk()
app.geometry('1920x1080')
app.minsize(1200, 500)

searchFm = ctk.CTkFrame(master=app, height=28)
searchFm.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

searchBar = ctk.CTkEntry(master=searchFm, placeholder_text='Enter anime title', width=800)
searchBar.pack(side=tk.LEFT)

searchBtn = ctk.CTkButton(master=searchFm, text='search', command=searchAnime)
searchBtn.pack(padx=20, expand=False, side=tk.RIGHT)


app.mainloop()
