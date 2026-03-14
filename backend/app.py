import os
import hashlib

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from gtts import gTTS

load_dotenv()

app = Flask(__name__)
CORS(app)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

AUDIO_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'audio_cache')
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
