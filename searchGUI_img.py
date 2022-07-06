import asyncio
import sys
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

        # default window size
        self.geometry("1920x1080")
        self.minsize(1200, 500)
        self.title("Weeb Playlist Manager")

        # frame for holding the pages
        masterFrame = ctk.CTkFrame(master=self)
        masterFrame.grid_rowconfigure(0, weight=1)
        masterFrame.grid_columnconfigure(0, weight=1)
        masterFrame.pack(side=tk.TOP, fill="both", expand=True)

        # initialize pages into a dictionary
        self.frames = {}
        for page in (
            animesearchpage.AnimeSearchPage,
            playlistpage.PlaylistPage,
            spotifypage.SpotifyPage,
        ):
            frame = page(master=masterFrame, root=self)
            self.frames[page.__name__] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        # data structures for holding playlist
        self.playlist = library.Playlist()
        self.final_playlist = []
        self.scroll_target = None

        self.playlist.playlistPage = self.frames["PlaylistPage"]
        self.playlist.animePage = self.frames["AnimeSearchPage"]

        self.show_frame("AnimeSearchPage")

        self.bind_all("<MouseWheel>", self.scroll_handler)

    # shows the corresponding page
    def show_frame(self, page: str) -> None:
        frame = self.frames[page]
        frame.toggle_scroll()
        self.frames["PlaylistPage"].player.stop()
        frame.tkraise()

    def on_scrollable_enter(self, scrollcanvas=None, event=None):
        print("entered", scrollcanvas)
        if scrollcanvas.scroll_enabled:
            self.scroll_target = scrollcanvas

    def on_scrollable_leave(self, event=None):
        self.scroll_target = None

    # enable trackpad/mousewheel scrolling
    def scroll_handler(self, event):
        if self.scroll_target:
            if sys.platform.startswith("win32"):
                self.scroll_target.yview_scroll(-1 * event.delta // 120, "units")
            elif sys.platform.startswith("darwin"):
                self.scroll_target.yview_scroll(-1 * event.delta, "units")
            else:
                self.scroll_target.yview_scroll(-1 * event.delta, "units")

    # updates the tkinter window
    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    # ends the loops when window is closed
    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


if __name__ == "__main__":

    # We use the asncio loop in place of the
    # default tkinter loop
    # Credit to Terry Jan Reedy on Stackoverflow

    asyncioLoop = asyncio.new_event_loop()
    app = tkinterApp(asyncioLoop)
    asyncioLoop.run_forever()
    asyncioLoop.close()
