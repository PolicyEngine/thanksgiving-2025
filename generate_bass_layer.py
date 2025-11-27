#!/usr/bin/env python3
"""Layer 1: Warm, gentle pad foundation."""

import numpy as np
from scipy.io import wavfile

def generate_bass_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Warm, soft pad chord (C major - very gentle)
    # Using higher frequencies for warmth, not deep bass
    freqs = [130.81, 164.81, 196.00]  # C3, E3, G3

    for freq in freqs:
        # Soft sine waves with gentle harmonics
        audio += 0.15 * np.sin(2 * np.pi * freq * t)
        audio += 0.05 * np.sin(2 * np.pi * freq * 2 * t)  # Soft overtone

    # Very slow, gentle volume swell
    swell = 0.8 + 0.2 * np.sin(2 * np.pi * 0.08 * t)
    audio *= swell

    return audio

if __name__ == "__main__":
    audio = generate_bass_layer()
    audio = audio / np.max(np.abs(audio)) * 0.7
    wavfile.write('bass_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Warm pad layer created")
