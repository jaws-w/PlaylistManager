from cmath import exp
from doctest import master
from logging import root
import tkinter as tk
from tkinter.font import BOLD
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

class AnimeList(ctk.CTkFrame):
    def __init__(self, *args, bg_color=None, fg_color="default_theme", border_color="default_theme", border_width="default_theme", corner_radius="default_theme", width=200, height=200, overwrite_preferred_drawing_method: str = None, **kwargs):
        super().__init__(*args, bg_color=bg_color, fg_color=fg_color, border_color=border_color, border_width=border_width, corner_radius=corner_radius, width=width, height=height, overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs)

        self.query = None
        self.pagenum = 0

        scroll_canvas = ctk.CTkCanvas(master=self)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


        v = tk.Scrollbar(master=self, orient='vertical')
        v.pack(side=tk.RIGHT, fill=tk.Y)
        v.config(command=scroll_canvas.yview)


        scroll_canvas.configure(yscrollcommand=v.set)
        scroll_canvas.bind('<Configure>', lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all')))

        self.innerFrame = ctk.CTkFrame(master=scroll_canvas)
        scroll_canvas.create_window((0,0), window=self.innerFrame, anchor='nw')

    def search(self, query, pagenum):

        if self.query != query or self.pagenum != pagenum:
            for child in self.innerFrame.winfo_children():
                child.destroy()

            self.query = query
            self.pagenum = pagenum
            search_result = jikan.search('anime', query, page=pagenum)

            for anime in search_result['results']:
                animeFrame = AnimeResult(master=self.innerFrame, anime=anime)
                animeFrame.pack()

def searchAnime():
    print('button pressed')
    anime_title = searchBar.get()
    if anime_title != '':

        print(anime_title)

        searchFm.pack(pady=50)

        animesList.search(anime_title, 1)
        animesList.pack(fill=tk.BOTH, expand=True)
        


app = ctk.CTk()
app.geometry('1920x1080')
app.minsize(1200, 500)

searchFm = ctk.CTkFrame(master=app, height=28)
searchFm.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

searchBar = ctk.CTkEntry(master=searchFm, placeholder_text='Enter anime title', width=800)
searchBar.pack(side=tk.LEFT)
animesList = None

searchBtn = ctk.CTkButton(master=searchFm, text='search', command=searchAnime)
searchBtn.pack(padx=20, expand=False, side=tk.RIGHT)

animesList = AnimeList(master=app)

app.mainloop()
