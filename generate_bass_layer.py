#!/usr/bin/env python3
"""Layer 1: Warm bass foundation - cozy fireplace crackle undertones."""

import numpy as np
from scipy.io import wavfile

def generate_bass_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Warm, cozy sub-bass drone (very gentle)
    base_freq = 55  # Low A - warm and inviting
    audio += 0.3 * np.sin(2 * np.pi * base_freq * t)

    # Add gentle harmonics for warmth
    audio += 0.15 * np.sin(2 * np.pi * base_freq * 2 * t)
    audio += 0.08 * np.sin(2 * np.pi * base_freq * 3 * t)

    # Slow, gentle pulsing like a heartbeat of warmth
    pulse = 0.15 * np.sin(2 * np.pi * 0.3 * t)  # Very slow pulse
    audio *= (1 + pulse)

    # Add subtle crackling texture (like distant fireplace)
    np.random.seed(42)
    crackle = np.random.randn(len(t)) * 0.02
    # Filter to make it more gentle
    from scipy import signal
    b, a = signal.butter(4, 200/(sample_rate/2), btype='low')
    crackle = signal.filtfilt(b, a, crackle)
    audio += crackle

    return audio

if __name__ == "__main__":
    audio = generate_bass_layer()
    wavfile.write('bass_layer.wav', 44100, (audio / np.max(np.abs(audio)) * 0.8 * 32767).astype(np.int16))
    print("Warm bass layer created")
