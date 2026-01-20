import os
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
# from moviepy import VideoFileClip, AudioFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio
from re import sub, search, compile

def downloadAudio(url, dir="", status=None):
    dir = f"DOWNLOADED\\{dir}"
    yt = YouTube(url, on_progress_callback=on_progress)
    title = yt.title
    if status: status(msg2=f"Song: {title}")
    ys = yt.streams.filter(only_audio=True).order_by("abr").last()
    ys.download(output_path=dir)

def downloadVideo(url, res="1080p", dir="", status=None):
    dir = f"DOWNLOADED\\{dir}"
    yt = YouTube(url, on_progress_callback=on_progress)
    title = sub("[^A-Za-z0-9 ]", "", yt.title)
    if status: status(msg2=f"Video: {title}")
    ys = yt.streams
    yv = ys.filter(progressive=True, res=res)
    if len(yv) > 0:
        yv = yv.first()
        yv.download(output_path=dir)
    else:
        yv = ys.filter(res=res).first()
        if not yv:
            print("Video not available in that resolution")
            return
        ya = ys.filter(only_audio=True, audio_codec="mp4a.40.2").order_by("abr").last()

        yv.download(output_path=dir, filename=f"{title}_video.mp4", )
        ya.download(output_path=dir, filename=f"{title}_audio.mp4")

        ffmpeg_merge_video_audio(f"{dir}{title}_video.mp4", f"{dir}{title}_audio.mp4", f"{dir}{title}.mp4")
        # video_clip = VideoFileClip(f"{title}_video.mp4")
        # audio_clip = AudioFileClip(f"{title}_audio.mp4")
        # video_clip.audio = audio_clip
        # video_clip.write_videofile(f"{title}.mp4", threads=16)
        os.remove(f"{dir}{title}_video.mp4")
        os.remove(f"{dir}{title}_audio.mp4")

def downloadPlaylist(url, res="1080p", music=False, status=None):
    ytp = Playlist(url)
    title = sub("[^A-Za-z0-9 ]", "", ytp.title)
    if status: status(msg1=f"Downloading Playlist ({len(ytp.video_urls)} items)")
    print(ytp.video_urls)
    for ytv in ytp.video_urls:
        if music: downloadAudio(ytv, f"{title}\\", status)
        else: download(ytv, res, f"{title}\\", status)


def getPlaylistVideos(url):
    ytp = Playlist(url)
    return ytp.video_urls


def download(url, res="1080p", dir="", status=None):
    t = getVideoType(url)
    if t == "watch":
        downloadVideo(url, res, dir, status)
    elif t == "playlist":
        downloadPlaylist(url, res, status)
    elif t == "music":
        print(url)
        downloadAudio(url, dir, status)
    elif t == "music playlist":
        downloadPlaylist(url, res, True, status)
    elif t == "shorts":
        downloadVideo(url, res, dir, status)
    elif t == "list":
        for link in url:
            download(link, res, dir, status)
    else:
        print("Not a valid Youtube Video or Playlist")
        return None

def getVideoType(url):
    if type(url) == list:
        return "list"
    if "playlist" in url and "music.youtube" in url:
        return "music playlist"
    if "playlist" in url:
        return "playlist"
    elif "music.youtube" in url:
        return "music"
    elif "shorts" in url:
        return "shorts"
    elif "watch" in url:
        return "watch"
    p = compile("(?:youtube.com/)([^?]+)")
    s = p.search(url)
    if s:
        return s.group(1)
    return ""

# download(input("URL: "), input("Res: "))