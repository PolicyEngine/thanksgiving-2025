#!/usr/bin/env python3
"""Master script: Mix all layers into a warm, cozy Thanksgiving soundtrack."""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
import subprocess
import os

os.chdir(Path(__file__).parent)

# Generate all layers
print("Generating warm Thanksgiving soundtrack...")
venv_python = Path(__file__).parent / '.venv' / 'bin' / 'python3'
subprocess.run([str(venv_python), 'generate_bass_layer.py'], check=True)
subprocess.run([str(venv_python), 'generate_melody_layer.py'], check=True)
subprocess.run([str(venv_python), 'generate_atmosphere_layer.py'], check=True)
subprocess.run([str(venv_python), 'generate_effects_layer.py'], check=True)

print("\nMixing layers...")

# Load all layers
sr1, bass = wavfile.read('bass_layer.wav')
sr2, melody = wavfile.read('melody_layer.wav')
sr3, atmosphere = wavfile.read('atmosphere_layer.wav')
sr4, effects = wavfile.read('effects_layer.wav')

# Convert to float
bass = bass.astype(np.float32) / 32767
melody = melody.astype(np.float32) / 32767
atmosphere = atmosphere.astype(np.float32) / 32767
effects = effects.astype(np.float32) / 32767

# Boost bass warmth with gentle low-shelf
b_ls, a_ls = signal.butter(2, 300/(sr1/2), btype='low')
bass_warm = signal.filtfilt(b_ls, a_ls, bass) * 0.3 + bass * 0.7

# Mix - emphasize warmth (bass and atmosphere)
mixed = (
    0.40 * bass_warm +      # Strong warm bass foundation
    0.25 * melody +         # Gentle melody
    0.30 * atmosphere +     # Rich atmosphere
    0.12 * effects          # Light chime accents
)

# Gentle compression for smooth, cozy sound
threshold = 0.35
ratio = 2.0
compressed = np.copy(mixed)
over_threshold = np.abs(compressed) > threshold
compressed[over_threshold] = np.sign(compressed[over_threshold]) * (
    threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio
)

# Gentle high-cut for warmth (remove any harshness)
b_lp, a_lp = signal.butter(2, 8000/(sr1/2), btype='low')
mixed = signal.filtfilt(b_lp, a_lp, compressed)

# Normalize
mixed = mixed / np.max(np.abs(mixed)) * 0.78

# Smooth fade in/out for looping
fade_samples = int(2.0 * sr1)
fade_in = np.linspace(0, 1, fade_samples) ** 2
fade_out = np.linspace(1, 0, fade_samples) ** 2
mixed[:fade_samples] *= fade_in
mixed[-fade_samples:] *= fade_out

# Save
mixed_int16 = (mixed * 32767).astype(np.int16)
wavfile.write('thanksgiving-soundtrack-final.wav', sr1, mixed_int16)

size_kb = Path('thanksgiving-soundtrack-final.wav').stat().st_size / 1024
print(f"Mixed soundtrack: {size_kb:.0f} KB")

# Convert to MP3
print("\nConverting to MP3...")
mp3_cmd = [
    'ffmpeg', '-y',
    '-i', 'thanksgiving-soundtrack-final.wav',
    '-codec:a', 'libmp3lame',
    '-b:a', '192k',
    'thanksgiving-soundtrack.mp3'
]
result = subprocess.run(mp3_cmd, capture_output=True, text=True)
if result.returncode == 0:
    mp3_size = Path('thanksgiving-soundtrack.mp3').stat().st_size / 1024
    print(f"MP3 created: {mp3_size:.0f} KB")

print("\nRunning quality tests...")
subprocess.run(['python3', 'test_soundtrack_quality.py'], check=False)

# Cleanup
for f in ['bass_layer.wav', 'melody_layer.wav', 'atmosphere_layer.wav', 'effects_layer.wav']:
    Path(f).unlink(missing_ok=True)

print("\nHappy Thanksgiving!")
