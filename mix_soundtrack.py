#!/usr/bin/env python3
"""Master script: Mix all layers into a warm, pleasant soundtrack."""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
import subprocess
import os

os.chdir(Path(__file__).parent)

# Generate all layers
print("Generating warm soundtrack layers...")
subprocess.run(['python3', 'generate_bass_layer.py'], check=True)
subprocess.run(['python3', 'generate_melody_layer.py'], check=True)
subprocess.run(['python3', 'generate_atmosphere_layer.py'], check=True)
subprocess.run(['python3', 'generate_effects_layer.py'], check=True)

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

# Mix - balanced and warm
mixed = (
    0.35 * bass +         # Warm pad foundation
    0.30 * melody +       # Gentle melody
    0.25 * atmosphere +   # Soft ambience
    0.15 * effects        # Light chime accents
)

# Gentle compression
threshold = 0.4
ratio = 2.0
compressed = np.copy(mixed)
over_threshold = np.abs(compressed) > threshold
compressed[over_threshold] = np.sign(compressed[over_threshold]) * (
    threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio
)

# Normalize
mixed = compressed / np.max(np.abs(compressed)) * 0.75

# Smooth fade in/out for looping
fade_samples = int(1.5 * sr1)
fade_in = np.linspace(0, 1, fade_samples) ** 1.5
fade_out = np.linspace(1, 0, fade_samples) ** 1.5
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
else:
    print(f"MP3 conversion note: {result.stderr}")

# Combine with video if available
video_input = Path.home() / "Desktop" / "thanksgiving-policyengine-silent.mp4"
video_output = Path.home() / "Desktop" / "thanksgiving-policyengine-final.mp4"

if video_input.exists():
    print("\nCombining with video...")
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', str(video_input),
        '-i', 'thanksgiving-soundtrack-final.wav',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-shortest',
        str(video_output)
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = video_output.stat().st_size / 1024 / 1024
        print(f"Final video: {video_output}")
        print(f"File size: {size_mb:.1f} MB")
        subprocess.run(['open', '-a', 'QuickTime Player', str(video_output)])
    else:
        print(f"Video error: {result.stderr}")
else:
    print(f"\nTo create final video, save screen recording to:")
    print(f"  {video_input}")

print("\nHappy Thanksgiving!")

# Cleanup
for f in ['bass_layer.wav', 'melody_layer.wav', 'atmosphere_layer.wav', 'effects_layer.wav']:
    Path(f).unlink(missing_ok=True)
