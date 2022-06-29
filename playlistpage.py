from doctest import master
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
        self.rowconfigure(0, weight=1)

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

            title = ctk.CTkLabel(master=self, pady=20, text="Selected tracks")
            title.pack(side=tk.TOP)

            dummyFrame = ctk.CTkFrame(master=self)
            dummyFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            self.scroll_canvas, self.innerFrame = library.create_scroll_canvas(
                master=dummyFrame
            )

        def add_song_button(self, track):

            buttonHolderFrame = ctk.CTkFrame(master=self.innerFrame)
            songBtn = ctk.CTkButton(
                master=buttonHolderFrame, text=track, fg_color="gray", width=60
            )
            songBtn.track = track
            songBtn.configure(command=lambda i=songBtn: self.songBtnOnClick(i))
            songBtn.pack(side=tk.LEFT)
            buttonHolderFrame.songBtn = songBtn
            removeBtn = ctk.CTkButton(
                master=buttonHolderFrame,
                text="X",
                width=20,
                command=lambda t=track: self.root.playlist.update_playlist(t),
            )
            removeBtn.pack(side=tk.RIGHT)
            buttonHolderFrame.pack()

            return buttonHolderFrame

        def songBtnOnClick(self, btn):
            print(btn.track)
            for frame in self.root.playlist.playlist.values():
                button = frame.songBtn
                if button is btn:
                    button.configure(fg_color=ThemeManager.theme["color"]["button"])
                else:
                    button.configure(fg_color="gray")
            self.activeBtn = btn
            self.master.spotifyFm.search_spotify(btn.track)

    class SpotifySearchFrame(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root

            self.label = ctk.CTkLabel(master=self, text="Add tracks to search!")
            self.label.pack(side=tk.TOP, fill=tk.X, expand=1)

            self.scroll_canvas, self.innerFrame = library.create_scroll_canvas(
                master=self
            )

        def search_spotify(self, track):
            for child in self.innerFrame.winfo_children():

                child.destroy()

            self.label.configure(
                text="Searching for {} by {} on Spotify".format(track[0], track[1])
            )

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
                addtoPlaylist.configure(command=lambda tr=track: self.add_song(tr))
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

        def add_song(self, track):
            print(track)
            self.root.final_playlist.append(track)
            self.root.frames["SpotifyPage"].playlistReviewFm.update()
