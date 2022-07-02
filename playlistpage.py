import asyncio
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from customtkinter import ThemeManager

import library


class PlaylistPage(ctk.CTkFrame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = library.MediaPlayer()

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
                master=buttonHolderFrame,
                text=f"{track[0]} by {track[1]}",
                fg_color="gray",
                width=60,
            )
            songBtn.track = track
            songBtn.configure(command=lambda i=songBtn: self.songBtnOnClick(i))
            songBtn.pack(side=tk.LEFT, fill=tk.X, expand=1)
            songBtn.results = None
            buttonHolderFrame.songBtn = songBtn
            removeBtn = ctk.CTkButton(
                master=buttonHolderFrame,
                text="X",
                width=20,
                # command=lambda t=track: self.root.playlist.update_playlist(t),
            )
            removeBtn.configure(
                command=lambda i=removeBtn, t=track: self.removeBtnOnClick(i, t)
            )
            removeBtn.pack(side=tk.RIGHT)
            buttonHolderFrame.pack(side=tk.TOP, fill=tk.X, expand=1)

            return buttonHolderFrame

        def songBtnOnClick(self, btn):
            print(btn.track)
            for frame in self.root.playlist.playlist.values():
                button = frame.songBtn
                if button is btn:
                    button.configure(fg_color=ThemeManager.theme["color"]["button"])
                else:
                    button.configure(fg_color="gray")
            self.activeBtnFm = btn.master
            asyncio.run(self.master.spotifyFm.search_spotify(btn.track))

        def removeBtnOnClick(self, btn, t):
            if self.activeBtnFm is btn.master:
                self.master.spotifyFm.clear_search()

            self.root.playlist.update_playlist(t)

    class SpotifySearchFrame(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root

            self.query = None

            img = Image.open("assets/dark_mode_loading70x70.png")
            self.loading_img = ImageTk.PhotoImage(img)

            self.label = ctk.CTkLabel(master=self, text="Add tracks to search!")
            self.label.pack(side=tk.TOP, pady=20)

            self.album_img = ctk.CTkLabel(master=self, text="")
            self.album_img.pack(side=tk.TOP, pady=20)

            self.scroll_canvas, self.innerFrame = library.create_scroll_canvas(
                master=self
            )
            self.activePlay = None

        def clear_search(self):
            for child in self.innerFrame.winfo_children():

                child.destroy()
            self.master.player.stop()

            self.label.configure(text="Add tracks to search!")
            # self.album_img.pack_forget()
            self.album_img.configure(image="")

        async def search_spotify(self, track):
            # for child in self.innerFrame.winfo_children():

            #     child.destroy()
            if self.query == track:
                return

            self.query = track

            self.clear_search()
            self.label.configure(
                text="Searching for {} by {} on Spotify".format(track[0], track[1])
            )

            self.playBtns = []

            self.previous, self.next, self.tracks = library.search_spotify(
                track[0], track[1]
            )

            for i, track in enumerate(self.tracks):
                print(track.track_title, track.preview_url)

                playBtn = tk.Button(
                    master=self.innerFrame,
                    image=self.loading_img,
                    highlightthickness=0,
                    bd=0,
                )
                playBtn.configure(
                    command=lambda btn=playBtn, tr=track: self.playOnClick(btn, tr)
                )
                asyncio.create_task(library.setButtonCover(playBtn, track))
                playBtn.grid(row=i, column=0)
                self.playBtns.append(playBtn)

                changeFinal = ctk.CTkButton(master=self.innerFrame, width=60)
                # if track in self.root.final_playlist:
                #    changeFinal.configure(text='-')
                # else:
                changeFinal.configure(text="+")
                changeFinal.configure(
                    command=lambda btn=changeFinal, tr=track: self.updatefinal(btn, tr)
                )
                changeFinal.grid(row=i, column=4, sticky=tk.NSEW)

                playBtn.changeFinal = changeFinal

                titleLabel = ctk.CTkLabel(
                    master=self.innerFrame,
                    text=track.track_title,
                    anchor=tk.W,
                    # wraplength=100,
                    justify="center",
                    pady=10,
                )
                # if len(track.track_title) > 30:
                #    titleLabel.configure(text=track.track_title[0:30])
                # wraplength=100, justify="center"

                artistsText = track.artists[0]
                for artist in track.artists[1:]:
                    artistsText += ", " + artist
                    if len(artistsText) >= 40:
                        artistsText += ", ..."
                        break

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
                titleLabel.grid(row=i, column=1, sticky=tk.NSEW)
                artistLabel.grid(row=i, column=2, sticky=tk.NSEW)
                durationLabel = ctk.CTkLabel(
                    master=self.innerFrame,
                    text=track.duration,
                )
                durationLabel.grid(row=i, column=3, sticky=tk.NSEW)

                self.innerFrame.columnconfigure(1, weight=1)
                self.update()

        def clearSearch(self):
            for child in self.winfo_children():
                child.destroy()

        def updatefinal(self, btn, track):
            # print(track)
            if track in self.root.final_playlist:
                # self.root.final_playlist.remove(track)
                btn.configure(text="+")
                self.root.frames["SpotifyPage"].playlistReviewFm.removeFromFinal(
                    btn.finalFrame, track
                )
            else:
                self.root.final_playlist.append(track)
                btn.configure(text="-")
                btn.finalFrame = self.root.frames[
                    "SpotifyPage"
                ].playlistReviewFm.addToFinal(btn, track)

        def playOnClick(self, btn, tr):
            asyncio.run(library.load_album_cover(self, tr))
            # isbtn = False
            self.master.player.play(tr.preview_url)

            # if

            # for playing in self.playBtns:
            #     if playing == self.activePlay:
            #         # laying.configure(text="play")
            #         # library.stopPreview(self.p)
            #         self.player = vlc.MediaPlayer(tr.preview_url)
            #         self.player.play()
            #         print(self.player.get_media())
            #         self.activePlay = None
            #         isbtn = True
            #         break
            # if not isbtn:
            #     # btn.configure(text="pause")
            #     # self.p = library.loadPreview(tr)

            #     self.activePlay = btn
