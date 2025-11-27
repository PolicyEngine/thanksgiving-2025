#!/usr/bin/env python3
"""Layer 3: Soft ambient texture - very subtle warmth."""

import numpy as np
from scipy.io import wavfile
from scipy import signal

def generate_atmosphere_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Soft, warm chord pad that slowly evolves
    # F major 7 - very warm and pleasant
    freqs = [174.61, 220.00, 261.63, 329.63]  # F3, A3, C4, E4

    for i, freq in enumerate(freqs):
        # Each note enters slightly delayed for a gentle build
        delay = i * 0.3
        delay_samples = int(delay * sample_rate)

        tone_length = len(t) - delay_samples
        tone_t = np.linspace(0, duration - delay, tone_length)

        tone = 0.08 * np.sin(2 * np.pi * freq * tone_t)

        # Very gentle fade in
        fade_in = np.minimum(tone_t / 2.0, 1.0)
        tone *= fade_in

        audio[delay_samples:] += tone

    # Add very subtle shimmer (high, soft)
    shimmer_freq = 1318.51  # E6 - high and delicate
    shimmer = 0.02 * np.sin(2 * np.pi * shimmer_freq * t)
    shimmer *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t)  # Gentle pulsing
    audio += shimmer

    return audio

if __name__ == "__main__":
    audio = generate_atmosphere_layer()
    audio = audio / np.max(np.abs(audio)) * 0.6
    wavfile.write('atmosphere_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Soft atmosphere layer created")
