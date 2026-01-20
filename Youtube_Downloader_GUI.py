from pytube_downloader import *
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading


class YoutubeDownloaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.px = 10
        self.py = 5

        self.title("Youtube Downloader")
        # self.resizable(False, False)
        
        # URL
        url_frame = tk.Frame(self)
        url_frame.pack(anchor="w", padx=self.px, pady=self.py, fill="x")
        tk.Label(url_frame, text="URL(s)").pack(anchor="w", pady=self.py)
        self.url_text = tk.Text(url_frame, wrap="none", width=50, height=5)
        self.url_text.pack(side="left", fill="both", expand=True)
        self.url_scroll = tk.Scrollbar(url_frame, command=self.url_text.yview)
        self.url_scroll.pack(side="right", fill="y")
        self.url_text.config(yscrollcommand=self.url_scroll.set)
        
        # Resolution
        res_frame = tk.Frame(self)
        res_frame.pack(anchor="w", padx=self.px, pady=self.py, fill="x")
        tk.Label(res_frame, text="Resolution").pack(anchor="w", pady=self.py)
        self.res_combo = ttk.Combobox(res_frame, values=["360p", "480p", "720p", "1080p", "1440p", "2160p"])
        self.res_combo.set("1080p")
        self.res_combo.pack(anchor="w")

        # Download Button
        self.btn_download = tk.Button(self, text="Download", command=self.download)
        self.btn_download.pack(anchor="w", padx=self.px, pady=self.py*2, fill="x")

        # Status Box
        self.status_box = tk.Label(self, text="...", fg="white", bg="black")
        self.status_box.pack(anchor="w", padx=self.px, pady=self.py, fill="x")

        # Open Dir
        self.btn_dir = tk.Button(self, text="Open Download Directory", command=self.open_download_dir)
        self.btn_dir.pack(anchor="center", padx=self.px, pady=self.py*2)
    
    def set_status(self, msg):
        self.status_box.config(text=msg)
        self.update_idletasks()

    def get_urls(self):
        raw = self.url_text.get("1.0", "end")
        return [line.strip() for line in raw.splitlines() if line.strip()]
    
    def download(self):
        urls = self.get_urls()
        res = self.res_combo.get()

        if not urls: 
            self.set_status("No URLs provided")
            return
        
        self.btn_download.config(state="disabled")
        threading.Thread(
            target=self.download_thread, 
            args=(urls, res),
            daemon=True
        ).start()
    
    def download_thread(self, urls, res):
        try:
            for i, url in enumerate(urls):
                tag = f"({i+1}/{len(urls)})"
                self.set_status(f"Getting URL info... {tag}")

                t = getVideoType(url)
                match t:
                    case "":
                        self.set_status("Not a valid URL")
                    case "watch":
                        self.set_status(f"Downloading Video... {tag}")
                        downloadVideo(url, res, status=self.set_status)
                    case "playlist":
                        self.set_status(f"Downloading Playlist... {tag}")
                        downloadPlaylist(url, res, status=self.set_status)
                    case "music":
                        self.set_status(f"Downloading Music... {tag}")
                        downloadAudio(url, status=self.set_status)
                    case "shorts":
                        self.set_status(f"Downloading Short... {tag}")
                        downloadVideo(url, res, status=self.set_status)
            
            self.set_status("Downloads done")
        finally:
            self.url_text.delete("1.0", "end")
            self.btn_download.config(state="normal")
    
    def open_download_dir(self):
        os.startfile("DOWNLOADED")


app = YoutubeDownloaderGUI()
app.mainloop()
