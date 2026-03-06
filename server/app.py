import os
import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

# Lazy-load heavy modules to avoid OOM on Render free tier startup
_sf = None
_librosa = None
_detector = None

def get_sf():
    global _sf
    if _sf is None:
        import soundfile
        _sf = soundfile
    return _sf

def get_librosa():
    global _librosa
    if _librosa is None:
        import librosa
        _librosa = librosa
    return _librosa

def get_detector():
    global _detector
    if _detector is None:
        from chord_detector import analyze_chunk, analyze_file
        _detector = {'chunk': analyze_chunk, 'file': analyze_file}
    return _detector


# ── Health check ──────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'See Harmony Chord API'})


# ── Real-time chunk endpoint ───────────────────────────────────────
@app.route('/chord', methods=['POST'])
def chord():
    try:
        sf = get_sf()
        librosa = get_librosa()
        det = get_detector()

        data = request.get_json(force=True)
        fmt  = data.get('format', 'wav')
        sr_in = int(data.get('sr', 44100))

        raw = base64.b64decode(data['audio'])

        if fmt == 'wav':
            buf = io.BytesIO(raw)
            audio, sr = sf.read(buf, dtype='float32', always_2d=False)
            if audio.ndim == 2:
                audio = audio.mean(axis=1)
        else:
            audio = np.frombuffer(raw, dtype='<f4').copy()
            sr    = sr_in

        if sr != 22050:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=22050)
            sr = 22050

        result = det['chunk'](audio, sr)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'chord': '', 'confidence': 0.0}), 200


# ── Full file analysis endpoint ────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        sf = get_sf()
        librosa = get_librosa()
        det = get_detector()

        # Accept multipart file upload
        if request.files and 'file' in request.files:
            f = request.files['file']
            buf = io.BytesIO(f.read())
            audio, sr = sf.read(buf, dtype='float32', always_2d=False)
            if audio.ndim == 2:
                audio = audio.mean(axis=1)

        # Accept JSON base64
        elif request.is_json or request.data:
            data = request.get_json(force=True)
            fmt  = data.get('format', 'wav')
            sr_in = int(data.get('sr', 44100))
            raw  = base64.b64decode(data['audio'])

            if fmt == 'wav':
                buf = io.BytesIO(raw)
                audio, sr = sf.read(buf, dtype='float32', always_2d=False)
                if audio.ndim == 2:
                    audio = audio.mean(axis=1)
            else:
                audio = np.frombuffer(raw, dtype='<f4').copy()
                sr = sr_in
        else:
            return jsonify({'error': 'No audio provided'}), 400

        result = det['file'](audio, sr)
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
