import whisper
import os
import requests
from pydub import AudioSegment

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model():

    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model 


INDIAN_LANGUAGES = {
    "hinglish", "hindi", "telugu", "tamil", "kannada",
    "malayalam", "bengali", "gujarati", "marathi", "punjabi", "odia"
}


def transcribe_chunk_whisper(chunk_path: str, task: str = "transcribe") -> str:
    try:
        audio = AudioSegment.from_file(chunk_path)
        if len(audio) < 500:
            return ""
    except Exception:
        pass

    model = load_model()  
    result = model.transcribe(chunk_path, task=task)  
    return result["text"]  


def _get_sarvam_api_key() -> str:
    return os.getenv("SARVAM_API_KEY") or SARVAM_API_KEY

def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    api_key = _get_sarvam_api_key()
    headers = {"api-subscription-key": api_key}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": os.getenv("SARVAM_STT_MODEL", SARVAM_MODEL), "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    api_key = _get_sarvam_api_key()
    if not api_key:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route chunk to Sarvam or Whisper based on language choice:
    - english  → Whisper (local model, transcribe)
    - Indian languages (telugu, hinglish/hindi, tamil, etc.) → Sarvam AI (if key set), else Whisper (translate)
    - auto / other → Whisper (local model, translate to English)
    """
    lang = language.lower().strip()
    if lang == "english":
        return transcribe_chunk_whisper(chunk_path, task="transcribe")

    api_key = _get_sarvam_api_key()
    if lang in INDIAN_LANGUAGES and api_key:
        return transcribe_chunk_sarvam(chunk_path)

    # Fallback / Global translation to English via Whisper
    return transcribe_chunk_whisper(chunk_path, task="translate")


def get_transcription_engine(language: str = "english") -> str:
    """Helper to get descriptive engine name being used."""
    lang = language.lower().strip()
    if lang == "english":
        return "Whisper (Local Transcribe)"
    api_key = _get_sarvam_api_key()
    if lang in INDIAN_LANGUAGES and api_key:
        return f"Sarvam AI ({lang.title()} -> English STT Translate)"
    return f"Whisper (Local {lang.title()} -> English Translate)"


def transcribe_all(chunks, language: str = "english") -> str:
    if isinstance(chunks, str):
        print("Using direct transcript extracted via API.")
        return chunks.strip()

    full_transcript = "" 
    engine_name = get_transcription_engine(language)
    print(f"Using {engine_name} for transcription.")

    for i, chunk in enumerate(chunks):  
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)  
        full_transcript += text + " "  

    print("Transcription complete.")
    return full_transcript.strip()  
