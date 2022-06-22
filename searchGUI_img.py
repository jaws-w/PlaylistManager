import tkinter as tk
from tkinter.ttk import Label, Style

import customtkinter as ctk
from customtkinter import ThemeManager

import asyncio

import library

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green



class AnimeResult(ctk.CTkFrame):
    def __init__(self, 
        anime, 
        *args, 
        **kwargs):
        super().__init__(*args, **kwargs)

        self.anime = anime
        self.songsShown = False
        self.songListFrame = None
        self.songButtons = []

        dummyFrame = ctk.CTkFrame(master=self)
        dummyFrame.pack(side=tk.TOP, fill=tk.X)

        self.imgLabel = ctk.CTkLabel(master=dummyFrame, width=50, height=70, text='img')
        self.imgLabel.pack(side=tk.LEFT)

        self.titleText = ctk.CTkLabel(master=dummyFrame, text=self.anime['title'])
        self.titleText.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self.showButton = ctk.CTkButton(master=dummyFrame, text='Show songs', command=lambda: AnimeResult.show_songs(self))
        self.showButton.pack(side=tk.LEFT, expand=False)

        # asyncio.run(library.set_image(self.anime, self.imgLabel))
        # app.update()

    def select_song(self, tr):
        playlist.update_playlist(tr)
        self.update_buttons()
        
    def show_songs(self):
        if self.songsShown == False:
            if self.songListFrame is None:
                self.songListFrame = ctk.CTkFrame(master=self, border_color='red')

                songs = library.get_songs(self.anime)

                opsLabel = ctk.CTkLabel(master=self.songListFrame, text='Openings:')
                opsLabel.grid(row=0, column=0, sticky=tk.EW)
                if len(songs['openings']) == 0:
                    nullLabel = ctk.CTkLabel(master=self.songListFrame, text='no songs found')
                    nullLabel.grid(row=1, column=0, sticky=tk.EW)
                else:
                    for r, tr in enumerate(songs['openings']):
                        song = ctk.CTkButton(master=self.songListFrame, 
                            text='{} by {}'.format(tr[0], tr[1]), 
                            fg_color='gray',
                            command=lambda i=tr: self.select_song(i)
                        )
                        song.tr = tr
                        song.grid(row=r+1, column=0, sticky=tk.EW)
                        self.songButtons.append(song)

                edsLabel = ctk.CTkLabel(master=self.songListFrame, text='Endings:')
                edsLabel.grid(row=0, column=1, sticky=tk.EW)
                if len(songs['endings']) == 0:
                    nullLabel = ctk.CTkLabel(master=self.songListFrame, text='no songs found')
                    nullLabel.grid(row=1, column=1, sticky=tk.EW)
                else:
                    for r, tr in enumerate(songs['endings']):
                        song = ctk.CTkButton(master=self.songListFrame, 
                            text='{} by {}'.format(tr[0], tr[1]), 
                            fg_color='gray',
                            command=lambda i=tr: self.select_song(i)
                        )
                        song.tr = tr
                        song.grid(row=r+1, column=1, sticky=tk.EW)
                        self.songButtons.append(song)

                self.songListFrame.columnconfigure(0, weight=1, uniform='group1')
                self.songListFrame.columnconfigure(1, weight=1, uniform='group1')
                
            self.showButton.configure(text='Hide songs')
            self.songListFrame.pack(side=tk.TOP, fill=tk.X)
        else:
            self.showButton.configure(text='Show songs')
            self.songListFrame.pack_forget()

        self.songsShown = not self.songsShown

    def update_buttons(self):
        for button in self.songButtons:
            if button.tr in playlist.playlist:
                button.configure(fg_color=ThemeManager.theme["color"]["button"])
            else:
                button.configure(fg_color='gray')


class AnimeList(ctk.CTkFrame):
    def __init__(self,  
        *args, 
        **kwargs):
        super().__init__(*args, **kwargs)

        self.query = None
        self.pagenum = 0

        self.scroll_canvas = ctk.CTkCanvas(master=self, bg='#343638', bd=0, highlightthickness=0)

        
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
            search_result = library.search_anime(query, pagenum, parameters={'rated': ['g', 'pg', 'pg13', 'r17']})

            # LIMIT TO 5 FOR TESTINGS
            for res in search_result['results']:
                animeFrame = AnimeResult(master=self.innerFrame, anime=res)
                animeFrame.pack(side=tk.TOP, fill=tk.X, expand=1)

                asyncio.create_task(library.set_image(res, animeFrame.imgLabel))
                app.update()
                

            buttonHolder = ctk.CTkFrame(master=self.innerFrame)
            prevButton = ctk.CTkButton(master=buttonHolder, text='<')
            nextButton = ctk.CTkButton(master=buttonHolder, text='>')

            prevButton.pack(side=tk.LEFT, fill=tk.X, expand=1)
            nextButton.pack(side=tk.RIGHT, fill=tk.X, expand=1)
            buttonHolder.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
            

class tkinterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry('1920x1080')
        self.minsize(1200, 500)

        masterFrame = ctk.CTkFrame(master=self)

        masterFrame.grid_rowconfigure(0,weight=1)
        masterFrame.grid_columnconfigure(0,weight=1)
        masterFrame.pack(side=tk.TOP, fill="both", expand = True)

        self.frames = {}
        for page in (SearchPage, DisplayPage):
            frame = page(master=masterFrame, controller=self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SearchPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class SearchPage(ctk.CTkFrame):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.searchFm = ctk.CTkFrame(master=self, height=28)
        self.searchFm.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.searchBar = ctk.CTkEntry(master=self.searchFm, placeholder_text='Enter anime title', width=700)
        self.searchBar.pack(side=tk.LEFT)
        self.animesList = AnimeList(master=self)

        self.searchBtn = ctk.CTkButton(master=self.searchFm, text='search', command=self.searchAnime)
        self.searchBtn.pack(padx=20, expand=False, side=tk.LEFT)

        self.goToPlaylist = ctk.CTkButton(master=self.searchFm, text='current playlist >', command=lambda: controller.show_frame(DisplayPage))
        self.goToPlaylist.pack(padx=20, side=tk.LEFT)
        
    
    def searchAnime(self):
        print('button pressed')
        anime_title = self.searchBar.get()
        if anime_title != '':

            print(anime_title)

            self.searchFm.pack(pady=50)

            self.animesList.pack(fill=tk.BOTH, expand=True)
            asyncio.run(self.animesList.search(anime_title, 1))

class DisplayPage(ctk.CTkFrame):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.goBackBtn = ctk.CTkButton(master=self, text='add more songs', command=lambda: controller.show_frame(SearchPage))
        self.goBackBtn.pack(side=tk.LEFT, anchor=tk.N)

        self.style = Style(self)

        self.style.configure("titleFont", font=('Arial', 25))
        title = Label(master=self, text='Your Playlist')
        title.pack(anchor=tk.N)

        # currentPlaylist(self, songPlaylist)

def currentPlaylist(obj, songPlaylist):
    for tr in songPlaylist:
        songLabel = ctk.CTk(master=obj, text=tr, pady=20)
        songLabel.pack(side=tk.BOTTOM)


app = tkinterApp()
playlist = library.Playlist()
app.mainloop()