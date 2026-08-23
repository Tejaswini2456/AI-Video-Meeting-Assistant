import yt_dlp
from pydub import AudioSegment
import os
import re

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_youtube_video_id(url: str) -> str:
    pattern = r'(?:v=|\/|be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def fetch_youtube_transcript_api(url: str):
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return None, 0.0
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=['en', 'hi', 'te', 'ta', 'kn', 'ml', 'mr', 'gu', 'bn', 'pa', 'auto']
        )
        full_text = " ".join([item['text'] for item in transcript_list])
        last_item = transcript_list[-1]
        duration_sec = float(last_item['start'] + last_item.get('duration', 0.0))
        return full_text, duration_sec
    except Exception as e:
        print(f"youtube-transcript-api fallback to yt-dlp: {e}")
        return None, 0.0

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    client_configs = [
        ["ios"],
        ["android_vr"],
        ["tv_embedded"],
        ["mweb"],
        ["android"],
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    for client in client_configs:
        ydl_opts = {
            "format": "m4a/ba/b",
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "user_agent": headers["User-Agent"],
            "http_headers": headers,
            "extractor_args": {
                "youtube": {
                    "player_client": client
                }
            },
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                raw_filename = ydl.prepare_filename(info)
                filename = os.path.splitext(raw_filename)[0] + ".wav"
                if os.path.exists(filename):
                    return filename
        except Exception:
            continue
            
    # Final fallback attempt with generic settings
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "nocheckcertificate": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_filename = ydl.prepare_filename(info)
            filename = os.path.splitext(raw_filename)[0] + ".wav"
            return filename
    except Exception as e:
        raise RuntimeError("YouTube 403 Forbidden: YouTube blocked direct audio stream downloading on this cloud server. Please try a video with captions, or upload your media file (.mp4, .mp3, .wav) directly using the File Uploader in the sidebar.") from e

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> tuple:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Attempting transcript API extraction...")
        transcript, duration_sec = fetch_youtube_transcript_api(source)
        if transcript:
            print("Successfully extracted YouTube transcript via API!")
            return transcript, None, duration_sec
        
        print("Transcript API unavailable. Falling back to audio download via yt-dlp...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local/uploaded file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    audio = AudioSegment.from_wav(wav_path)
    duration_sec = len(audio) / 1000.0

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks, wav_path, duration_sec



