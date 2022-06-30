import customtkinter as ctk
import tkinter as tk

import library

import animesearchpage
import playlistpage
import spotifypage

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class tkinterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1920x1080")
        self.minsize(1200, 500)

        self.final_playlist = []
        self.playlist = library.Playlist()

        masterFrame = ctk.CTkFrame(master=self)

        masterFrame.grid_rowconfigure(0, weight=1)
        masterFrame.grid_columnconfigure(0, weight=1)
        masterFrame.pack(side=tk.TOP, fill="both", expand=True)

        self.frames = {}
        for page in (
            animesearchpage.AnimeSearchPage,
            playlistpage.PlaylistPage,
            spotifypage.SpotifyPage,
        ):
            frame = page(master=masterFrame, root=self)
            self.frames[page.__name__] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.playlist.playlistPage = self.frames["PlaylistPage"]
        self.playlist.animePage = self.frames["AnimeSearchPage"]

        self.show_frame("AnimeSearchPage")
        # self.show_frame("SpotifyPage")

    def show_frame(self, page: str) -> None:
        frame = self.frames[page]
        # if page == "PlaylistPage":
        #     frame.playlistFm.load_current_playlist()
        frame.tkraise()


if __name__ == "__main__":
    app = tkinterApp()
    app.mainloop()