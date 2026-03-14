import os
import sys
import traceback
import hashlib
import subprocess
import uuid

from dotenv import load_dotenv

# Add ocr-to-action to path for perform_ocr and call_gemini
OCR_TO_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', 'ocr-to-action')
sys.path.insert(0, OCR_TO_ACTION_DIR)
from main import perform_ocr, call_gemini, SYSTEM_PROMOPT_ENGLISH
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from gtts import gTTS

load_dotenv()

ROHINGYA_INTERPRETER_DIR = os.path.join(os.path.dirname(__file__), '..', 'rohingya-interpreter')
ROHINGYA_CLI = os.path.join(ROHINGYA_INTERPRETER_DIR, 'cli.py')
ROHINGYA_PYTHON = os.path.join(ROHINGYA_INTERPRETER_DIR, '.venv', 'bin', 'python')
if not os.path.exists(ROHINGYA_PYTHON):
    ROHINGYA_PYTHON = os.path.join(ROHINGYA_INTERPRETER_DIR, '.venv', 'bin', 'python3')
if not os.path.exists(ROHINGYA_PYTHON):
    ROHINGYA_PYTHON = 'python3'  # fallback; ensure rohingya-interpreter deps are installed


def translate_to_rohingya(text):
    """Run rohingya-interpreter CLI as subprocess to avoid NumPy/sklearn import conflicts."""
    if not text or not text.strip():
        return ''
    try:
        result = subprocess.run(
            [ROHINGYA_PYTHON, ROHINGYA_CLI, text.strip(), '-d', 'en2rhg'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=ROHINGYA_INTERPRETER_DIR,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ''
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"[translate_to_rohingya] Error: {e}")
        return ''

app = Flask(__name__)
CORS(app)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

AUDIO_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'audio_cache')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def process_uploaded_image(image_path):
    """
    Custom function called when an image is uploaded via the sóbi (camera) flow.
    Override this to add your own logic (e.g. vision API, object detection, etc.).
    """
    # Example: log the path, run vision model, etc.
    print(f"[process_uploaded_image] Received image: {image_path}")
    return {"path": image_path}


def generate_with_gtts(text, cache_path):
    tts = gTTS(text=text, lang='en', slow=True)
    tts.save(cache_path)


def generate_with_elevenlabs(text, cache_path):
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id='JBFqnCBsd6RMkjVDRZzb',
        model_id='eleven_flash_v2_5',
        output_format='mp3_44100_128',
    )

    with open(cache_path, 'wb') as f:
        for chunk in audio:
            if isinstance(chunk, bytes):
                f.write(chunk)


@app.route('/api/health')
def health():
    return jsonify(status='ok')


@app.route('/api/tts')
def text_to_speech():
    text = request.args.get('text', '').strip()
    engine = request.args.get('engine', 'gtts')

    if not text:
        return jsonify(error='Missing text parameter'), 400

    if engine == 'elevenlabs' and not ELEVENLABS_API_KEY:
        return jsonify(error='ElevenLabs API key not configured'), 500

    prefix = 'el' if engine == 'elevenlabs' else 'gt'
    cache_key = hashlib.md5(text.lower().encode()).hexdigest()
    cache_path = os.path.join(AUDIO_CACHE_DIR, f'{prefix}_{cache_key}.mp3')

    if not os.path.exists(cache_path):
        if engine == 'elevenlabs':
            generate_with_elevenlabs(text, cache_path)
        else:
            generate_with_gtts(text, cache_path)

    return send_file(cache_path, mimetype='audio/mpeg')


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/image/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files and 'file' not in request.files:
        return jsonify(error='No image in request'), 400

    file = request.files.get('image') or request.files.get('file')
    if not file or file.filename == '':
        return jsonify(error='No file selected'), 400

    if not _allowed_file(file.filename):
        return jsonify(error='Invalid file type'), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    save_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    try:
        file.save(save_path)
        result = {'path': save_path}

        # 1. OCR the image
        ocr_text = perform_ocr(save_path)
        print(f"[upload_image] OCR text: {ocr_text}")

        # 2. Get actionable English summary via Gemini
        gemini_response = call_gemini(ocr_text, SYSTEM_PROMOPT_ENGLISH)
        english_summary = ''
        if gemini_response:
            try:
                english_summary = (gemini_response.text or '').strip()
            except (ValueError, AttributeError):
                # .text can raise when response blocked or has no valid Part
                candidates = getattr(gemini_response, 'candidates', []) or []
                if candidates:
                    content = getattr(candidates[0], 'content', None)
                    if content:
                        parts = getattr(content, 'parts', []) or []
                        if parts:
                            english_summary = (getattr(parts[0], 'text', '') or '').strip()

        # 3. Translate to Rohingya
        rohingya = translate_to_rohingya(english_summary)

        result['text'] = english_summary
        result['rohingya'] = rohingya

        return jsonify(ok=True, result=result)
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
