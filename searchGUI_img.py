import tkinter as tk
from tkinter.ttk import Label, Style

import customtkinter as ctk
from customtkinter import ThemeManager

import asyncio

import library

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Class for displaying anime
class AnimeResult(ctk.CTkFrame):

    # init Frame with Jikan anime search response as argument
    def __init__(self, anime, *args, **kwargs):
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

    # onClick function for song buttons
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
        self.result_num = -1

        self.scroll_canvas = ctk.CTkCanvas(master=self, bg='#343638', bd=0, highlightthickness=0)   
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.v = tk.Scrollbar(master=self, orient='vertical')
        self.v.pack(side=tk.RIGHT, fill=tk.Y)
        self.v.config(command=self.scroll_canvas.yview)

        self.scroll_canvas.configure(yscrollcommand=self.v.set)
        self.scroll_canvas.bind('<Configure>', self.frameWidth)

        self.scroll_canvas.bind_all('<MouseWheel>', self.on_vertical)

        self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
        self.w = self.scroll_canvas.create_window((0,0), window=self.innerFrame, anchor='nw')
        self.innerFrame.bind('<Configure>', self.canvasConfigure)

        self.cachedFrames = dict()
        self.loadedPages = 0

    def frameWidth(self, event):
        print(event.width)
        self.scroll_canvas.itemconfig(self.w, width=event.width)

    def canvasConfigure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all'))

    #enable trackpad/mousewheel scrolling
    def on_vertical(self, event):
        self.scroll_canvas.yview_scroll(-1 * event.delta, 'units')
       

    async def search(self, query, pagenum, result_num):
        print('result=', result_num)
        print('page=', pagenum)

        if self.query != query or self.pagenum != pagenum:
            self.search_result = library.search_anime(query, pagenum, parameters={'rated': ['g', 'pg', 'pg13', 'r17']})
            self.result_num = -1
            
        if self.result_num != result_num:
            
            print('new search')
            for child in self.innerFrame.winfo_children():
                child.pack_forget()

            #go to top of results page
            self.scroll_canvas.yview_moveto('0.0')

            self.query = query
            self.pagenum = pagenum
            self.result_num = result_num


            buttonHolder = ctk.CTkFrame(master=self.innerFrame)
            prevButton = ctk.CTkButton(master=buttonHolder, text='<', command= lambda: self.diffPage(query, pagenum, result_num-1))
            nextButton = ctk.CTkButton(master=buttonHolder, text='>', command= lambda: self.diffPage(query, pagenum, result_num+1))
            prevButton.pack(side=tk.LEFT, fill=tk.X, expand=1)
            nextButton.pack(side=tk.RIGHT, fill=tk.X, expand=1)
            if (result_num <= 0):
                prevButton.config(state='disabled', fg_color='gray')
            if (result_num >= self.search_result['last_page'] > 10):
                nextButton.config(state='disabled', fg_color='gray')

            # takes the page number of search page, displays 10 anime from jikan search (5 pages, 50 total)
            try: 
                for i in range(self.result_num * 10, (self.result_num + 1) * 10):
                    res = self.search_result['results'][i % 50]
                    if res['mal_id'] not in self.cachedFrames:
                        animeFrame = AnimeResult(master=self.innerFrame, anime=res)
                        asyncio.create_task(library.set_image(res, animeFrame.imgLabel))

                        self.cachedFrames[res['mal_id']] = animeFrame
                    else:
                        animeFrame = self.cachedFrames[res['mal_id']]

                    animeFrame.pack(side=tk.TOP, fill=tk.X, expand=1)

                    app.update()
            except IndexError:
                nextButton.config(state='disabled', fg_color='gray')
            

            buttonHolder.pack(side=tk.BOTTOM, fill=tk.X, expand=1) 
            app.update()


    def diffPage(self, query, pagenum, result_num):
        if result_num >= 5 * pagenum:
            asyncio.run(self.search(query, pagenum+1, result_num))
        elif result_num < 5 * (pagenum - 1):
            asyncio.run(self.search(query, pagenum-1, result_num))
        else:
            asyncio.run(self.search(query, pagenum, result_num))
            

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
        self.bind_all('<Return>', self.searchAnimeReturn)
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
            asyncio.run(self.animesList.search(anime_title, 1, 0))
            
    #searchAnime when return key is pressed
    def searchAnimeReturn(self, event):
        print('button pressed')
        anime_title = self.searchBar.get()
        if anime_title != '':

            print(anime_title)

            self.searchFm.pack(pady=50)

            self.animesList.pack(fill=tk.BOTH, expand=True)
            asyncio.run(self.animesList.search(anime_title, 1, 0))

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
