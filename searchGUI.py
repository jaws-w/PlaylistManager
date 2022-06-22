from doctest import master
from io import BytesIO
import tkinter as tk
from tkinter.ttk import Label, Style

from jmespath import search
import customtkinter as ctk
from AnimeSearchV2 import *

import asyncio

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

        # imgThread = threading.Thread(target=self.getImage())
        # imgThread.start()
        self.imgLabel = ctk.CTkLabel(master=self, width=50, height=70, text='img')
        self.imgLabel.pack(side=tk.LEFT)
        # self.getImage()

        self.titleText = ctk.CTkLabel(master=self, text=self.anime['title'])
        self.titleText.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self.showButton = ctk.CTkButton(master=self, text='>', command=lambda: AnimeResult.getSongs(self))
        self.showButton.pack(side=tk.LEFT, expand=False)

        # imgThread.join()

    async def getImage(self):
        app.update()
        imgRes = requests.get(self.anime['image_url'])
        img = ImageTk.PhotoImage(Image.open(BytesIO(imgRes.content)).resize((50,70)))
        # imgLabel = ctk.CTkLabel(master=self, image=img)
        self.imgLabel.configure(image=img)
        self.imgLabel.image = img
        print('task for {} finished'.format(self.anime['title']))

    def getSongs(self):
        if self.songsShown == False:
            if self.songListFrame is None:
                self.songListFrame = ctk.CTkFrame(master=self)
                
                anime_res = jikan.anime(self.anime['mal_id'])

                songs = anime_res['opening_themes'] + anime_res['ending_themes']

                for tr in songs:
                    song = ctk.CTkButton(master=self.songListFrame, text=tr, command= lambda i = tr: updatePlaylist(i))
                    song.pack(expand=1, fill=tk.X)

                if len(self.songListFrame.winfo_children()) == 0:
                    nullLabel = ctk.CTkLabel(master=self.songListFrame, text='no songs found')
                    nullLabel.pack()

            self.songListFrame.pack(side=tk.LEFT)
            self.songsShown = True
        else:
            self.songListFrame.pack_forget()
            self.songsShown = False

def updatePlaylist(tr):
    if tr in songPlaylist:
        removeTrack(parse_track(tr), songPlaylist)
    else:  
        addTrack(parse_track(tr), songPlaylist)

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
       

    async def search(self, query, pagenum):

        if self.query != query or self.pagenum != pagenum:
            for child in self.innerFrame.winfo_children():
                child.destroy()

            self.query = query
            self.pagenum = pagenum
            search_result = jikan.search('anime', query, page=pagenum, parameters={'rated': ['g', 'pg', 'pg13', 'r17']})

            # imgTasks = []

            for res in search_result['results']:
                animeFrame = AnimeResult(master=self.innerFrame, anime=res)
                animeFrame.pack(side=tk.TOP, fill=tk.X, expand=1)
                print('task for {} created'.format(res['title']))
                asyncio.create_task(animeFrame.getImage())

            buttonHolder = ctk.CTkFrame(master=self.innerFrame)
            prevButton = ctk.CTkButton(master=buttonHolder, text='<')
            nextButton = ctk.CTkButton(master=buttonHolder, text='>')

            prevButton.pack(side=tk.LEFT, fill=tk.X, expand=1)
            nextButton.pack(side=tk.RIGHT, fill=tk.X, expand=1)
            buttonHolder.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

            # await asyncio.gather(*imgTasks)

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry('1920x1080')
        self.minsize(1200, 500)

        masterFrame = tk.Frame(master=self)

        masterFrame.grid_rowconfigure(0,weight=1)
        masterFrame.grid_columnconfigure(0,weight=1)
        masterFrame.pack(side=tk.TOP, fill="both", expand = True)

        self.frames = {}
        for page in (SearchPage, DisplayPage):
            frame = page(masterFrame, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SearchPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.searchFm = ctk.CTkFrame(master=self, height=28)
        self.searchFm.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.searchBar = ctk.CTkEntry(master=self.searchFm, placeholder_text='Enter anime title', width=700)
        self.searchBar.pack(side=tk.LEFT)
        # animesList = None
        self.animesList = AnimeList(master=self)

        self.searchBtn = ctk.CTkButton(master=self.searchFm, text='search', command=self.searchAnime)
        self.searchBtn.pack(padx=20, expand=False, side=tk.RIGHT)

        goToPlaylist = ctk.CTkButton(master=self, text='current playlist >', command=lambda: controller.show_frame(DisplayPage))
        self.goToPlaylist = goToPlaylist
        goToPlaylist.pack(side=tk.RIGHT, anchor=tk.N)
        
        
    
    async def searchAnime(self):
        # if animesList != None:
        #     animesList.updatePlaylist()
        #     #print(songPlaylist)
        #     print('updated')
        print('button pressed')
        anime_title = self.searchBar.get()
        if anime_title != '':

            print(anime_title)

            self.searchFm.pack(pady=50)

            self.animesList.pack(fill=tk.BOTH, expand=True)
            await self.animesList.search(anime_title, 1)

class DisplayPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        songPlaylist = []
        
        self.goBackBtn = ctk.CTkButton(master=self, text='add more songs', command=lambda: controller.show_frame(SearchPage))
        self.goBackBtn.pack(side=tk.LEFT, anchor=tk.N)

        self.style = Style(self)

        self.style.configure("titleFont", font=('Arial', 25))
        title = Label(master=self, text='Your Playlist')
        title.pack(anchor=tk.N)

        currentPlaylist(self, songPlaylist)

def currentPlaylist(obj, songPlaylist):
    for tr in songPlaylist:
        songLabel = ctk.CTk(master=obj, text=tr, pady=20)
        songLabel.pack(side=tk.BOTTOM)


app = tkinterApp()
app.mainloop()