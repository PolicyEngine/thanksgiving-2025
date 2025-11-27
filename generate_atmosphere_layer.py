#!/usr/bin/env python3
"""Layer 3: Rich, warm pad atmosphere - like being wrapped in a blanket."""

import numpy as np
from scipy.io import wavfile

def generate_atmosphere_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Warm, rich chord pad - C major with added 9th for warmth
    # This creates a "golden" sound
    chord_freqs = [
        (130.81, 0.3),   # C3 - root (warm bass)
        (164.81, 0.25),  # E3 - major third
        (196.00, 0.25),  # G3 - fifth
        (293.66, 0.15),  # D4 - added 9th (warmth)
        (261.63, 0.2),   # C4 - octave
        (329.63, 0.1),   # E4 - higher third
    ]

    for freq, amp in chord_freqs:
        # Each note with soft harmonics
        tone = amp * np.sin(2 * np.pi * freq * t)
        tone += amp * 0.3 * np.sin(2 * np.pi * freq * 2 * t)

        # Very slow fade in (3 seconds)
        fade_in = np.minimum(t / 3.0, 1.0) ** 1.5
        tone *= fade_in

        audio += tone

    # Add subtle warmth in the 200-400Hz range
    warmth_freq = 220  # A3
    warmth = 0.1 * np.sin(2 * np.pi * warmth_freq * t)
    warmth += 0.05 * np.sin(2 * np.pi * warmth_freq * 1.5 * t)  # E4 (fifth)

    # Gentle pulsing
    warmth *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * t)
    audio += warmth

    # Very gentle high shimmer (like distant warmth)
    shimmer = 0.02 * np.sin(2 * np.pi * 880 * t)  # A5
    shimmer *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
    # Fade shimmer in slowly
    shimmer *= np.minimum(t / 4.0, 1.0)
    audio += shimmer

    return audio

if __name__ == "__main__":
    audio = generate_atmosphere_layer()
    audio = audio / np.max(np.abs(audio)) * 0.7
    wavfile.write('atmosphere_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Rich warm atmosphere created")
