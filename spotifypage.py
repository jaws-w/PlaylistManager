import customtkinter as ctk
from customtkinter import ThemeManager
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

            self.innerFrame.columnconfigure(1, weight=1)
            self.next_row = 0

            self.goBackBtn = ctk.CTkButton(
                master=self,
                text="< edit playlist",
                pady=20,
                command=lambda: root.show_frame("PlaylistPage"),
            )
            self.goBackBtn.pack(fill=tk.X)

        def addToFinal(self, addBtn, track):
            finalFrame = SpotifyPage.SpotifyTrackDisplay(
                addBtn, self.innerFrame, track, self.next_row, self
            )
            self.next_row += 1
            return finalFrame

        def removeFromFinal(self, del_frame, track):
            del_frame.addBtn.configure(text="+", fg_color="gray")
            del_frame.destroy()
            self.root.final_playlist.remove(track)
            self.toggle_scroll()

        def toggle_scroll(self):
            self.scrollable.toggle_scroll()

    class SpotifyTrackDisplay:
        def __init__(self, addBtn, master, track, row, plrev) -> None:
            self.addBtn = addBtn

            self.album = ctk.CTkLabel(
                master=master,
                anchor=tk.W,
                justify="center",
                pady=10,
            )
            library.load_song_album(self.album, track, size=(70, 70))
            self.album.grid(row=row, column=0, sticky=tk.NSEW)

            self.titleLabel = ctk.CTkLabel(
                master=master,
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
            self.artistLabel = ctk.CTkLabel(
                master=master,
                text=artistsText,
                anchor=tk.W,
                wraplength=100,
                justify="center",
                pady=10,
            )

            self.titleLabel.grid(row=row, column=1, sticky=tk.NSEW)
            self.artistLabel.grid(row=row, column=2, sticky=tk.NSEW)
            self.durationLabel = ctk.CTkLabel(
                master=master,
                text=track.duration,
            )
            self.durationLabel.grid(row=row, column=3, sticky=tk.NSEW)

            self.removeBtn = ctk.CTkButton(
                master=master,
                text="X",
                width=20,
                command=lambda tr=track, f=self: plrev.removeFromFinal(f, tr),
            )
            self.removeBtn.grid(row=row, column=4, sticky=tk.NSEW)

        def destroy(self):
            self.album.destroy()
            self.titleLabel.destroy()
            self.artistLabel.destroy()
            self.removeBtn.destroy()
            self.durationLabel.destroy()

    class AddPlaylist(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.root = root

            self.radio_var = tk.IntVar(master=self, value=0)
            spacer_1 = ctk.CTkLabel(master=self, text="")
            spacer_1.grid(row=0, column=1)

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
                command=self.addBtnOnclick,
            )
            self.addButton.grid(row=5, column=1, sticky=tk.EW)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(4, weight=1)
            self.rowconfigure(0, minsize=20)

        def frame_select(self):
            print(f"button {self.radio_var.get()} selected")

            self.frames[self.radio_var.get()].tkraise()

        def addBtnOnclick(self):
            library.addPlaylist(self.get_playlist(), self.root.final_playlist)
            self.load_playlists(self.innerFrame)

        def load_playlists(self, frame):
            user_pls = library.get_user_playlists()
            self.selectButtons = []

            for child in frame.winfo_children():
                child.destroy()

            for i, pl in enumerate(user_pls["items"]):
                label = ctk.CTkLabel(master=frame, text=pl["name"])
                label.grid(row=i, column=0, sticky=tk.EW)
                selectBtn = ctk.CTkButton(
                    master=frame,
                    text="select",
                    fg_color="gray",
                    command=lambda index=i: self.select_playlist(index),
                )
                selectBtn.grid(row=i, column=1)
                selectBtn.pl = pl
                self.selectButtons.append(selectBtn)
            frame.columnconfigure(0, weight=1)

        def select_playlist(self, index):
            for btn in self.selectButtons:
                btn.configure(fg_color="gray")

            self.selectButtons[index].configure(
                fg_color=ThemeManager.theme["color"]["button"]
            )
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
