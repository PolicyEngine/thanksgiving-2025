#!/usr/bin/env python3
"""
Create Thanksgiving soundtrack using real Steinway piano samples
from University of Iowa Musical Instrument Samples (public domain).
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
import os
import subprocess

os.chdir(Path(__file__).parent)

SAMPLE_RATE = 44100
DURATION = 12  # seconds


def load_aiff_sample(filepath):
    """Load AIFF file and convert to numpy array."""
    # Convert AIFF to WAV using ffmpeg, then load
    temp_wav = filepath.replace('.aiff', '_temp.wav')
    subprocess.run([
        'ffmpeg', '-y', '-i', filepath,
        '-ar', str(SAMPLE_RATE),
        '-ac', '1',  # mono
        temp_wav
    ], capture_output=True)

    sr, audio = wavfile.read(temp_wav)
    Path(temp_wav).unlink()  # Clean up

    # Normalize to float
    if audio.dtype == np.int16:
        audio = audio.astype(np.float64) / 32767
    elif audio.dtype == np.int32:
        audio = audio.astype(np.float64) / 2147483647

    return audio


def apply_envelope(audio, attack=0.01, decay=0.1, sustain=0.7, release=0.5, duration=None):
    """Apply ADSR envelope to audio."""
    if duration is not None:
        target_len = int(duration * SAMPLE_RATE)
        if len(audio) > target_len:
            audio = audio[:target_len]
        else:
            # Pad with zeros
            audio = np.pad(audio, (0, target_len - len(audio)))

    total_samples = len(audio)

    # Calculate sample counts for each phase
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

    envelope = np.ones(total_samples)

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay to sustain level
    if decay_samples > 0:
        start = attack_samples
        end = start + decay_samples
        if end <= total_samples:
            envelope[start:end] = np.linspace(1, sustain, decay_samples)

    # Sustain
    sustain_start = attack_samples + decay_samples
    sustain_end = sustain_start + sustain_samples
    if sustain_end <= total_samples:
        envelope[sustain_start:sustain_end] = sustain

    # Release
    if release_samples > 0:
        release_start = total_samples - release_samples
        envelope[release_start:] = np.linspace(sustain, 0, release_samples) ** 2

    return audio * envelope


def pitch_shift_sample(audio, semitones):
    """Shift pitch by resampling (simple method)."""
    factor = 2 ** (semitones / 12)

    # Resample
    new_length = int(len(audio) / factor)
    indices = np.linspace(0, len(audio) - 1, new_length)
    shifted = np.interp(indices, np.arange(len(audio)), audio)

    return shifted


def create_warm_pad(duration, freqs):
    """Create a warm synthesized string-like pad."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    audio = np.zeros_like(t)

    for freq in freqs:
        # Ensemble-style multiple voices slightly detuned
        for detune in [-0.004, 0, 0.004]:
            detuned = freq * (1 + detune)

            # Slow vibrato
            vibrato = 1 + 0.003 * np.sin(2 * np.pi * 4.5 * t)
            phase = np.cumsum(2 * np.pi * detuned * vibrato / SAMPLE_RATE)

            # Rich harmonics
            sound = np.sin(phase)
            sound += 0.4 * np.sin(phase * 2)
            sound += 0.15 * np.sin(phase * 3)

            audio += sound / (3 * len(freqs))

    # Very slow attack
    attack = int(2.0 * SAMPLE_RATE)
    audio[:attack] *= np.linspace(0, 1, attack) ** 2

    # Gentle release
    release = int(2.5 * SAMPLE_RATE)
    audio[-release:] *= np.linspace(1, 0, release) ** 2

    return audio * 0.12  # Reduced from 0.3 - keep pad subtle under piano


def create_thanksgiving_soundtrack():
    """Create soundtrack using real piano samples."""
    print("Loading piano samples...")

    # Load available samples
    samples = {}
    sample_notes = {
        'G4': 392.00,
        'A4': 440.00,
        'B4': 493.88,
        'C5': 523.25,
        'C4': 261.63,
        'E4': 329.63,
        'C3': 130.81,
        'E3': 164.81,
        'G3': 196.00,
        'D4': 293.66,
    }

    for note in sample_notes.keys():
        filepath = f'samples/piano/Piano.mf.{note}.aiff'
        if Path(filepath).exists():
            try:
                samples[note] = load_aiff_sample(filepath)
                print(f"  Loaded {note}")
            except Exception as e:
                print(f"  Failed to load {note}: {e}")

    if not samples:
        print("No samples loaded! Falling back to synthesis.")
        return None

    # Create output array
    total_samples = int(DURATION * SAMPLE_RATE)
    audio = np.zeros(total_samples)

    # Layer 1: Warm pad underneath (synthesized)
    print("Creating warm pad layer...")
    pad_freqs = [130.81, 164.81, 196.00]  # C3, E3, G3
    pad = create_warm_pad(DURATION, pad_freqs)
    audio[:len(pad)] += pad

    # Layer 2: Piano melody using real samples
    # Simple "coming home" melody: G - A - C - B - A - G
    print("Adding piano melody...")
    melody = [
        (0.5, 'G4', 2.0, 0.85),
        (3.0, 'A4', 1.8, 0.8),
        (5.0, 'C5', 2.5, 0.95),   # Home note, emphasized
        (7.5, 'B4', 1.5, 0.75),
        (9.2, 'A4', 1.3, 0.7),
        (10.8, 'G4', 1.2, 0.8),
    ]

    for time, note, dur, vel in melody:
        if note in samples:
            start = int(time * SAMPLE_RATE)
            sample = samples[note].copy()
            sample = apply_envelope(sample, attack=0.01, decay=0.3, sustain=0.6,
                                   release=0.8, duration=dur)
            sample *= vel

            end = min(start + len(sample), total_samples)
            audio[start:end] += sample[:end - start]

    # Layer 3: Lower piano notes for warmth
    print("Adding bass piano notes...")
    bass_notes = [
        (0.0, 'C3', 4.0, 0.4),
        (4.0, 'E3', 3.5, 0.35),
        (8.0, 'C3', 4.0, 0.4),
    ]

    for time, note, dur, vel in bass_notes:
        if note in samples:
            start = int(time * SAMPLE_RATE)
            sample = samples[note].copy()
            sample = apply_envelope(sample, attack=0.02, decay=0.5, sustain=0.5,
                                   release=1.5, duration=dur)
            sample *= vel

            end = min(start + len(sample), total_samples)
            audio[start:end] += sample[:end - start]

    # Layer 4: Gentle high notes for sparkle
    print("Adding gentle high notes...")
    high_notes = [
        (2.0, 'E4', 1.5, 0.25),
        (6.5, 'D4', 1.5, 0.25),
    ]

    for time, note, dur, vel in high_notes:
        if note in samples:
            start = int(time * SAMPLE_RATE)
            sample = samples[note].copy()
            sample = apply_envelope(sample, attack=0.05, decay=0.3, sustain=0.4,
                                   release=0.6, duration=dur)
            sample *= vel

            end = min(start + len(sample), total_samples)
            audio[start:end] += sample[:end - start]

    # Post-processing
    print("Applying warmth processing...")

    # Gentle low-pass to remove harshness
    nyquist = SAMPLE_RATE / 2
    cutoff = 5000 / nyquist
    b, a = signal.butter(2, cutoff, btype='low')
    audio = signal.filtfilt(b, a, audio)

    # Soft compression to reduce dynamic range (more gentle feel)
    # Simple soft-knee compression
    threshold = 0.3
    ratio = 3.0
    audio_sign = np.sign(audio)
    audio_abs = np.abs(audio)
    mask = audio_abs > threshold
    audio_abs[mask] = threshold + (audio_abs[mask] - threshold) / ratio
    audio = audio_sign * audio_abs

    # Soft saturation for tape-like warmth
    audio = np.tanh(audio * 2.0) / 2.0

    # Long fade in/out
    fade_in = int(2.0 * SAMPLE_RATE)
    fade_out = int(2.5 * SAMPLE_RATE)
    audio[:fade_in] *= np.linspace(0, 1, fade_in) ** 2
    audio[-fade_out:] *= np.linspace(1, 0, fade_out) ** 2

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.85

    return audio


def main():
    print("Creating Thanksgiving soundtrack with real piano samples...")
    print("(Using University of Iowa Musical Instrument Samples - Public Domain)")
    print()

    audio = create_thanksgiving_soundtrack()

    if audio is None:
        print("Failed to create soundtrack")
        return

    # Save WAV
    wavfile.write('thanksgiving-soundtrack-final.wav', SAMPLE_RATE,
                  (audio * 32767).astype(np.int16))
    print("\nCreated WAV file")

    # Convert to MP3
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_wav('thanksgiving-soundtrack-final.wav')
        sound.export('thanksgiving-soundtrack.mp3', format='mp3', bitrate='192k')
        print(f"Created MP3: {Path('thanksgiving-soundtrack.mp3').stat().st_size // 1024} KB")
    except Exception as e:
        print(f"MP3 conversion failed: {e}")

    print("\nHappy Thanksgiving!")


if __name__ == "__main__":
    main()
