# Oral ESL

An oral English-as-a-Second-Language app for Rohingya speakers. Learn vocabulary and phrases with audio, and use the camera to photograph signs or text and get instant English summaries with Rohingya translations.

## Features

- **Category-based learning** – Doctor, navigation, groceries, restaurant, and camera
- **Flashcards** – Grocery items with Rohingya translations and pronunciation
- **Phrase cards** – Common phrases for shopping and daily situations
- **Text-to-speech** – Hear words and phrases in English (gTTS or ElevenLabs AI voice)
- **Camera / Sign reader (sóbi)** – Upload a photo of a sign or text; get OCR → English summary → Rohingya translation

## Project Structure

```
oral-esl/
├── my-app/           # React + Vite frontend
├── backend/          # Flask API (TTS, image upload, OCR pipeline)
├── ocr-to-action/    # OCR (Tesseract) + Gemini for actionable English
├── rohingya-interpreter/  # RAG-based English ↔ Rohingya translation (Ollama)
├── rohingya-dict/    # Dictionary corpus for RAG
└── .env              # API keys and config
```

## Prerequisites

- **Node.js** (for frontend)
- **Python 3.10+**
- **Tesseract OCR** – `sudo apt install tesseract-ocr` (Linux) or `brew install tesseract` (macOS)
- **Ollama** – For rohingya-interpreter (local LLM)
- **Gemini API key** – For OCR → actionable English (see [Google AI Studio](https://aistudio.google.com/apikey))

## Setup

### 1. Environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_key   # optional, for AI voice
```

### 2. Rohingya Interpreter

```bash
cd rohingya-interpreter
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Ensure the [rohingya-dict](../rohingya-dict) pipeline has been run so `output/rag_corpus.json` and `output/dictionary.json` exist. Pull an Ollama model:

```bash
ollama pull llama3.2:3b
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
pip install pytesseract Pillow google-generativeai  # for ocr-to-action
```

### 4. Frontend

```bash
cd my-app
npm install
```

## Running the App

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd my-app
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to the Flask backend on port 5000.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/tts` | GET | Text-to-speech (`?text=...&engine=gtts|elevenlabs`) |
| `/api/image/upload` | POST | Upload image → OCR → English summary → Rohingya translation |

## Camera Flow (sóbi)

1. User uploads a photo (sign, text, etc.)
2. **OCR** (Tesseract) extracts raw text
3. **Gemini** turns it into an actionable English sentence
4. **Rohingya interpreter** translates to Rohingya (Ollama + RAG)

## Optional: ElevenLabs Voice

For higher-quality TTS, add `ELEVENLABS_API_KEY` to `.env` and toggle the TTS switch in the app.

## License

MIT
