import customtkinter as ctk
import tkinter as tk
from customtkinter import ThemeManager

import library


class PlaylistPage(ctk.CTkFrame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.playlistFm = PlaylistPage.PlaylistFrame(master=self, root=root)
        self.playlistFm.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        self.spotifyFm = PlaylistPage.SpotifySearchFrame(master=self, root=root)
        self.spotifyFm.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)

        self.columnconfigure(0, weight=1, uniform="group1")
        self.columnconfigure(1, weight=1, uniform="group1")

        self.goBackBtn = ctk.CTkButton(
            master=self,
            text="< add more songs",
            pady=20,
            command=lambda: root.show_frame("AnimeSearchPage"),
        )
        self.goBackBtn.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)

        self.finalPlaylistBtn = ctk.CTkButton(
            master=self,
            text="add current playlist to your Spotify library",
            pady=20,
            # command=lambda: library.addPlaylist(final_playlist),
            command=lambda: root.show_frame("SpotifyPage"),
        )
        self.finalPlaylistBtn.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=10)

    class PlaylistFrame(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root

            title = ctk.CTkLabel(master=self, pady=20, text="Your Playlist")
            title.pack(side=tk.TOP)

            dummyFrame = ctk.CTkFrame(master=self)
            dummyFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            self.scroll_canvas = ctk.CTkCanvas(
                master=dummyFrame, bg="#343638", bd=0, highlightthickness=0
            )
            self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            self.v = tk.Scrollbar(master=dummyFrame, orient="vertical")
            self.v.pack(side=tk.RIGHT, fill=tk.Y)
            self.v.config(command=self.scroll_canvas.yview)

            self.scroll_canvas.configure(yscrollcommand=self.v.set)
            self.scroll_canvas.bind("<Configure>", self.frameWidth)

            self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

            self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
            self.w = self.scroll_canvas.create_window(
                (0, 0), window=self.innerFrame, anchor="nw"
            )
            self.innerFrame.bind("<Configure>", self.canvasConfigure)

            self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

            self.songButtons = []
            # self.removeButtons = []

        def load_current_playlist(self):
            for btn in self.songButtons:
                btn.destroy()
            # for btn in self.removeButtons:
            #    btn.destroy()

            self.songButtons = []
            # self.removeButtons = []

            for tr in self.root.playlist.playlist.copy():
                playlistFrame = ctk.CTkFrame(master=self.innerFrame)
                playlistFrame.pack(side=tk.TOP, fill=tk.X, expand=1)
                songBtn = ctk.CTkButton(
                    master=playlistFrame, text=tr, fg_color="gray", width=60
                )
                songBtn.track = tr
                songBtn.configure(command=lambda i=songBtn: self.songBtnOnClick(i))
                songBtn.pack(side=tk.LEFT)
                removeBtn = ctk.CTkButton(
                    master=playlistFrame,
                    text="X",
                    width=20,
                    command=lambda t=tr, i=playlistFrame, j=songBtn: self.removeSong(
                        t, i, j
                    ),
                )
                removeBtn.pack(side=tk.RIGHT)
                self.songButtons.append(songBtn)
                # self.removeButtons.append(removeBtn)

            if self.songButtons:
                self.songBtnOnClick(self.songButtons[0])

        def songBtnOnClick(self, btn):
            print(btn.track)
            for button in self.songButtons:
                if button is btn:
                    button.configure(fg_color=ThemeManager.theme["color"]["button"])
                else:
                    button.configure(fg_color="gray")
            self.activeBtn = btn
            self.master.spotifyFm.search_spotify(btn.track)

        def removeSong(self, tr, playlistFrame, songBtn):
            self.master.playlist.update_playlist(tr)
            playlistFrame.destroy()
            self.songButtons.remove(songBtn)
            if self.songButtons:
                if songBtn == self.activeBtn:
                    self.songBtnOnClick(self.songButtons[0])
            else:
                self.master.spotifyFm.clearSearch()
                # means playlist is now empty
                # might need to put label here to say to add more songs

        def on_vertical(self, event):
            self.scroll_canvas.yview_scroll(-1 * event.delta, "units")

        def frameWidth(self, event):
            # print(event.width)
            self.scroll_canvas.itemconfig(self.w, width=event.width)

        def canvasConfigure(self, event):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

        # def createCanvas(self):
        #     self.scroll_canvas = ctk.CTkCanvas(master=self, bg="#343638", bd=0, highlightthickness=0)
        #     self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #     self.v = tk.Scrollbar(master=self, orient="vertical")
        #     self.v.pack(side=tk.RIGHT, fill=tk.Y)
        #     self.v.config(command=self.scroll_canvas.yview)

        #     self.scroll_canvas.configure(yscrollcommand=self.v.set)
        #     self.scroll_canvas.bind("<Configure>", self.frameWidth)

        #     self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

        #     self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
        #     self.w = self.scroll_canvas.create_window((0, 0), window=self.innerFrame, anchor="nw")
        #     self.innerFrame.bind("<Configure>", self.canvasConfigure)

        #     self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

    class SpotifySearchFrame(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root

            self.label = ctk.CTkLabel(master=self, text="Add tracks to search!")
            self.label.pack(side=tk.TOP, fill=tk.X, expand=1)

            self.scroll_canvas = ctk.CTkCanvas(
                master=self, bg="#343638", bd=0, highlightthickness=0
            )
            self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            self.v = tk.Scrollbar(master=self, orient="vertical")
            self.v.pack(side=tk.RIGHT, fill=tk.Y)
            self.v.config(command=self.scroll_canvas.yview)

            self.scroll_canvas.configure(yscrollcommand=self.v.set)
            self.scroll_canvas.bind("<Configure>", self.frameWidth)

            self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

            self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
            self.w = self.scroll_canvas.create_window(
                (0, 0), window=self.innerFrame, anchor="nw"
            )
            self.innerFrame.bind("<Configure>", self.canvasConfigure)

            self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

        def search_spotify(self, track):
            for child in self.innerFrame.winfo_children():

                child.destroy()

            self.label.configure(
                text="Searching for {} by {} on Spotify".format(track[0], track[1])
            )

            # label = ctk.CTkLabel(
            #     master=self,
            #     text="Searching for {} by {} on Spotify".format(track[0], track[1]),
            # )
            # label.grid(row=0, column=0, columnspan=4, sticky=tk.EW)

            response = library.search_spotify(track[0], track[1])
            self.previous, self.next, self.tracks = response

            for i, track in enumerate(self.tracks):
                print(track.track_title, track.preview_url)

                playBtn = ctk.CTkButton(master=self.innerFrame, text="play", width=60)
                playBtn.configure(command=lambda tr=track: library.playPreview(tr))
                playBtn.grid(row=i, column=0)

                addtoPlaylist = ctk.CTkButton(
                    master=self.innerFrame, text="add", width=60
                )
                addtoPlaylist.configure(
                    command=lambda tr=track: self.root.final_playlist.append(tr)
                )
                addtoPlaylist.grid(row=i, column=1)

                titleLabel = ctk.CTkLabel(
                    master=self.innerFrame,
                    text=track.track_title,
                    anchor=tk.W,
                    wraplength=100,
                    justify="center",
                    pady=10,
                )
                # if len(track.track_title) > 30:
                #    titleLabel.configure(text=track.track_title[0:30])
                # wraplength=100, justify="center"

                artistsText = track.artists[0]
                for artist in track.artists[1:]:
                    artistsText += ", " + artist
                artistLabel = ctk.CTkLabel(
                    master=self.innerFrame,
                    text=artistsText,
                    anchor=tk.W,
                    wraplength=100,
                    justify="center",
                    pady=10,
                )
                # if len(artistsText) > 30:
                #    artistLabel.configure(text=artistsText[0:30])
                titleLabel.grid(row=i, column=2, sticky=tk.NSEW)
                artistLabel.grid(row=i, column=3, sticky=tk.NSEW)
                durationLabel = ctk.CTkLabel(
                    master=self.innerFrame,
                    text=track.duration,
                )
                durationLabel.grid(row=i, column=4, sticky=tk.NSEW)

        def clearSearch(self):
            for child in self.winfo_children():
                child.destroy()

        def on_vertical(self, event):
            self.scroll_canvas.yview_scroll(-1 * event.delta, "units")

        def frameWidth(self, event):
            print(event.width)
            self.scroll_canvas.itemconfig(self.w, width=event.width)

        def canvasConfigure(self, event):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

        # def createCanvas(self):
        #     self.scroll_canvas = ctk.CTkCanvas(
        #         master=self, bg="#343638", bd=0, highlightthickness=0
        #     )
        #     self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #     self.v = tk.Scrollbar(master=self, orient="vertical")
        #     self.v.pack(side=tk.RIGHT, fill=tk.Y)
        #     self.v.config(command=self.scroll_canvas.yview)

        #     self.scroll_canvas.configure(yscrollcommand=self.v.set)
        #     self.scroll_canvas.bind("<Configure>", self.frameWidth)

        #     self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)

        #     self.innerFrame = ctk.CTkFrame(master=self.scroll_canvas)
        #     self.w = self.scroll_canvas.create_window(
        #         (0, 0), window=self.innerFrame, anchor="nw"
        #     )
        #     self.innerFrame.bind("<Configure>", self.canvasConfigure)

        #     self.scroll_canvas.bind_all("<MouseWheel>", self.on_vertical)
