from cProfile import label
from doctest import master
from io import BytesIO
import tkinter as tk
from tkinter.font import BOLD
from turtle import update
import customtkinter as ctk
from AnimeSearchV2 import *


from PIL import ImageTk, Image

import re
from jikanpy import Jikan
from dotenv import load_dotenv
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth


SHOW_SEARCH_RESULTS = 10
jikan = Jikan()

# load_dotenv()

# MARKET_CODE = 'us'
# scope = "playlist-modify-private"
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
# user_id = sp.current_user()['id']

#import AnimeSearch

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class AnimeResult(ctk.CTkFrame):

    def __init__(self, anime, *args, bg_color=None, fg_color="default_theme", border_color="default_theme", border_width="default_theme", corner_radius="default_theme", width=200, height=200, overwrite_preferred_drawing_method: str = None, **kwargs):
        super().__init__(*args, bg_color=bg_color, fg_color=fg_color, border_color=border_color, border_width=border_width, corner_radius=corner_radius, width=width, height=height, overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs)

        self.anime = anime
        self.songsShown = False
        self.songListFrame = None


        imgRes = requests.get(anime['image_url'])
        img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)))
        imgLabel = ctk.CTkLabel(master=self, image=img)
        imgLabel.image = img
        imgLabel.pack(side=tk.LEFT)

        self.titleText = ctk.CTkLabel(master=self, text=self.anime['title'])
        self.titleText.pack(side=tk.LEFT)

        self.showButton = ctk.CTkButton(master=self, text='>', command=lambda: AnimeResult.getSongs(self))
        self.showButton.pack(side=tk.LEFT, expand=False)

    def getSongs(self):
        if self.songsShown == False:
            if self.songListFrame is None:
                self.songListFrame = ctk.CTkFrame(master=self)
                
                anime_res = jikan.anime(self.anime['mal_id'])

                songs = anime_res['opening_themes'] + anime_res['ending_themes']

                for tr in songs:
                    song = ctk.CTkCheckBox(master=self.songListFrame, text=tr)
                    song.pack(expand=1, fill=tk.X)

                if len(self.songListFrame.winfo_children()) == 0:
                    nullLabel = ctk.CTkLabel(master=self.songListFrame, text='no songs found')
                    nullLabel.pack()

            self.songListFrame.pack(side=tk.LEFT)
            self.songsShown = True
        else:
            self.songListFrame.pack_forget()
            self.songsShown = False


    def check(self):
        for checkbox in self.songListFrame.winfo_children():
            if checkbox.get() == 1:
                addTrack(checkbox.text, songPlaylist)


def addTrack(track, songPlaylist):
    print('adding track')
    getIndividualTrack(parse_track(track), songPlaylist)


class AnimeList(ctk.CTkFrame):
    def __init__(self, *args, bg_color=None, fg_color="default_theme", border_color="default_theme", border_width="default_theme", corner_radius="default_theme", width=200, height=200, overwrite_preferred_drawing_method: str = None, **kwargs):
        super().__init__(*args, bg_color=bg_color, fg_color=fg_color, border_color=border_color, border_width=border_width, corner_radius=corner_radius, width=width, height=height, overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs)

        self.query = None
        self.pagenum = 0

        self.scroll_canvas = ctk.CTkCanvas(master=self)

        
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        v = tk.Scrollbar(master=self, orient='vertical')
        v.pack(side=tk.RIGHT, fill=tk.Y)
        v.config(command=self.scroll_canvas.yview)


        self.scroll_canvas.configure(yscrollcommand=v.set)
        self.scroll_canvas.bind('<Configure>', self.frameWidth)

        self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
        self.w = self.scroll_canvas.create_window((0,0), window=self.innerFrame, anchor='nw')
        self.innerFrame.bind('<Configure>', self.canvasConfigure)        

        


    def frameWidth(self, event):
        print(event.width)
        self.scroll_canvas.itemconfig(self.w, width=event.width)

    def canvasConfigure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all'))
       

    def search(self, query, pagenum):

        if self.query != query or self.pagenum != pagenum:
            for child in self.innerFrame.winfo_children():
                child.destroy()

            self.query = query
            self.pagenum = pagenum
            search_result = jikan.search('anime', query, page=5, parameters={'rated': ['g', 'pg', 'pg13', 'r17']})

            for res in search_result['results'][:5]:
                animeFrame = AnimeResult(master=self.innerFrame, anime=res)
                animeFrame.pack(side=tk.TOP, fill=tk.X, expand=1)

            buttonHolder = ctk.CTkFrame(master=self.innerFrame)
            prevButton = ctk.CTkButton(master=buttonHolder, text='<')
            nextButton = ctk.CTkButton(master=buttonHolder, text='>')

            prevButton.pack(side=tk.LEFT, fill=tk.X, expand=1)
            nextButton.pack(side=tk.RIGHT, fill=tk.X, expand=1)
            buttonHolder.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

    # def updatePlaylist(self):
    #     if self.innerFrame.winfo_exists():
    #         for animeFrame in self.innerFrame.winfo_children():
    #             animeFrame.check()

def searchAnime():
    # if animesList != None:
    #     animesList.updatePlaylist()
    #     #print(songPlaylist)
    #     print('updated')
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
# animesList = None

searchBtn = ctk.CTkButton(master=searchFm, text='search', command=searchAnime)
searchBtn.pack(padx=20, expand=False, side=tk.RIGHT)

# compileBtn = ctk.CTkButton(master=searchFm, text='make playlist', command=createSpotifyPlaylist)

songPlaylist = []

animesList = AnimeList(master=app)

app.mainloop()