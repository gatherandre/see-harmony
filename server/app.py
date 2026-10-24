import os
import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024   # 40 MB per request

ENGINE_VERSION = 'v66.1'

# Lazy-load heavy modules to avoid OOM on Render free tier startup
_sf = None
_engine = None


def get_sf():
    global _sf
    if _sf is None:
        import soundfile
        _sf = soundfile
    return _sf


def get_engine():
    global _engine
    if _engine is None:
        import chord_engine
        _engine = chord_engine
    return _engine


def read_audio():
    """Audio from a multipart 'file' (any format soundfile reads), or JSON
    {'audio': base64, 'format': 'wav'|'f32', 'sr': int}. Returns (mono float32, sr)."""
    sf = get_sf()
    if request.files and 'file' in request.files:
        audio, sr = sf.read(io.BytesIO(request.files['file'].read()), dtype='float32', always_2d=False)
    else:
        data = request.get_json(force=True)
        raw = base64.b64decode(data['audio'])
        if data.get('format', 'wav') == 'wav':
            audio, sr = sf.read(io.BytesIO(raw), dtype='float32', always_2d=False)
        else:
            audio = np.frombuffer(raw, dtype='<f4').copy()
            sr = int(data.get('sr', 44100))
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    return audio, int(sr)


# ── Health check ──────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'See Harmony Chord API', 'engine': ENGINE_VERSION})


# ── Real-time window endpoint (microphone mode) ───────────────────
@app.route('/chord', methods=['POST'])
def chord():
    try:
        audio, sr = read_audio()
        result = get_engine().analyze_window(audio, sr)
        result['engine'] = ENGINE_VERSION
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'chord': '', 'confidence': 0.0}), 200


# ── Segment endpoint (file mode: the browser sends ~30 s segments) ─
@app.route('/segment', methods=['POST'])
def segment():
    try:
        audio, sr = read_audio()
        result = get_engine().analyze_segment(audio, sr)
        result['engine'] = ENGINE_VERSION
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── Whole-file endpoint ────────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        audio, sr = read_audio()
        result = get_engine().analyze_file(audio, sr)
        result['engine'] = ENGINE_VERSION
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
