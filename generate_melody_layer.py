#!/usr/bin/env python3
"""Layer 2: Warm, human melody - with vibrato and expression."""

import numpy as np
from scipy.io import wavfile

def expressive_tone(t, freq, vibrato_rate=5.0, vibrato_depth=0.008):
    """Generate a warm tone with subtle vibrato for human feel."""
    # Add gentle vibrato (pitch modulation)
    vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    modulated_freq = freq * vibrato

    # Phase accumulation for smooth pitch changes
    phase = np.cumsum(2 * np.pi * modulated_freq / 44100)

    # Rich harmonics for warmth
    sound = np.sin(phase)                          # Fundamental
    sound += 0.35 * np.sin(phase * 2)              # Octave
    sound += 0.12 * np.sin(phase * 3)              # Fifth
    sound += 0.05 * np.sin(phase * 4)              # 2nd octave

    # Slight detuning for warmth (like a chorus effect)
    detune = 0.003
    sound += 0.15 * np.sin(phase * (1 + detune))
    sound += 0.15 * np.sin(phase * (1 - detune))

    return sound

def generate_melody_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Warm folk melody - overlapping notes for legato feel
    # G - A - C - B - A - G with expression
    notes = [
        (0.3, 392.00, 2.2, 0.70),   # G4 - gentle start
        (2.3, 440.00, 1.8, 0.65),   # A4 - stepping up
        (4.0, 523.25, 2.5, 0.80),   # C5 - home, emphasized
        (6.5, 493.88, 1.8, 0.60),   # B4 - gentle tension
        (8.2, 440.00, 1.5, 0.55),   # A4 - stepping down
        (9.8, 392.00, 2.2, 0.65),   # G4 - resolve
    ]

    for note_time, freq, note_dur, velocity in notes:
        start = int(note_time * sample_rate)
        dur = int(note_dur * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, note_dur, dur)

            # Vibrato increases slightly over time (more expressive)
            vibrato_depth = 0.005 + 0.003 * (note_t / note_dur)
            note_sound = expressive_tone(note_t, freq, vibrato_depth=np.mean(vibrato_depth))

            # ADSR envelope - soft attack, sustain, gentle release
            envelope = np.ones_like(note_t)

            # Attack (0.15s - quick but not harsh)
            attack_time = 0.15
            attack_samples = min(int(attack_time * sample_rate), len(envelope) // 4)
            if attack_samples > 0:
                envelope[:attack_samples] = (np.linspace(0, 1, attack_samples)) ** 2

            # Release (0.4s)
            release_time = 0.4
            release_samples = min(int(release_time * sample_rate), len(envelope) // 3)
            if release_samples > 0:
                envelope[-release_samples:] = (np.linspace(1, 0, release_samples)) ** 1.5

            audio[start:start + dur] += note_sound * envelope * velocity * 0.12

    # Lower octave doubling - more sustained, pad-like
    lower_notes = [
        (0.0, 196.00, 4.0),   # G3 - held
        (4.0, 261.63, 4.0),   # C4 - held
        (8.0, 220.00, 4.0),   # A3 - held
    ]

    for note_time, freq, note_dur in lower_notes:
        start = int(note_time * sample_rate)
        dur = int(note_dur * sample_rate)
        if start + dur < len(audio):
            note_t = np.linspace(0, note_dur, dur)
            note_sound = expressive_tone(note_t, freq, vibrato_rate=4.0, vibrato_depth=0.004)

            envelope = np.ones_like(note_t)
            # Very soft attack (0.5s)
            attack_samples = int(0.5 * sample_rate)
            if attack_samples > 0 and attack_samples < len(envelope):
                envelope[:attack_samples] = (np.linspace(0, 1, attack_samples)) ** 2
            # Gentle release
            release_samples = int(0.8 * sample_rate)
            if release_samples > 0 and release_samples < len(envelope):
                envelope[-release_samples:] = (np.linspace(1, 0, release_samples)) ** 2

            audio[start:start + dur] += note_sound * envelope * 0.08

    return audio

if __name__ == "__main__":
    audio = generate_melody_layer()
    audio = audio / np.max(np.abs(audio)) * 0.7
    wavfile.write('melody_layer.wav', 44100, (audio * 32767).astype(np.int16))
    print("Expressive melody layer created")
