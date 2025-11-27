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
    t = np.linspace(0, DURATION, total_samples)
    nyquist = SAMPLE_RATE / 2

    # Layer 0: Ambient fall sounds
    print("Adding ambient fall sounds...")

    # Gentle wind (filtered noise)
    wind = np.random.randn(total_samples) * 0.03
    # Very low-pass for soft whoosh
    wind_cutoff = 400 / nyquist
    b_wind, a_wind = signal.butter(3, wind_cutoff, btype='low')
    wind = signal.filtfilt(b_wind, a_wind, wind)
    # Slow volume swells
    wind_swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)  # ~12 second cycle
    wind *= wind_swell * 0.4
    audio += wind

    # Rustling leaves (higher filtered noise, intermittent)
    leaves = np.random.randn(total_samples) * 0.02
    # Band-pass for papery rustle sound
    leaves_low = 800 / nyquist
    leaves_high = 3000 / nyquist
    b_leaves, a_leaves = signal.butter(2, [leaves_low, leaves_high], btype='band')
    leaves = signal.filtfilt(b_leaves, a_leaves, leaves)
    # Intermittent rustles
    rustle_times = [1.5, 4.0, 7.5, 10.0]
    leaves_env = np.zeros(total_samples)
    for rt in rustle_times:
        start = int(rt * SAMPLE_RATE)
        rustle_dur = int(0.8 * SAMPLE_RATE)
        if start + rustle_dur < total_samples:
            rustle_shape = np.exp(-3 * np.linspace(0, 1, rustle_dur))
            leaves_env[start:start+rustle_dur] = rustle_shape
    leaves *= leaves_env * 0.3
    audio += leaves

    # Distant birds (simple chirps using sine sweeps)
    bird_times = [2.5, 6.0, 9.5]
    for bt in bird_times:
        start = int(bt * SAMPLE_RATE)
        chirp_dur = int(0.15 * SAMPLE_RATE)
        if start + chirp_dur < total_samples:
            chirp_t = np.linspace(0, 0.15, chirp_dur)
            # Descending chirp
            chirp_freq = 2500 - 800 * chirp_t / 0.15
            chirp = np.sin(2 * np.pi * chirp_freq * chirp_t)
            chirp *= np.exp(-8 * chirp_t)  # Quick decay
            audio[start:start+chirp_dur] += chirp * 0.015
            # Second chirp slightly after
            start2 = start + int(0.2 * SAMPLE_RATE)
            if start2 + chirp_dur < total_samples:
                audio[start2:start2+chirp_dur] += chirp * 0.012

    # Layer 1: Very subtle low bass foundation (not a "hum" - just warmth)
    print("Adding subtle bass foundation...")
    # Very low, barely audible bass notes that follow the chord roots
    bass_foundation = np.zeros_like(t)
    bass_times = [(0.5, 65.41), (3.0, 82.41), (5.5, 65.41), (8.0, 98.00), (10.3, 65.41)]  # C2, E2, C2, G2, C2
    for bass_time, bass_freq in bass_times:
        start = int(bass_time * SAMPLE_RATE)
        bass_dur = 2.5
        bass_samples = int(bass_dur * SAMPLE_RATE)
        if start + bass_samples < len(bass_foundation):
            bass_t = np.linspace(0, bass_dur, bass_samples)
            # Pure sine, very soft
            bass_note = np.sin(2 * np.pi * bass_freq * bass_t)
            # Slow attack and release
            bass_env = np.ones_like(bass_t)
            attack = int(0.3 * SAMPLE_RATE)
            release = int(0.8 * SAMPLE_RATE)
            bass_env[:attack] = np.linspace(0, 1, attack) ** 2
            bass_env[-release:] = np.linspace(1, 0, release) ** 2
            bass_foundation[start:start+bass_samples] += bass_note * bass_env * 0.15
    audio += bass_foundation

    # Layer 2: Piano chords using real samples
    # Warm chord progression with melody note on top
    print("Adding piano chords...")

    # Chord definitions: (time, [(note, velocity), ...], duration)
    # More flowing, overlapping progression
    chords = [
        # C major - gentle opening
        (0.5, [('C3', 0.4), ('G3', 0.35), ('C4', 0.4), ('E4', 0.5)], 3.2),
        # C/E - bass moves up smoothly
        (3.0, [('E3', 0.35), ('G3', 0.35), ('C4', 0.4), ('G4', 0.55)], 2.8),
        # F major - warmth
        (5.5, [('C3', 0.4), ('C4', 0.4), ('E4', 0.35), ('A4', 0.5)], 2.8),
        # G7 - gentle tension leading home
        (8.0, [('G3', 0.4), ('D4', 0.35), ('G4', 0.45), ('B4', 0.5)], 2.5),
        # C major - final resolve (let it ring)
        (10.3, [('C3', 0.45), ('E3', 0.4), ('G3', 0.35), ('C4', 0.5)], 2.0),
    ]

    for time, chord_notes, dur in chords:
        for i, (note, vel) in enumerate(chord_notes):
            if note in samples:
                # Very gentle roll - almost simultaneous but not quite
                strum_delay = i * 0.015  # 15ms between notes - subtler
                start = int((time + strum_delay) * SAMPLE_RATE)
                sample = samples[note].copy()
                # Longer decay and release for more legato feel
                sample = apply_envelope(sample, attack=0.02, decay=0.8, sustain=0.4,
                                       release=1.5, duration=dur + 0.5)  # Extra ring time
                sample *= vel

                end = min(start + len(sample), total_samples)
                audio[start:end] += sample[:end - start]

    # Post-processing
    print("Applying warmth processing...")

    # Boost low frequencies for warmth (bass shelf)
    bass_cutoff = 300 / nyquist
    b_bass, a_bass = signal.butter(2, bass_cutoff, btype='low')
    bass_boost = signal.filtfilt(b_bass, a_bass, audio)
    audio = audio + bass_boost * 0.8  # Add bass warmth

    # Gentle low-pass to remove harshness
    cutoff = 6000 / nyquist
    b, a = signal.butter(2, cutoff, btype='low')
    audio = signal.filtfilt(b, a, audio)

    # Heavy compression for smooth, even dynamics
    threshold = 0.15
    ratio = 6.0
    audio_sign = np.sign(audio)
    audio_abs = np.abs(audio)
    mask = audio_abs > threshold
    audio_abs[mask] = threshold + (audio_abs[mask] - threshold) / ratio
    audio = audio_sign * audio_abs

    # Second pass compression
    threshold2 = 0.25
    ratio2 = 3.0
    audio_abs = np.abs(audio)
    mask = audio_abs > threshold2
    audio_abs[mask] = threshold2 + (audio_abs[mask] - threshold2) / ratio2
    audio = np.sign(audio) * audio_abs

    # Soft saturation for tape-like warmth
    audio = np.tanh(audio * 2.5) / 2.5

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
