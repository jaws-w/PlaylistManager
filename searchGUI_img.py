import asyncio
import customtkinter as ctk
import tkinter as tk

import library

import animesearchpage
import playlistpage
import spotifypage

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class tkinterApp(ctk.CTk):
    def __init__(self, loop: asyncio.AbstractEventLoop, interval: float = 1 / 120):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.tasks.append(loop.create_task(self.updater(interval)))

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

    def show_frame(self, page: str) -> None:
        frame = self.frames[page]
        self.frames["PlaylistPage"].player.stop()
        frame.tkraise()

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


if __name__ == "__main__":
    asyncioLoop = asyncio.new_event_loop()
    app = tkinterApp(asyncioLoop)
    asyncioLoop.run_forever()
    asyncioLoop.close()
