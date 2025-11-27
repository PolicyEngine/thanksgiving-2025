#!/usr/bin/env python3
"""Master script: Mix all layers and combine with video."""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
import subprocess

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

# Apply high-pass filter to non-bass layers (remove everything <200Hz)
b_hp, a_hp = signal.butter(6, 200/(sr1/2), btype='high')
melody_filtered = signal.filtfilt(b_hp, a_hp, melody)
atmosphere_filtered = signal.filtfilt(b_hp, a_hp, atmosphere)
effects_filtered = signal.filtfilt(b_hp, a_hp, effects)

# Mix with balanced warmth - melody and atmosphere more prominent than Halloween
mixed = (
    0.70 * bass +              # Warm bass foundation
    0.25 * melody_filtered +   # Melodic chimes and piano
    0.20 * atmosphere_filtered + # Autumn atmosphere
    0.15 * effects_filtered    # Turkey and gathering sounds
)

# Apply soft compression to tame dynamic range
threshold = 0.3
ratio = 2.5
compressed = np.copy(mixed)
over_threshold = np.abs(compressed) > threshold
compressed[over_threshold] = np.sign(compressed[over_threshold]) * (
    threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio
)

# Master limiting
mixed = compressed / np.max(np.abs(compressed)) * 0.85

# Apply master fade for looping
fade_samples = int(2.0 * sr1)
fade_in = (np.linspace(0, 1, fade_samples)) ** 2
fade_out = (np.linspace(1, 0, fade_samples)) ** 2
mixed[:fade_samples] *= fade_in
mixed[-fade_samples:] *= fade_out

# Save mixed soundtrack
mixed_int16 = (mixed * 32767).astype(np.int16)
wavfile.write('thanksgiving-soundtrack-final.wav', sr1, mixed_int16)

size_mb = Path('thanksgiving-soundtrack-final.wav').stat().st_size / 1024 / 1024
print(f"Mixed soundtrack: {size_mb:.1f} MB")

# Convert to MP3 for web
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
        print("\nOpening video...")
        subprocess.run(['open', '-a', 'QuickTime Player', str(video_output)])
    else:
        print(f"Video combination error: {result.stderr}")
else:
    print(f"\nNote: Video file not found at {video_input}")
    print("To create the final video:")
    print("1. Record the animation from index.html (5-6 seconds)")
    print("2. Save as ~/Desktop/thanksgiving-policyengine-silent.mp4")
    print("3. Re-run this script")

print("\nDone! Happy Thanksgiving!")

# Cleanup intermediate files
print("\nCleaning up intermediate files...")
for f in ['bass_layer.wav', 'melody_layer.wav', 'atmosphere_layer.wav', 'effects_layer.wav']:
    Path(f).unlink(missing_ok=True)
print("Cleanup complete")
