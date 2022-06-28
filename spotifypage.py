import customtkinter as ctk
import tkinter as tk

import library


class SpotifyPage(ctk.CTkFrame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.playlistReviewFm = SpotifyPage.PlaylistReview(master=self, root=root)
        self.playlistReviewFm.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        self.addPlaylistFm = SpotifyPage.AddPlaylist(master=self, root=root)
        self.addPlaylistFm.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)

        self.columnconfigure(0, weight=1, uniform="group1")
        self.columnconfigure(1, weight=1, uniform="group1")

    class PlaylistReview(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.root = root

            for track in self.root.final_playlist:
                label = ctk.CTkLabel(master=self, text=track)
                label.pack()

            self.goBackBtn = ctk.CTkButton(
                master=self,
                text="< edit playlist",
                pady=20,
                command=lambda: root.show_frame("PlaylistPage"),
            )
            self.goBackBtn.pack()

    class AddPlaylist(ctk.CTkFrame):
        def __init__(self, root, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.root = root

            self.addButton = ctk.CTkButton(
                master=self,
                text="Add to Spotify",
                pady=20,
                command=lambda: library.addPlaylist(self.root.final_playlist),
            )
            self.addButton.pack()
