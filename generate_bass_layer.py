#!/usr/bin/env python3
"""Layer 1: Rich, warm bass foundation - like a cozy fireplace."""

import numpy as np
from scipy.io import wavfile

def generate_bass_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Strong warm bass foundation (80-250Hz range)
    # C2 and G2 - perfect fifth for richness
    bass_freqs = [65.41, 98.00]  # C2, G2

    for freq in bass_freqs:
        # Rich bass with warm harmonics
        audio += 0.4 * np.sin(2 * np.pi * freq * t)
        audio += 0.25 * np.sin(2 * np.pi * freq * 2 * t)  # Octave
        audio += 0.1 * np.sin(2 * np.pi * freq * 3 * t)   # Fifth above octave

    # Add warm body frequencies (200-400Hz)
    body_freqs = [130.81, 196.00, 261.63]  # C3, G3, C4
    for freq in body_freqs:
        audio += 0.15 * np.sin(2 * np.pi * freq * t)

    # Very slow, gentle breathing swell
    swell = 0.85 + 0.15 * np.sin(2 * np.pi * 0.05 * t)
    audio *= swell

    # Soft fade in
    fade_in = np.minimum(t / 2.0, 1.0)
    audio *= fade_in

    return audio

if __name__ == "__main__":
    audio = generate_bass_layer()
    audio = audio / np.max(np.abs(audio)) * 0.75
    wavfile.write('bass_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Rich warm bass layer created")
