import os

import youtube_dl
from pytube import Playlist


def download_audio(yt_url):
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(url=yt_url, download=False) or ""
    except:
        return
    filename = f"downloads/{video_info['title']}.mp3"
    if os.path.exists(filename):
        print(filename)
        return
    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': filename,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])


if __name__ == '__main__':
    link = "https://music.youtube.com/playlist?list=PLHBDkKdpuQN8f6p0KAU0uRbB0KBkUHnI3&feature=share"
    urls = Playlist(link).video_urls
    urls = list(urls)
    newUrl = []
    for link in urls:
        newUrl.append(link)
    newUrl.reverse()
    for link in newUrl:
        download_audio(link)
