#!/usr/bin/env python3
"""
seraphim_batch_wav.py
=====================
Seraphim LQG Framework — Batch GW Chirp Audio Generator
lis10inc · github.com/groksgalaxynet/Seraphim-LQG

Generates one .wav file per event from GWOSC posterior medians.
Each WAV is a post-Newtonian inspiral chirp + ringdown derived
from the measured chirp mass, total mass, and ISCO frequency.

No external audio libraries needed — pure numpy + stdlib struct.

Usage
-----
  python3 seraphim_batch_wav.py                        # uses seraphim_gap_v3_results.csv
  python3 seraphim_batch_wav.py --csv path/to/file.csv
  python3 seraphim_batch_wav.py --dur 3.0 --rd 0.6    # longer sounds
  python3 seraphim_batch_wav.py --pitch true            # true GW frequencies (may be inaudible)
  python3 seraphim_batch_wav.py --target 440            # tune ISCO to 440 Hz (A4)
  python3 seraphim_batch_wav.py --event GW150914        # single event only
  python3 seraphim_batch_wav.py --zip                   # pack all WAVs into a zip

Output
------
  ./gw_samples/
      seraphim_GW150914_095045_n5.340_Mc27.7_pitched.wav
      seraphim_GW190814_211039_n4.189_Mc6.1_pitched.wav
      ... (175 files)
      seraphim_sample_index.csv    -- metadata for every file
"""

import os
import sys
import csv
import math
import struct
import argparse
import zipfile
import time
from pathlib import Path

try:
    import numpy as np
    NUMPY = True
except ImportError:
    NUMPY = False
    print("[WARN] numpy not found — falling back to pure Python (slower ~15s total)")

# ================================================================
# CONSTANTS
# ================================================================
G    = 6.674e-11   # m^3 kg^-1 s^-2
C    = 3.0e8       # m/s
PI   = math.pi
MSUN = 1.989e30    # kg
SR   = 44100       # audio sample rate (Hz)

# ================================================================
# PN PHYSICS
# ================================================================
def f_isco(Mt_msun):
    """ISCO frequency in Hz for total mass Mt (solar masses)."""
    Mt_kg = Mt_msun * MSUN
    return C**3 / (6 * math.sqrt(6) * PI * G * Mt_kg)


def pn_freq_scalar(tau, Mc_kg):
    """Leading-order PN GW frequency at time-to-merger tau (seconds)."""
    if tau <= 1e-7:
        return float('inf')
    return (1/PI) * (5/(256*tau))**(3/8) * (C**3/(G*Mc_kg))**(5/8)


# ================================================================
# AUDIO GENERATION — NUMPY PATH (fast)
# ================================================================
def generate_numpy(Mc_msun, Mt_msun, dur_s, rd_s, pitch_target_hz, volume=0.85):
    """
    Generate PCM float32 buffer using numpy vectorised PN integration.

    Parameters
    ----------
    Mc_msun        : chirp mass in solar masses
    Mt_msun        : total mass in solar masses
    dur_s          : inspiral duration in seconds (audio)
    rd_s           : ringdown duration in seconds
    pitch_target_hz: f_ISCO will be shifted to this frequency (800 Hz default)
                     set to 0 to use true GW frequencies
    volume         : peak amplitude 0..1

    Returns
    -------
    buf            : float32 numpy array, values in [-1, 1]
    f_gw_track     : float32 array of true GW frequencies per sample
    f_isco_true    : true ISCO frequency in Hz
    pitch_factor   : applied pitch shift
    """
    Mc_kg = Mc_msun * MSUN
    f_isco_true = f_isco(Mt_msun)
    f_qnm = f_isco_true * 0.95            # dominant QNM ~ 0.95 * f_ISCO

    pf = (pitch_target_hz / f_isco_true) if pitch_target_hz > 0 else 1.0

    n_ins = int(dur_s * SR)
    n_rd  = int(rd_s  * SR)

    # --- Inspiral ---
    t    = np.linspace(-dur_s, 0.0, n_ins, endpoint=False)
    tau  = np.maximum(-t, 1e-7)
    f_gw = np.minimum(
        (1/PI) * (5/(256*tau))**(3/8) * (C**3/(G*Mc_kg))**(5/8),
        f_isco_true
    )
    f_audio  = f_gw * pf
    phi_ins  = np.cumsum(2*PI * f_audio / SR)
    env      = np.minimum((tau / dur_s)**(-0.25), 10.0)
    ins_buf  = env * np.cos(phi_ins)

    # --- Ringdown ---
    rd_t     = np.arange(n_rd, dtype=np.float64) / SR
    phi_last = float(phi_ins[-1])
    phi_rd   = phi_last + np.cumsum(np.full(n_rd, 2*PI * f_qnm * pf / SR))
    rd_buf   = np.exp(-rd_t / rd_s) * np.cos(phi_rd)

    # Combine
    buf  = np.concatenate([ins_buf, rd_buf]).astype(np.float64)
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf = buf / peak * volume

    # Fade in (5 ms) and fade out (20 ms)
    fi = int(0.005 * SR)
    fo = int(0.020 * SR)
    if fi > 0:
        buf[:fi]  *= np.linspace(0.0, 1.0, fi)
    if fo > 0:
        buf[-fo:] *= np.linspace(1.0, 0.0, fo)

    f_gw_track = np.concatenate([f_gw, np.full(n_rd, f_qnm)])
    return buf.astype(np.float32), f_gw_track.astype(np.float32), f_isco_true, pf


# ================================================================
# AUDIO GENERATION — PURE PYTHON FALLBACK (slow but no deps)
# ================================================================
def generate_python(Mc_msun, Mt_msun, dur_s, rd_s, pitch_target_hz, volume=0.85):
    Mc_kg = Mc_msun * MSUN
    f_isco_true = f_isco(Mt_msun)
    f_qnm = f_isco_true * 0.95
    pf = (pitch_target_hz / f_isco_true) if pitch_target_hz > 0 else 1.0

    n_ins = int(dur_s * SR)
    n_rd  = int(rd_s  * SR)
    n_total = n_ins + n_rd

    buf = [0.0] * n_total
    phi = 0.0

    for i in range(n_ins):
        t   = -dur_s + i / SR
        tau = max(-t, 1e-7)
        f_gw = min(pn_freq_scalar(tau, Mc_kg), f_isco_true)
        phi += 2 * PI * f_gw * pf / SR
        env  = min((tau / dur_s) ** (-0.25), 10.0)
        buf[i] = env * math.cos(phi)

    for i in range(n_rd):
        rd_t = i / SR
        phi += 2 * PI * f_qnm * pf / SR
        buf[n_ins + i] = math.exp(-rd_t / rd_s) * math.cos(phi)

    peak = max(abs(x) for x in buf) or 1.0
    buf  = [x / peak * volume for x in buf]

    fi = int(0.005 * SR)
    fo = int(0.020 * SR)
    for i in range(fi):
        buf[i] *= i / fi
    for i in range(fo):
        buf[n_total - 1 - i] *= i / fo

    return buf, None, f_isco_true, pf


def generate_audio(Mc_msun, Mt_msun, dur_s, rd_s, pitch_target_hz, volume=0.85):
    if NUMPY:
        return generate_numpy(Mc_msun, Mt_msun, dur_s, rd_s, pitch_target_hz, volume)
    else:
        return generate_python(Mc_msun, Mt_msun, dur_s, rd_s, pitch_target_hz, volume)


# ================================================================
# WAV WRITER
# ================================================================
def buf_to_wav_bytes(buf):
    """
    Convert float buffer (values in [-1, 1]) to 16-bit mono WAV bytes.
    Returns raw bytes ready to write to a .wav file.
    """
    if NUMPY:
        pcm = (np.clip(buf, -1.0, 1.0) * 32767).astype(np.int16)
        pcm_bytes = pcm.tobytes()
    else:
        pcm_bytes = b''.join(
            struct.pack('<h', max(-32767, min(32767, int(s * 32767))))
            for s in buf
        )

    n_samples  = len(pcm_bytes) // 2
    data_size  = n_samples * 2       # 16-bit mono
    file_size  = 36 + data_size

    header = struct.pack(
        '<4sI4s'      # RIFF....WAVE
        '4sIHHIIHH'   # fmt  chunk
        '4sI',        # data chunk header
        b'RIFF', file_size, b'WAVE',
        b'fmt ', 16,
        1,            # PCM
        1,            # mono
        SR,           # sample rate
        SR * 2,       # byte rate
        2,            # block align
        16,           # bits per sample
        b'data', data_size
    )
    return header + pcm_bytes


def write_wav(path, buf):
    wav = buf_to_wav_bytes(buf)
    with open(path, 'wb') as f:
        f.write(wav)
    return len(wav)


# ================================================================
# FILENAME BUILDER
# ================================================================
def make_filename(event_id, n_obs, Mc, catalog, pitched, pitch_hz):
    """
    seraphim_GW150914_095045_n5.340_Mc27.7_pitched.wav
    seraphim_GW200115_042309_n4.741_Mc2.4_true.wav
    """
    safe = event_id.replace(' ', '_')
    n_str  = f"n{n_obs:.3f}"
    mc_str = f"Mc{Mc:.1f}"
    mode   = "pitched" if pitched else "true"
    return f"seraphim_{safe}_{n_str}_{mc_str}_{mode}.wav"


# ================================================================
# LOAD EVENTS FROM CSV
# ================================================================
def load_events(csv_path, event_filter=None):
    """
    Load unique events from seraphim_gap_v3_results.csv.
    Returns list of dicts with all needed fields.
    Deduplicates by event name (keeps first occurrence).
    """
    events = {}
    with open(csv_path, newline='') as f:
        for row in csv.DictReader(f):
            key = row['event']
            if key in events:
                continue
            if event_filter and event_filter not in key:
                continue
            try:
                Mt = float(row['M_total_Msun'])
                Mc = float(row['M_chirp_Msun'])
                q  = float(row['mass_ratio'])
                n  = float(row['n_seraphim'])
            except (ValueError, KeyError):
                continue
            eta    = q / (1+q)**2
            m1     = Mt / (1+q)
            m2     = Mt * q / (1+q)
            fi     = f_isco(Mt)
            n_theory = 3.561 + 7.012 * eta

            events[key] = {
                'event'    : key,
                'catalog'  : row.get('catalog', '?'),
                'Mc'       : Mc,
                'Mt'       : Mt,
                'm1'       : m1,
                'm2'       : m2,
                'q'        : q,
                'eta'      : eta,
                'n_obs'    : n,
                'n_theory' : n_theory,
                'chi_eff'  : float(row.get('chi_eff', 0)),
                'z'        : float(row.get('redshift', 0)),
                'f_isco'   : fi,
            }
    return list(events.values())


# ================================================================
# MAIN
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description='Seraphim Batch WAV Builder — GW chirps from posterior medians'
    )
    parser.add_argument('--csv',    default=None,
                        help='Path to seraphim_gap_v3_results.csv (auto-detects if not given)')
    parser.add_argument('--out',    default='gw_samples',
                        help='Output directory (default: ./gw_samples)')
    parser.add_argument('--dur',    type=float, default=2.0,
                        help='Inspiral duration in seconds (default: 2.0)')
    parser.add_argument('--rd',     type=float, default=0.4,
                        help='Ringdown duration in seconds (default: 0.4)')
    parser.add_argument('--pitch',  default='pitched',
                        choices=['pitched','true'],
                        help='"pitched": shift f_ISCO to --target Hz. "true": raw GW frequencies')
    parser.add_argument('--target', type=float, default=800.0,
                        help='Pitch target frequency in Hz (default: 800)')
    parser.add_argument('--volume', type=float, default=0.85,
                        help='Peak amplitude 0..1 (default: 0.85)')
    parser.add_argument('--event',  default=None,
                        help='Generate single event only (partial match, e.g. GW150914)')
    parser.add_argument('--zip',    action='store_true',
                        help='Pack all WAVs into seraphim_gw_samples.zip after generation')
    parser.add_argument('--note',   action='store_true',
                        help='Map events to nearest musical note (prints mapping)')
    args = parser.parse_args()

    # --- Find CSV ---
    if args.csv:
        csv_path = args.csv
    else:
        candidates = [
            'seraphim_gap_v3_results.csv',
            '/mnt/project/seraphim_gap_v3_results.csv',
        ]
        # Also look in script directory and cwd
        script_dir = Path(__file__).parent
        candidates += [
            str(script_dir / 'seraphim_gap_v3_results.csv'),
        ]
        csv_path = None
        for c in candidates:
            if os.path.exists(c):
                csv_path = c
                break
        if not csv_path:
            print("[ERROR] Cannot find seraphim_gap_v3_results.csv")
            print("        Place it next to this script or pass --csv /path/to/file.csv")
            sys.exit(1)

    print(f"[INFO] Loading events from: {csv_path}")
    events = load_events(csv_path, event_filter=args.event)
    if not events:
        print(f"[ERROR] No events found (filter='{args.event}')")
        sys.exit(1)
    print(f"[INFO] {len(events)} unique events loaded")

    # --- Output dir ---
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output directory: {out_dir.resolve()}")

    pitched   = args.pitch == 'pitched'
    pitch_hz  = args.target if pitched else 0.0

    # --- Optional: note mapping ---
    NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    def freq_to_note(f):
        if f <= 0: return '?'
        midi = 12 * math.log2(f / 440.0) + 69
        note_num = round(midi) % 12
        octave   = (round(midi)) // 12 - 1
        cents    = round((midi - round(midi)) * 100)
        sign     = '+' if cents >= 0 else ''
        return f"{NOTE_NAMES[note_num]}{octave} ({sign}{cents}¢)"

    # --- Index ---
    index_rows = []

    # --- Generation loop ---
    t_start = time.time()
    errors  = []

    for i, ev in enumerate(events):
        label = f"[{i+1:3d}/{len(events)}]"
        try:
            buf, freq_track, f_isco_true, pf = generate_audio(
                ev['Mc'], ev['Mt'],
                args.dur, args.rd,
                pitch_hz, args.volume
            )

            fname  = make_filename(ev['event'], ev['n_obs'], ev['Mc'], ev['catalog'], pitched, pitch_hz)
            fpath  = out_dir / fname
            nbytes = write_wav(str(fpath), buf)

            f_audio_isco = f_isco_true * pf
            note_str     = freq_to_note(f_audio_isco) if pitched else freq_to_note(f_isco_true)

            index_rows.append({
                'filename'    : fname,
                'event'       : ev['event'],
                'catalog'     : ev['catalog'],
                'm1_msun'     : f"{ev['m1']:.4f}",
                'm2_msun'     : f"{ev['m2']:.4f}",
                'Mc_msun'     : f"{ev['Mc']:.4f}",
                'Mt_msun'     : f"{ev['Mt']:.4f}",
                'q'           : f"{ev['q']:.4f}",
                'eta'         : f"{ev['eta']:.5f}",
                'chi_eff'     : f"{ev['chi_eff']:.4f}",
                'z'           : f"{ev['z']:.4f}",
                'f_isco_hz'   : f"{f_isco_true:.2f}",
                'f_audio_hz'  : f"{f_audio_isco:.1f}",
                'pitch_factor': f"{pf:.2f}",
                'note'        : note_str,
                'n_obs'       : f"{ev['n_obs']:.5f}",
                'n_theory'    : f"{ev['n_theory']:.5f}",
                'delta_n'     : f"{ev['n_obs']-ev['n_theory']:.5f}",
                'dur_s'       : f"{args.dur:.2f}",
                'rd_s'        : f"{args.rd:.2f}",
                'wav_kb'      : f"{nbytes/1024:.1f}",
                'mode'        : 'pitched' if pitched else 'true',
            })

            note_disp = f"  {note_str}" if args.note else ''
            print(f"{label} {ev['event']:30s}  n={ev['n_obs']:.3f}  "
                  f"f_ISCO={f_isco_true:6.0f}Hz → {f_audio_isco:5.0f}Hz  "
                  f"{nbytes//1024:4d}KB{note_disp}")

        except Exception as e:
            print(f"{label} [ERROR] {ev['event']}: {e}")
            errors.append((ev['event'], str(e)))

    elapsed = time.time() - t_start

    # --- Write index CSV ---
    index_path = out_dir / 'seraphim_sample_index.csv'
    if index_rows:
        with open(str(index_path), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(index_rows[0].keys()))
            writer.writeheader()
            writer.writerows(index_rows)
        print(f"\n[INFO] Index written: {index_path}")

    # --- ZIP ---
    if args.zip and index_rows:
        zip_path = out_dir.parent / 'seraphim_gw_samples.zip'
        print(f"[INFO] Packing ZIP: {zip_path}")
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for row in index_rows:
                fp = out_dir / row['filename']
                if fp.exists():
                    zf.write(str(fp), arcname=row['filename'])
            zf.write(str(index_path), arcname='seraphim_sample_index.csv')
        zip_size = os.path.getsize(str(zip_path))
        print(f"[INFO] ZIP: {zip_path}  ({zip_size/1024/1024:.1f} MB)")

    # --- Summary ---
    total_kb = sum(float(r['wav_kb']) for r in index_rows)
    print(f"\n{'='*60}")
    print(f"Generated : {len(index_rows)}/{len(events)} events")
    print(f"Errors    : {len(errors)}")
    print(f"Total size: {total_kb/1024:.1f} MB")
    print(f"Time      : {elapsed:.1f}s  ({elapsed/max(len(index_rows),1)*1000:.0f}ms/event)")
    print(f"Output    : {out_dir.resolve()}/")
    if args.note:
        print(f"\nNote mapping (f_ISCO → nearest musical note):")
        for row in sorted(index_rows, key=lambda r: float(r['f_audio_hz'])):
            print(f"  {row['event']:30s}  {float(row['f_audio_hz']):6.1f} Hz  {row['note']}")
    if errors:
        print(f"\nErrors:")
        for ev_id, err in errors:
            print(f"  {ev_id}: {err}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
