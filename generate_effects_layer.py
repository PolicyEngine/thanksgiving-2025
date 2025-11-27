#!/usr/bin/env python3
"""Layer 4: Gentle chime accents - no creepy sounds!"""

import numpy as np
from scipy.io import wavfile

def gentle_chime(duration, sample_rate, freq):
    """Generate a soft, pleasant chime."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Pure, bell-like tone
    chime = np.sin(2 * np.pi * freq * t)
    chime += 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    chime += 0.25 * np.sin(2 * np.pi * freq * 3 * t)

    # Soft attack, long decay
    envelope = np.exp(-t * 1.5)
    attack = np.minimum(t * 20, 1.0)
    envelope *= attack

    return chime * envelope

def generate_effects_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Just a few soft, pleasant chimes
    chimes = [
        (1.0, 1046.50, 0.8),   # C6
        (4.0, 1318.51, 0.8),   # E6
        (8.0, 1567.98, 0.8),   # G6
        (11.0, 1046.50, 1.0),  # C6 (resolve)
    ]

    for chime_time, freq, chime_dur in chimes:
        start = int(chime_time * sample_rate)
        chime_samples = int(chime_dur * sample_rate)
        if start + chime_samples < len(audio):
            chime = gentle_chime(chime_dur, sample_rate, freq)
            audio[start:start + chime_samples] += chime * 0.08

    return audio

if __name__ == "__main__":
    audio = generate_effects_layer()
    audio = audio / np.max(np.abs(audio)) * 0.5
    wavfile.write('effects_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Gentle chimes layer created")
