#!/usr/bin/env python3
"""Cut the pauses out of a talking-head video (jump cuts), keeping a natural breath between lines.

usage: python trim.py input.mp4 output.mp4 [--gap 0.4] [--keep 0.16] [--speed 1.0] [--dry]

  --gap    only pauses longer than this are cut (seconds)
  --keep   how much of each cut pause is kept, so it doesn't sound breathless (seconds)
  --speed  1.0 keeps your normal pace; 1.1 speeds the result up a little
  --dry    just print what would be cut

Saves output.cuts.json with the parts that were kept, and prints how much time was saved.
"""
import argparse, json, os, subprocess, sys

import numpy as np

SR = 16000
WIN = 0.02  # analysis window (seconds)


def load_audio(src):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def runs(b):
    d = np.diff(np.concatenate([[0], b.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def speech(a, below=30.0):
    """True for each 20 ms window that sounds like speech (within `below` dB of the loud parts)."""
    w = int(SR * WIN); n = len(a) // w
    lvl = 20 * np.log10(np.sqrt((a[:n * w].reshape(n, w).astype(np.float64) ** 2).mean(1) + 1e-12))
    loud = lvl > max(np.percentile(lvl, 95) - below, -55.0)
    for s, e in runs(~loud):          # fill tiny dips inside words
        if (e - s) * WIN < 0.08: loud[s:e] = True
    for s, e in runs(loud):           # drop isolated clicks
        if (e - s) * WIN < 0.06: loud[s:e] = False
    return loud


def keep_parts(loud, dur, gap=0.4, keep=0.16):
    cuts = []
    for s, e in runs(~loud):
        ts, te = s * WIN, min(dur, e * WIN)
        if s == 0: cuts.append((0.0, max(0.0, te - keep * 0.6)))
        elif e >= len(loud) - 1: cuts.append((min(dur, ts + keep * 0.6), dur))
        elif te - ts >= gap: cuts.append((ts + keep * 0.45, te - keep * 0.55))
    parts, t = [], 0.0
    for a, b in cuts:
        if a > t + 0.05: parts.append((t, a))
        t = max(t, b)
    if dur > t + 0.05: parts.append((t, dur))
    return parts or [(0.0, dur)]


def probe(src):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,r_frame_rate:format=duration',
                                   '-of', 'json', src], capture_output=True, text=True, check=True).stdout)
    v = [s for s in j['streams'] if s.get('codec_type') == 'video'][0]; num, den = v['r_frame_rate'].split('/')
    return min(float(num) / float(den or 1), 30.0), float(j['format']['duration']), any(s.get('codec_type') == 'audio' for s in j['streams'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src'); ap.add_argument('dst', nargs='?')
    ap.add_argument('--gap', type=float, default=0.4); ap.add_argument('--keep', type=float, default=0.16)
    ap.add_argument('--speed', type=float, default=1.0); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    fps, dur, has_audio = probe(a.src)
    if not has_audio: sys.exit('This video has no sound, so there are no pauses to find.')
    fps_txt = f'{fps:.3f}'.rstrip('0').rstrip('.')
    snap = lambda t: round(t * fps) / fps   # cut on whole frames so sound and picture stay in sync
    parts = [(snap(s), snap(e)) for s, e in keep_parts(speech(load_audio(a.src)), dur, a.gap, a.keep)]
    parts = [(s, e) for s, e in parts if e - s >= 1 / fps]
    new = sum(e - s for s, e in parts) / a.speed
    print(f'Keeping {len(parts)} parts: {dur:.1f}s -> {new:.1f}s ({dur - new:.1f}s of pauses removed)')
    if a.dry or not a.dst:
        for s, e in parts: print(f'  keep {s:7.2f} - {e:7.2f}')
        return
    sel = '+'.join(f'gte(t,{s:.4f})*lt(t,{e:.4f})' for s, e in parts)
    vf = f"[0:v]fps={fps_txt},select='{sel}',setpts=N/FRAME_RATE/TB"
    af = f"[0:a]aselect='{sel}',asetpts=N/SR/TB"
    if abs(a.speed - 1) > 1e-3: vf += f',setpts=PTS/{a.speed}'; af += f',atempo={a.speed}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.src, '-filter_complex', f'{vf}[v];{af}[a]', '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', a.dst], check=True)
    json.dump({'source': os.path.basename(a.src), 'speed': a.speed, 'kept': parts}, open(os.path.splitext(a.dst)[0] + '.cuts.json', 'w'), indent=1)
    print('Done:', a.dst)


if __name__ == '__main__':
    main()
