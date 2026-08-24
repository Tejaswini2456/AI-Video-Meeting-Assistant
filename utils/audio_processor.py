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
        api = YouTubeTranscriptApi() if callable(YouTubeTranscriptApi) else None
        fetched_snippets = None
        
        # Method 1: Try direct fetch (v1.x)
        if api and hasattr(api, "fetch"):
            try:
                fetched_snippets = api.fetch(video_id)
            except Exception as e_fetch:
                print(f"api.fetch failed: {e_fetch}")
        
        # Method 2: Iterate over transcript list
        if not fetched_snippets and api and hasattr(api, "list"):
            try:
                transcript_list = api.list(video_id)
                for t in transcript_list:
                    fetched_snippets = t.fetch()
                    if fetched_snippets:
                        break
            except Exception as e1:
                print(f"api.list failed: {e1}")

        if fetched_snippets:
            full_text = " ".join([snippet.text if hasattr(snippet, "text") else snippet.get("text", "") if isinstance(snippet, dict) else str(snippet) for snippet in fetched_snippets])
            last_item = fetched_snippets[-1]
            start_val = last_item.start if hasattr(last_item, "start") else last_item.get("start", 0.0) if isinstance(last_item, dict) else 0.0
            dur_val = last_item.duration if hasattr(last_item, "duration") else last_item.get("duration", 0.0) if isinstance(last_item, dict) else 0.0
            duration_sec = float(start_val + dur_val)
            if full_text.strip():
                return full_text, duration_sec

    except Exception as e:
        print(f"youtube-transcript-api extraction failed: {e}")

    return None, 0.0

def fetch_youtube_transcript_ytdlp(url: str):
    """Fallback transcript extractor using yt-dlp caption metadata (doesn't trigger 403 audio download block)."""
    try:
        import urllib.request
        import json
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = float(info.get('duration', 0.0))
            subs = info.get('subtitles', {}) or {}
            auto_subs = info.get('automatic_captions', {}) or {}
            all_subs = {**auto_subs, **subs}
            
            preferred_langs = ['en', 'en-US', 'en-GB'] + list(all_subs.keys())
            for lang in preferred_langs:
                if lang in all_subs and all_subs[lang]:
                    formats = all_subs[lang]
                    json3_fmt = next((f for f in formats if f.get('ext') == 'json3'), None)
                    if json3_fmt and 'url' in json3_fmt:
                        req = urllib.request.Request(json3_fmt['url'], headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as res:
                            data = json.loads(res.read().decode('utf-8'))
                            events = data.get('events', [])
                            text_parts = []
                            for e in events:
                                segs = e.get('segs', [])
                                text = ''.join([s.get('utf8', '') for s in segs if 'utf8' in s]).strip()
                                if text and text != '\n':
                                    text_parts.append(text)
                            if text_parts:
                                return ' '.join(text_parts), duration
    except Exception as e:
        print(f"yt-dlp subtitle extraction fallback failed: {e}")
    return None, 0.0

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    client_configs = [
        ["web_creator"],
        ["mweb"],
        ["ios"],
        ["android_vr"],
        ["tv_embedded"],
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
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"

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
    if os.path.exists("cookies.txt"):
        ydl_opts["cookiefile"] = "cookies.txt"

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
        if not transcript:
            print("Transcript API unavailable. Attempting yt-dlp subtitle metadata fallback...")
            transcript, duration_sec = fetch_youtube_transcript_ytdlp(source)

        if transcript:
            print("Successfully extracted YouTube transcript!")
            return transcript, None, duration_sec
        
        print("Subtitles/Transcript unavailable. Falling back to audio download via yt-dlp...")
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



