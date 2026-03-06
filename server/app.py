import os
import io
import base64
import numpy as np
import soundfile as sf
import librosa
from flask import Flask, request, jsonify
from flask_cors import CORS
from chord_detector import analyze_chunk, analyze_file

app = Flask(__name__)
CORS(app, origins="*")

# ── Health check ──────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'See Harmony Chord API'})


# ── Real-time chunk endpoint ───────────────────────────────────────
# POST /chord
# Body (JSON): { "audio": "<base64 WAV or raw float32>", "sr": 44100, "format": "wav"|"f32" }
# Returns:     { "chord": "Cmaj7", "confidence": 0.87, "chroma": [...] }
@app.route('/chord', methods=['POST'])
def chord():
    try:
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
            # raw float32 PCM
            audio = np.frombuffer(raw, dtype='<f4').copy()
            sr    = sr_in

        # Resample to 22050 for consistency
        if sr != 22050:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=22050)
            sr = 22050

        result = analyze_chunk(audio, sr)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'chord': '', 'confidence': 0.0}), 200


# ── Full file analysis endpoint ────────────────────────────────────
# POST /analyze
# Body (multipart): file=<audio file>
#   OR (JSON):      { "audio": "<base64>", "sr": 44100, "format": "wav" }
# Returns: { "key": "C maj", "timeline": [{t, chord},...], "duration": 275.3 }
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
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

        result = analyze_file(audio, sr)
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
