#!/usr/bin/env python3
"""Layer 2: Warm, gentle melody - like a lullaby or folk song."""

import numpy as np
from scipy.io import wavfile

def warm_tone(t, freq):
    """Generate a warm, round tone (like a soft flute or warm synth)."""
    # Fundamental with gentle, warm harmonics
    sound = np.sin(2 * np.pi * freq * t)
    sound += 0.4 * np.sin(2 * np.pi * freq * 2 * t)
    sound += 0.15 * np.sin(2 * np.pi * freq * 3 * t)
    sound += 0.05 * np.sin(2 * np.pi * freq * 4 * t)
    return sound

def generate_melody_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Simple, warm folk-like melody in C major
    # Think "coming home" - warm and nostalgic
    notes = [
        (0.5, 392.00, 1.8),   # G4 - start
        (2.5, 440.00, 1.5),   # A4
        (4.5, 523.25, 2.0),   # C5 - home note
        (7.0, 493.88, 1.5),   # B4 - gentle tension
        (9.0, 440.00, 1.2),   # A4
        (10.5, 392.00, 1.5),  # G4 - resolve down
    ]

    for note_time, freq, note_dur in notes:
        start = int(note_time * sample_rate)
        dur = int(note_dur * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, note_dur, dur)
            note_sound = warm_tone(note_t, freq)

            # Very soft attack (0.3s), long sustain, gentle release (0.5s)
            envelope = np.ones_like(note_t)

            attack_time = 0.3
            attack_samples = int(attack_time * sample_rate)
            if attack_samples > 0:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples) ** 1.5

            release_time = 0.5
            release_samples = int(release_time * sample_rate)
            if release_samples > 0 and release_samples < len(envelope):
                envelope[-release_samples:] = np.linspace(1, 0, release_samples) ** 1.5

            audio[start:start + dur] += note_sound * envelope * 0.15

    # Add lower octave doubling for warmth (softer)
    lower_notes = [
        (0.5, 196.00, 1.8),   # G3
        (4.5, 261.63, 2.0),   # C4
        (9.0, 220.00, 1.2),   # A3
    ]

    for note_time, freq, note_dur in lower_notes:
        start = int(note_time * sample_rate)
        dur = int(note_dur * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, note_dur, dur)
            note_sound = warm_tone(note_t, freq)

            envelope = np.ones_like(note_t)
            attack_samples = int(0.4 * sample_rate)
            if attack_samples > 0:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples) ** 2
            release_samples = int(0.6 * sample_rate)
            if release_samples > 0 and release_samples < len(envelope):
                envelope[-release_samples:] = np.linspace(1, 0, release_samples) ** 2

            audio[start:start + dur] += note_sound * envelope * 0.1

    return audio

if __name__ == "__main__":
    audio = generate_melody_layer()
    audio = audio / np.max(np.abs(audio)) * 0.7
    wavfile.write('melody_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Warm melody layer created")
