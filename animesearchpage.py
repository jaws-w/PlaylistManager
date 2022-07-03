import customtkinter as ctk
import tkinter as tk
from customtkinter import ThemeManager

import library
import searchGUI_img

# This page is responsible for search for anime by title and
# displaying the list of opening/ending themes
class AnimeSearchPage(ctk.CTkFrame):
    def __init__(self, root: searchGUI_img.tkinterApp, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # holder frame for search bar and buttons
        self.searchFm = ctk.CTkFrame(master=self, height=28)
        self.searchFm.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.searchBar = ctk.CTkEntry(
            master=self.searchFm, placeholder_text="Enter anime title", width=700
        )
        self.searchBtn = ctk.CTkButton(
            master=self.searchFm, text="search", command=self.searchAnime
        )
        self.goToPlaylist = ctk.CTkButton(
            master=self.searchFm,
            text="current playlist >",
            command=lambda: root.show_frame("PlaylistPage"),
        )

        self.searchBar.pack(side=tk.LEFT, pady=5, padx=(5, 0))
        self.searchBtn.pack(padx=(20, 0), side=tk.LEFT)
        self.goToPlaylist.pack(padx=(20, 5), side=tk.LEFT)

        # bind enter key to search button
        self.bind_all("<Return>", self.searchAnime)

        # holder for anime results
        self.animesList = AnimeList(master=self, root=root)

    # takes searchbar content and queries Jikan api
    def searchAnime(self, event=None) -> None:
        print("search button pressed")
        anime_title = self.searchBar.get().strip()
        if anime_title != "":
            print(f"Searching for: {anime_title}")

            self.searchFm.pack(pady=50)

            self.animesList.pack(fill=tk.BOTH, expand=True)
            self.animesList.search(anime_title, 1)

    # update the song buttons of the active frame
    def update_buttons(self):
        print("update buttons")
        for animeresultFm in self.animesList.innerFrame.winfo_children():
            if isinstance(animeresultFm, AnimeResult):
                if animeresultFm.songsShown:
                    animeresultFm.update_buttons()


# holder frame for animeresults
class AnimeList(ctk.CTkFrame):
    def __init__(self, root: searchGUI_img.tkinterApp, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root

        # store current search query
        self.query = ""
        self.page_num = 0

        # create scrollable frame
        self.scroll_canvas, self.innerFrame = library.create_scroll_canvas(master=self)

        # caches animeresult frames using mal_id as key
        self.cachedFrames = dict()

    # gets corresponding page of search results for query from Jikan
    def search(self, query: str, page_num: int):

        if self.query != query or self.page_num != page_num:
            print(f"page={page_num}")
            self.search_result = library.search_anime(query, page_num)

            # clear previous search results
            for child in self.innerFrame.winfo_children():
                child.pack_forget()

            # go to top of results page
            self.scroll_canvas.yview_moveto("0.0")

            # store current search query
            self.query = query
            self.page_num = page_num

            # holder for the prev/next page buttons
            buttonHolder = ctk.CTkFrame(master=self.innerFrame)
            prevButton = ctk.CTkButton(
                master=buttonHolder,
                text="<",
                command=lambda: self.search(query, self.page_num - 1),
            )
            nextButton = ctk.CTkButton(
                master=buttonHolder,
                text=">",
                command=lambda: self.search(query, self.page_num + 1),
            )
            prevButton.pack(side=tk.LEFT, fill=tk.X, expand=1)
            nextButton.pack(side=tk.RIGHT, fill=tk.X, expand=1)

            # disable the prev page button on the first page
            if page_num <= 1:
                prevButton.config(state="disabled", fg_color="gray")

            # note pagination currently not working
            # if not self.search_result["pagination"]["has_next_page"]:
            if self.search_result["pagination"]["items"]["count"] < 25:
                nextButton.config(state="disabled", fg_color="gray")
            buttonHolder.pack(side=tk.BOTTOM, fill=tk.X, expand=1, ipady=10)

            for res in self.search_result["data"]:
                # create corresponding animeResult frame and caches it
                if res["mal_id"] not in self.cachedFrames:
                    animeFrame = AnimeResult(
                        master=self.innerFrame, anime=res, root=self.root
                    )
                    self.root.loop.create_task(
                        library.set_image(res, animeFrame.imgLabel)
                    )
                    self.cachedFrames[res["mal_id"]] = animeFrame
                # fetch corresponding animeResult frame from cache
                else:
                    animeFrame = self.cachedFrames[res["mal_id"]]

                animeFrame.pack(side=tk.TOP, fill=tk.X, expand=1)

                self.root.update()


# Class for displaying anime results
class AnimeResult(ctk.CTkFrame):

    # init Frame with Jikan anime search response as argument
    def __init__(self, anime: dict, root: searchGUI_img.tkinterApp, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.anime = anime
        self.songsShown = False
        self.songListFrame = None
        self.songButtons = []
        self.root = root

        # holder for image, title, show songs button
        dummyFrame = ctk.CTkFrame(master=self)
        dummyFrame.pack(side=tk.TOP, fill=tk.X)

        self.imgLabel = ctk.CTkLabel(master=dummyFrame, width=50, height=70, text="img")
        self.titleText = ctk.CTkLabel(master=dummyFrame, text=self.anime["title"])
        self.showButton = ctk.CTkButton(
            master=dummyFrame,
            text="Show songs",
            command=lambda: AnimeResult.show_songs(self),
        )

        self.imgLabel.pack(side=tk.LEFT)
        self.titleText.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.showButton.pack(side=tk.LEFT, expand=False)

    # toggles list of songs
    def show_songs(self):
        # check if songs are already shown
        if not self.songsShown:
            # check if songListFrame is already created
            if not self.songListFrame:
                # create songListFrame
                self.songListFrame = ctk.CTkFrame(master=self, border_color="red")

                songs = library.get_songs(self.anime)

                # list of openings
                opsLabel = ctk.CTkLabel(master=self.songListFrame, text="Openings:")
                opsLabel.grid(row=0, column=0, sticky=tk.EW)
                if len(songs["openings"]) == 0:
                    nullLabel = ctk.CTkLabel(
                        master=self.songListFrame, text="no songs found"
                    )
                    nullLabel.grid(row=1, column=0, sticky=tk.EW)
                else:
                    for r, tr in enumerate(songs["openings"]):
                        songBtn = ctk.CTkButton(
                            master=self.songListFrame,
                            text=f"{tr[0]} by {tr[1]}",
                            fg_color="gray",
                            command=lambda i=tr: self.select_song(i),
                        )
                        songBtn.tr = tr
                        songBtn.grid(row=r + 1, column=0, sticky=tk.EW)
                        self.songButtons.append(songBtn)

                # list of endings
                edsLabel = ctk.CTkLabel(master=self.songListFrame, text="Endings:")
                edsLabel.grid(row=0, column=1, sticky=tk.EW)
                if len(songs["endings"]) == 0:
                    nullLabel = ctk.CTkLabel(
                        master=self.songListFrame, text="no songs found"
                    )
                    nullLabel.grid(row=1, column=1, sticky=tk.EW)
                else:
                    for r, tr in enumerate(songs["endings"]):
                        songBtn = ctk.CTkButton(
                            master=self.songListFrame,
                            text="{} by {}".format(tr[0], tr[1]),
                            fg_color="gray",
                            command=lambda i=tr: self.select_song(i),
                        )
                        songBtn.tr = tr
                        songBtn.grid(row=r + 1, column=1, sticky=tk.EW)
                        self.songButtons.append(songBtn)

                # make the two columns equal width
                self.songListFrame.columnconfigure(0, weight=1, uniform="group1")
                self.songListFrame.columnconfigure(1, weight=1, uniform="group1")

            # update button text
            self.showButton.configure(text="Hide songs")
            self.songListFrame.pack(side=tk.TOP, fill=tk.X)
            self.update_buttons()

            # hide all other song lists
            for sibling in self.master.winfo_children():
                if isinstance(sibling, AnimeResult):
                    if sibling is not self and sibling.songsShown:
                        sibling.show_songs()
        # hide song list
        else:
            self.showButton.configure(text="Show songs")
            self.songListFrame.pack_forget()

        self.songsShown = not self.songsShown

    # onClick function for song buttons
    def select_song(self, tr: tuple[str, str]):
        self.root.playlist.update_playlist(tr, False)
        self.update_buttons()

    # update the coloring of the buttons
    # blue for selected
    # gray for non-selected
    def update_buttons(self):
        for button in self.songButtons:
            if button.tr in self.root.playlist.playlist:
                button.configure(fg_color=ThemeManager.theme["color"]["button"])
            else:
                button.configure(fg_color="gray")
