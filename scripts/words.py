#!/usr/bin/env python3
"""Find when each word is said, so effects and captions land on the right word.

usage: python words.py input.mp4   -> prints "12.34  word" lines and saves input.words.json

Uses faster-whisper (installed into the skill's .venv on first run). On a Mac with mlx-whisper
installed, that is used instead. WHISPER_MODEL=base gives a faster, less accurate pass (default: small).
You can fix spellings in the saved .words.json by hand (e.g. "clot code" -> "Claude Code");
the effects script uses your edited file as long as it is newer than the video.
"""
import json, os, subprocess, sys

import numpy as np


def load_audio(src, sr=16000):
    """Decode the soundtrack to 16 kHz mono floats with ffmpeg (avoids PyAV quirks)."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def transcribe(src, model_name=None):
    model_name = model_name or os.environ.get('WHISPER_MODEL', 'small')
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(src, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True)
        return [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)}
                for seg in r['segments'] for w in seg.get('words', [])]
    except ImportError:
        pass
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print('Installing the transcriber (one time, about 1 minute)...', flush=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'faster-whisper'], check=True)
        from faster_whisper import WhisperModel
    print(f'Listening for words (whisper {model_name})...', flush=True)
    model = WhisperModel(model_name, device='cpu', compute_type='int8')
    segs, _ = model.transcribe(load_audio(src), word_timestamps=True, vad_filter=True)
    return [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or [])]


def words_path(src): return os.path.splitext(src)[0] + '.words.json'


def load_or_make(src):
    """Reuse <video>.words.json if it is newer than the video (so hand fixes stick), otherwise transcribe."""
    p = words_path(src)
    if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(src):
        return json.load(open(p))
    w = transcribe(src)
    json.dump(w, open(p, 'w'), indent=0)
    return w


if __name__ == '__main__':
    src = sys.argv[1]; out = words_path(src)
    words = transcribe(src)
    json.dump(words, open(out, 'w'), indent=0)
    for w in words: print(f"{w['s']:7.2f}  {w['w']}")
    print(f'\nSaved {len(words)} words to {out}')
