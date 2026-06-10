import os
import subprocess
import shutil

import yt_dlp


def get_ffmpeg_path():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    chocolatey_install = os.environ.get(
        "ChocolateyInstall", r"C:\ProgramData\chocolatey"
    )
    fallback_path = os.path.join(chocolatey_install, "bin", "ffmpeg.exe")
    if os.path.exists(fallback_path):
        return fallback_path

    return None


def convert_existing_files_to_mp3(downloads_dir, expected_stem=None):
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("ffmpeg non trovato: salto la conversione automatica dei file esistenti.")
        return

    for entry in os.scandir(downloads_dir):
        if not entry.is_file():
            continue

        source_path = entry.path
        base_name, extension = os.path.splitext(source_path)
        if extension.lower() == ".mp3":
            continue

        if expected_stem and os.path.basename(base_name) != expected_stem:
            continue

        target_path = f"{base_name}.mp3"
        if os.path.exists(target_path):
            print(f"MP3 gia presente, salto: {target_path}")
            continue

        print(f"Converto: {source_path} -> {target_path}")
        result = subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-i",
                source_path,
                "-vn",
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                target_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            os.remove(source_path)
            print(f"Conversione completata: {target_path}")
        else:
            print(f"Conversione fallita per {source_path}: {result.stderr.strip()}")


def download_audio(yt_url):
    try:
        video_info = (
            yt_dlp.YoutubeDL({"quiet": True}).extract_info(url=yt_url, download=False)
            or ""
        )
    except Exception:
        return

    safe_title = video_info.get("title", "audio").replace("/", "_").replace("\\", "_")
    filename = f"downloads/{safe_title}.mp3"
    if os.path.exists(filename):
        print(f"Gia presente: {filename}")
        return

    options = {
        "format": "bestaudio/best",
        "outtmpl": f"downloads/{safe_title}.%(ext)s",
        "noplaylist": True,
    }

    # Convert to mp3 only if ffmpeg is available; otherwise keep original audio format.
    if get_ffmpeg_path():
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            ydl.download([video_info["webpage_url"]])
            convert_existing_files_to_mp3("downloads", safe_title)
        except yt_dlp.utils.DownloadError as exc:
            print(f"Download fallito per {yt_url}: {exc}")


if __name__ == "__main__":
    link = "https://youtube.com/playlist?list=PLDhajrZgo0TI6bdIbpG0S71LBH6t85Z0V&si=sRVbPUqgXb6A5qj8"
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
        playlist_info = ydl.extract_info(link, download=False)

    urls = []
    for entry in playlist_info.get("entries", []):
        video_id = entry.get("id")
        if video_id:
            urls.append(f"https://www.youtube.com/watch?v={video_id}")

    if not os.path.exists("downloads"):
        os.mkdir("downloads")

    convert_existing_files_to_mp3("downloads")

    newUrl = []
    for link in urls:
        newUrl.append(link)
    newUrl.reverse()
    for link in newUrl:
        download_audio(link)
