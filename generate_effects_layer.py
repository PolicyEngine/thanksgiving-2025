#!/usr/bin/env python3
"""Layer 4: Gentle accents - soft chimes like wind through autumn trees."""

import numpy as np
from scipy.io import wavfile

def soft_chime(duration, sample_rate, freq):
    """Generate a soft, warm chime."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Soft bell-like tone with warm harmonics
    chime = np.sin(2 * np.pi * freq * t)
    chime += 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    chime += 0.2 * np.sin(2 * np.pi * freq * 3 * t)
    chime += 0.1 * np.sin(2 * np.pi * freq * 4 * t)

    # Soft attack (not sharp), gentle decay
    attack = 1 - np.exp(-t * 8)  # Soft attack
    decay = np.exp(-t * 1.2)      # Long, gentle decay
    envelope = attack * decay

    return chime * envelope

def generate_effects_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Soft, warm chimes - pentatonic for pleasant sound
    # Like gentle wind chimes on a porch
    chimes = [
        (1.5, 523.25, 1.2),   # C5
        (3.5, 659.25, 1.0),   # E5
        (6.0, 783.99, 1.2),   # G5
        (8.5, 880.00, 1.0),   # A5
        (10.5, 523.25, 1.5),  # C5 (return home)
    ]

    for chime_time, freq, chime_dur in chimes:
        start = int(chime_time * sample_rate)
        chime_samples = int(chime_dur * sample_rate)
        if start + chime_samples < len(audio):
            chime = soft_chime(chime_dur, sample_rate, freq)
            audio[start:start + chime_samples] += chime * 0.06

    # Add a low, warm "ding" at key moments (like a grandfather clock)
    warm_dings = [
        (0.2, 261.63, 2.0),   # C4 - opening
        (5.5, 196.00, 2.0),   # G3 - midpoint
        (11.0, 261.63, 2.0),  # C4 - closing
    ]

    for ding_time, freq, ding_dur in warm_dings:
        start = int(ding_time * sample_rate)
        ding_samples = int(ding_dur * sample_rate)
        if start + ding_samples < len(audio):
            ding = soft_chime(ding_dur, sample_rate, freq)
            # Add lower octave for warmth
            ding_t = np.linspace(0, ding_dur, ding_samples)
            ding += 0.5 * soft_chime(ding_dur, sample_rate, freq/2)
            audio[start:start + ding_samples] += ding * 0.05

    return audio

if __name__ == "__main__":
    audio = generate_effects_layer()
    audio = audio / np.max(np.abs(audio)) * 0.6
    wavfile.write('effects_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Warm chimes layer created")
