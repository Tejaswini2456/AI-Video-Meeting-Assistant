# 🎬 AI Video Assistant — Meeting Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Mistral AI](https://img.shields.io/badge/LLM-Mistral%20AI-orange.svg)](https://mistral.ai/)
[![OpenAI Whisper](https://img.shields.io/badge/STT-OpenAI%20Whisper-green.svg)](https://github.com/openai/whisper)
[![Sarvam AI](https://img.shields.io/badge/STT-Sarvam%20AI-purple.svg)](https://www.sarvam.ai/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-yellow.svg)](https://www.trychroma.com/)

An AI-powered video and meeting intelligence platform that transcribes, translates, summarizes, extracts actionable insights, and enables RAG-based interactive chat with audio and video content.

---

## ✨ Key Features

- 🔊 **Audio & Video Acquisition**: Direct ingestion from YouTube URLs or local media files (`.mp4`, `.mp3`, `.wav`, `.m4a`).
- 🌐 **Multi-Language STT & Translation**: 
  - **Indian Regional Languages**: Native support for **Telugu (తెలుగు)**, **Hindi (हिंदी)**, **Tamil (தமிழ்)**, **Kannada (ಕನ್ನಡ)**, **Malayalam**, **Bengali**, **Gujarati**, **Marathi**, and **Punjabi**.
  - **Global Languages**: Automatic Whisper translation to English for global speech.
- ⚡ **Dual STT Engine Architecture**:
  - **Sarvam AI (`saaras:v2.5`)**: High-accuracy cloud STT & translation for Indian regional languages.
  - **OpenAI Whisper**: Local, offline speech recognition and translation.
- 📋 **Automated Executive Summaries**:
  - Map-Reduce summarization for long transcripts.
  - Action Items extraction (with Task Description, Owner, and Deadline).
  - Key Decisions & Open Questions breakdown.
  - ⏱️ **Timestamped Agenda & Key Moments**: Chronologically bounded topic breakdown.
- 🧠 **Interactive RAG Chat**: RAG pipeline powered by ChromaDB vector store, HuggingFace embeddings, and Mistral AI LLM.
- 📥 **One-Click Export**: Download publication-ready **PDF Reports** or **Markdown Summaries**.
- 📚 **Session History Library**: Local persistent storage (`history/meetings.json`) to reload past sessions instantly without re-processing.

---

## 🛠️ Project Structure

```text
AI-Video-Assistant/
├── app.py                      # Main Streamlit Web Application
├── main.py                     # Command Line Interface (CLI)
├── Requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Exclusion Rules
├── core/
│   ├── transcriber.py          # Dual Engine STT Routing (Sarvam AI & Whisper)
│   ├── summarizer.py           # LangChain LCEL Map-Reduce Summarizer
│   ├── extractor.py            # Extraction Chains (Action Items, Decisions, Timestamps)
│   ├── rag_engine.py           # RAG Retrieval & QA Chain
│   └── vector_store.py         # ChromaDB Vector Store Builder
├── utils/
│   ├── audio_processor.py      # Audio Acquisition, Conversion & Slicing
│   ├── exporter.py             # PDF & Markdown Report Generators
│   └── history_manager.py      # Persistent Session History Manager
├── history/                    # Saved Meeting Sessions (JSON)
└── downloades/                 # Working Audio Directory
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Tejaswini2456/AI-Video-Assistant.git
cd AI-Video-Assistant
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r Requirements.txt
```

> **Prerequisite**: Ensure [FFmpeg](https://ffmpeg.org/) is installed and added to your system `PATH`.

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and add your API keys:
```ini
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

---

## 🏃 Running the Application

### Option A: Streamlit Web UI (Recommended)
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Option B: Command Line Interface (CLI)
```bash
python main.py
```

---

## 👤 Contributor

- **Tejaswini** ([@Tejaswini2456](https://github.com/Tejaswini2456))

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

