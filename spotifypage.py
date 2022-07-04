import customtkinter as ctk
import tkinter as tk

import library


class SpotifyPage(ctk.CTkFrame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.playlistReviewFm = SpotifyPage.PlaylistReview(master=self, root=root)
        self.playlistReviewFm.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        self.addPlaylistFm = SpotifyPage.AddPlaylist(master=self, root=root)
        self.addPlaylistFm.grid(
            row=0, column=1, sticky=tk.NSEW, ipadx=20, padx=10, pady=10
        )

        self.columnconfigure(0, weight=1, uniform="group_sp_1")
        self.columnconfigure(1, weight=1, uniform="group_sp_1")
        self.rowconfigure(0, weight=1)

    def toggle_scroll(self):
        self.playlistReviewFm.toggle_scroll()
        self.addPlaylistFm.toggle_scroll()

    class PlaylistReview(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.root = root
            self.final_songFrames = []

            playlistLabel = ctk.CTkLabel(master=self, text="Current playlist")
            playlistLabel.pack(side=tk.TOP, fill=tk.X, ipady=10)

            self.dummyFrame = ctk.CTkFrame(master=self)
            self.dummyFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # create scrollable frame
            self.scrollable = library.Scrollable(master=self.dummyFrame, root=self.root)
            self.scroll_canvas, self.innerFrame = (
                self.scrollable.scroll_canvas,
                self.scrollable.innerFrame,
            )
            self.goBackBtn = ctk.CTkButton(
                master=self,
                text="< edit playlist",
                pady=20,
                command=lambda: root.show_frame("PlaylistPage"),
            )
            self.goBackBtn.pack()

        def addToFinal(self, addBtn, track):
            finalFrame = ctk.CTkFrame(master=self.innerFrame)
            finalFrame.addBtn = addBtn

            album = ctk.CTkLabel(
                master=finalFrame,
                anchor=tk.W,
                justify="center",
                pady=10,
            )
            library.load_song_album(album, track, size=(70, 70))
            album.pack(side=tk.LEFT)

            titleLabel = ctk.CTkLabel(
                master=finalFrame,
                text=track.track_title,
                anchor=tk.W,
                justify="center",
                pady=10,
            )
            artistsText = track.artists[0]
            for artist in track.artists[1:]:
                artistsText += ", " + artist
                if len(artistsText) >= 40:
                    artistsText += ", ..."
                    break
            artistLabel = ctk.CTkLabel(
                master=finalFrame,
                text=artistsText,
                anchor=tk.W,
                wraplength=100,
                justify="center",
                pady=10,
            )

            titleLabel.pack(side=tk.LEFT, fill=tk.X, expand=1)
            artistLabel.pack(side=tk.LEFT)
            durationLabel = ctk.CTkLabel(
                master=finalFrame,
                text=track.duration,
            )
            durationLabel.pack(side=tk.LEFT)

            removeBtn = ctk.CTkButton(
                master=finalFrame,
                text="X",
                width=20,
                command=lambda tr=track, f=finalFrame: self.removeFromFinal(f, tr),
            )
            removeBtn.pack(side=tk.LEFT)
            finalFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.final_songFrames.append(finalFrame)

            self.innerFrame.columnconfigure(1, weight=1)
            return finalFrame

        def removeFromFinal(self, del_frame, track):
            del_frame.addBtn.configure(text="+")
            del_frame.destroy()
            self.root.final_playlist.remove(track)
            self.toggle_scroll()

        def toggle_scroll(self):
            self.scrollable.toggle_scroll()

    class AddPlaylist(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.root = root

            self.radio_var = tk.IntVar(master=self, value=0)
            spacer = ctk.CTkLabel(master=self, text="")
            spacer.grid(row=0, column=1)

            radioButton_1 = ctk.CTkRadioButton(
                master=self,
                text="Add to new playlist",
                command=self.frame_select,
                variable=self.radio_var,
                value=0,
            )
            radioButton_2 = ctk.CTkRadioButton(
                master=self,
                text="Add to own playlist",
                command=self.frame_select,
                variable=self.radio_var,
                value=1,
            )
            radioButton_3 = ctk.CTkRadioButton(
                master=self,
                text="Add to playlist by id",
                command=self.frame_select,
                variable=self.radio_var,
                value=2,
            )

            radioButton_1.grid(row=1, column=1)
            radioButton_2.grid(row=2, column=1)
            radioButton_3.grid(row=3, column=1)

            dummyFrame_0 = ctk.CTkFrame(master=self)
            self.titleBar = ctk.CTkEntry(
                master=dummyFrame_0,
                placeholder_text="Enter playlist title",
                width=700,
            )
            self.titleBar.pack(side=tk.TOP)

            self.dummyFrame_1 = ctk.CTkFrame(master=self)

            # create scrollable frame
            self.scrollable = library.Scrollable(
                master=self.dummyFrame_1, root=self.root
            )
            self.scroll_canvas, self.innerFrame = (
                self.scrollable.scroll_canvas,
                self.scrollable.innerFrame,
            )
            self.load_playlists(self.innerFrame)

            dummyFrame_2 = ctk.CTkFrame(master=self)
            self.idBar = ctk.CTkEntry(
                master=dummyFrame_2,
                placeholder_text="Enter playlist id",
                width=700,
            )
            self.idBar.pack(side=tk.TOP)

            self.frames = [dummyFrame_0, self.dummyFrame_1, dummyFrame_2]
            for frame in self.frames:
                frame.grid(row=4, column=1, sticky=tk.NSEW)

            radioButton_1.invoke()

            self.addButton = ctk.CTkButton(
                master=self,
                text="Add to Spotify",
                pady=20,
                command=lambda: library.addPlaylist(
                    self.get_playlist(), self.root.final_playlist
                ),
            )
            self.addButton.grid(row=5, column=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(4, weight=1)
            self.rowconfigure(0, minsize=20)

        def frame_select(self):
            print(f"button {self.radio_var.get()} selected")

            self.frames[self.radio_var.get()].tkraise()

        def load_playlists(self, frame):
            user_pls = library.get_user_playlists()
            self.selectButtons = []

            for i, pl in enumerate(user_pls["items"]):
                label = ctk.CTkLabel(master=frame, text=pl["name"])
                label.grid(row=i, column=0, sticky=tk.EW)
                selectBtn = ctk.CTkButton(
                    master=frame,
                    text="select",
                    command=lambda index=i: self.select_playlist(index),
                )
                selectBtn.grid(row=i, column=1)
                selectBtn.pl = pl
                self.selectButtons.append(selectBtn)
            frame.columnconfigure(0, weight=1)

        def select_playlist(self, index):
            self.index = index

        def get_playlist(self):
            match self.radio_var.get():
                case 0:
                    return library.new_playlist(self.titleBar.get())
                case 1:
                    return self.selectButtons[self.index].pl
                case 2:
                    return library.get_playlist(self.idBar.get())

        def toggle_scroll(self):
            self.scrollable.toggle_scroll()
