#!/usr/bin/env python3
"""Layer 2: Melodic elements - warm chimes, gentle bells, cozy tones."""

import numpy as np
from scipy.io import wavfile

def chime(t, freq, harmonics=[1, 2, 3, 4]):
    """Generate a warm wind chime sound."""
    sound = np.zeros_like(t)
    for i, h in enumerate(harmonics):
        amp = 1.0 / (i + 1.5)  # Softer harmonic decay
        sound += amp * np.sin(2 * np.pi * freq * h * t)
    return sound

def generate_melody_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Gentle wind chimes - warm pentatonic scale
    chime_times = [0.5, 2.0, 4.5, 6.5, 9.0, 11.0]
    chime_freqs = [523, 587, 659, 784, 880, 659]  # C5, D5, E5, G5, A5, E5 - major pentatonic

    for chime_time, chime_freq in zip(chime_times, chime_freqs):
        start = int(chime_time * sample_rate)
        dur = int(2.0 * sample_rate)
        if start + dur < len(audio):
            chime_t = np.linspace(0, 2.0, dur)
            chime_sound = chime(chime_t, chime_freq)
            chime_env = np.exp(-chime_t * 1.5)  # Gentle decay
            audio[start:start + dur] += chime_sound * chime_env * 0.12

    # Warm piano-like tones (gentle arpeggios)
    piano_notes = [
        (1.0, 262),   # C4
        (3.0, 330),   # E4
        (5.0, 392),   # G4
        (7.0, 330),   # E4
        (9.5, 262),   # C4
    ]

    for note_time, freq in piano_notes:
        start = int(note_time * sample_rate)
        dur = int(1.5 * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, 1.5, dur)
            # Warm, rounded tone
            note_sound = (
                0.5 * np.sin(2 * np.pi * freq * note_t) +
                0.3 * np.sin(2 * np.pi * freq * 2 * note_t) +
                0.1 * np.sin(2 * np.pi * freq * 3 * note_t)
            )
            # Soft attack, gentle decay
            attack = np.minimum(note_t * 10, 1)
            decay = np.exp(-note_t * 2)
            note_env = attack * decay
            audio[start:start + dur] += note_sound * note_env * 0.15

    # Gentle string pad swells
    pad_times = [(2.0, 4.0), (7.0, 9.0)]
    for start_time, end_time in pad_times:
        start = int(start_time * sample_rate)
        dur = int((end_time - start_time) * sample_rate)
        if start + dur < len(audio):
            pad_t = np.linspace(0, end_time - start_time, dur)
            # Warm major chord
            pad_sound = (
                0.3 * np.sin(2 * np.pi * 220 * pad_t) +  # A3
                0.25 * np.sin(2 * np.pi * 277 * pad_t) +  # C#4
                0.2 * np.sin(2 * np.pi * 330 * pad_t)    # E4
            )
            # Swell envelope
            sweep_progress = pad_t / (end_time - start_time)
            pad_env = np.sin(np.pi * sweep_progress) ** 2
            audio[start:start + dur] += pad_sound * pad_env * 0.1

    return audio

if __name__ == "__main__":
    audio = generate_melody_layer()
    wavfile.write('melody_layer.wav', 44100, (audio / np.max(np.abs(audio)) * 0.8 * 32767).astype(np.int16))
    print("Warm melody layer created")
