#!/usr/bin/env python3
"""Layer 2: Gentle, warm melody - soft piano-like tones."""

import numpy as np
from scipy.io import wavfile

def soft_tone(t, freq):
    """Generate a soft, warm tone."""
    # Pure sine with very gentle harmonics
    sound = np.sin(2 * np.pi * freq * t)
    sound += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    sound += 0.1 * np.sin(2 * np.pi * freq * 3 * t)
    return sound

def generate_melody_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Simple, gentle ascending melody (C major pentatonic - always pleasant)
    # Spaced out notes, very soft
    notes = [
        (0.5, 523.25, 1.5),   # C5
        (2.5, 587.33, 1.5),   # D5
        (5.0, 659.25, 1.5),   # E5
        (7.5, 783.99, 1.5),   # G5
        (10.0, 523.25, 1.8),  # C5 (resolve)
    ]

    for note_time, freq, note_dur in notes:
        start = int(note_time * sample_rate)
        dur = int(note_dur * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, note_dur, dur)
            note_sound = soft_tone(note_t, freq)

            # Soft attack, long sustain, gentle release
            attack_time = 0.1
            release_time = 0.5
            envelope = np.ones_like(note_t)

            # Attack
            attack_samples = int(attack_time * sample_rate)
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

            # Release
            release_samples = int(release_time * sample_rate)
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)

            audio[start:start + dur] += note_sound * envelope * 0.12

    return audio

if __name__ == "__main__":
    audio = generate_melody_layer()
    audio = audio / np.max(np.abs(audio)) * 0.7
    wavfile.write('melody_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Gentle melody layer created")
