#!/usr/bin/env python3
"""
Create a warm Thanksgiving soundtrack by:
1. Generating MIDI with real instrument sounds
2. Applying heavy warmth processing (EQ, compression, reverb)
3. Layering with a synthesized warm pad
"""

from midiutil import MIDIFile
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter, compress_dynamic_range
import subprocess
from pathlib import Path
import os
import numpy as np
from scipy.io import wavfile
from scipy import signal

os.chdir(Path(__file__).parent)

SOUNDFONT = "/opt/homebrew/Cellar/fluid-synth/2.5.1/share/fluid-synth/sf2/VintageDreamsWaves-v2.sf2"

def create_thanksgiving_midi():
    """Create warm MIDI with overlapping legato notes."""
    midi = MIDIFile(4)
    tempo = 66  # Slower, more contemplative

    for track in range(4):
        midi.addTempo(track, 0, tempo)

    # Track 0: Warm strings pad (held chord)
    track, channel = 0, 0
    midi.addProgramChange(track, channel, 0, 48)  # Strings

    # C major add9 - very warm
    pad_notes = [
        (48, 0, 14, 50),   # C3
        (52, 0.1, 14, 45), # E3
        (55, 0.2, 14, 45), # G3
        (62, 0.3, 14, 40), # D4 (add9)
        (60, 0.4, 14, 42), # C4
    ]
    for pitch, start, dur, vel in pad_notes:
        midi.addNote(track, channel, pitch, start, dur, vel)

    # Track 1: Piano melody - legato, overlapping
    track, channel = 1, 1
    midi.addProgramChange(track, channel, 0, 0)  # Acoustic Grand

    # Simple folk melody with overlapping notes
    melody = [
        (67, 0.5, 2.5, 65),   # G4
        (69, 2.5, 2.0, 60),   # A4 (overlaps)
        (72, 4.0, 3.0, 70),   # C5 - home note
        (71, 6.5, 2.0, 55),   # B4
        (69, 8.0, 2.0, 50),   # A4
        (67, 9.5, 3.5, 60),   # G4 - resolve
    ]
    for pitch, start, dur, vel in melody:
        midi.addNote(track, channel, pitch, start, dur, vel)

    # Track 2: Soft bass
    track, channel = 2, 2
    midi.addProgramChange(track, channel, 0, 32)  # Acoustic Bass

    bass = [
        (36, 0, 5, 55),    # C2
        (36, 5, 4, 50),    # C2
        (43, 9, 4, 55),    # G2
    ]
    for pitch, start, dur, vel in bass:
        midi.addNote(track, channel, pitch, start, dur, vel)

    # Track 3: Gentle bells (very sparse)
    track, channel = 3, 3
    midi.addProgramChange(track, channel, 0, 14)  # Tubular Bells

    bells = [
        (72, 2.0, 2.0, 35),  # C5
        (79, 7.0, 2.0, 30),  # G5
    ]
    for pitch, start, dur, vel in bells:
        midi.addNote(track, channel, pitch, start, dur, vel)

    with open("thanksgiving.mid", "wb") as f:
        midi.writeFile(f)
    print("Created MIDI file")


def midi_to_wav():
    """Convert MIDI to WAV using FluidSynth."""
    cmd = [
        'fluidsynth', '-a', 'file',
        '-F', 'midi_raw.wav',
        '-O', 's16',
        '-g', '0.8',  # Gain
        SOUNDFONT,
        'thanksgiving.mid'
    ]
    subprocess.run(cmd, capture_output=True)
    print("Converted MIDI to WAV")


def create_warm_pad():
    """Create a warm synthesized pad to layer underneath."""
    duration = 14
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))

    # Very warm C major pad with rich harmonics
    audio = np.zeros_like(t)

    # Low warm frequencies
    freqs = [65.41, 98.00, 130.81, 164.81, 196.00]  # C2, G2, C3, E3, G3
    for i, freq in enumerate(freqs):
        amp = 0.15 / (i + 1)
        audio += amp * np.sin(2 * np.pi * freq * t)
        audio += amp * 0.3 * np.sin(2 * np.pi * freq * 2 * t)

    # Slow swell
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t)
    audio *= swell

    # Fade in/out
    fade = int(2.0 * sr)
    audio[:fade] *= np.linspace(0, 1, fade) ** 2
    audio[-fade:] *= np.linspace(1, 0, fade) ** 2

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.6

    wavfile.write('warm_pad.wav', sr, (audio * 32767).astype(np.int16))
    print("Created warm pad")


def apply_warmth_processing():
    """Apply heavy warmth processing to make it cozy."""

    # Load the raw MIDI output
    midi_audio = AudioSegment.from_wav("midi_raw.wav")

    # Load the warm pad
    pad_audio = AudioSegment.from_wav("warm_pad.wav")

    # Match lengths
    target_len = 12000  # 12 seconds
    midi_audio = midi_audio[:target_len]
    pad_audio = pad_audio[:target_len]

    # Process MIDI audio for warmth:
    # 1. Low-pass to remove digital harshness - more aggressive filtering
    midi_warm = low_pass_filter(midi_audio, 3000)

    # 2. High-pass to tighten bass
    midi_warm = high_pass_filter(midi_warm, 60)

    # 3. Compress heavily for very smooth dynamics
    midi_warm = compress_dynamic_range(midi_warm, threshold=-25.0, ratio=5.0)

    # 4. Add long fade-in to soften attack transients
    midi_warm = midi_warm.fade_in(2000)

    # Process pad - longer fade-in for smooth entry
    pad_warm = low_pass_filter(pad_audio, 500)  # Very warm, just bass
    pad_warm = pad_warm.fade_in(3000)  # Extra long fade for ultimate smoothness

    # Layer: pad underneath, MIDI on top
    # Pad louder for warmth foundation
    combined = pad_warm + 4  # Boost pad more
    combined = combined.overlay(midi_warm - 3)  # MIDI even quieter for smoothness

    # Final processing
    # Heavy compression for buttery smooth sound
    final = compress_dynamic_range(combined, threshold=-18.0, ratio=4.0)

    # Additional smoothing compression pass
    final = compress_dynamic_range(final, threshold=-12.0, ratio=2.0)

    # Very long fade in/out for maximum smoothness
    final = final.fade_in(2500).fade_out(2500)

    # Normalize
    final = final.normalize()

    # Export
    final.export("thanksgiving-soundtrack-final.wav", format="wav")
    print("Created final warm soundtrack")

    # Convert to MP3
    final.export("thanksgiving-soundtrack.mp3", format="mp3", bitrate="192k")
    print(f"Created MP3: {Path('thanksgiving-soundtrack.mp3').stat().st_size // 1024} KB")


def main():
    print("Creating warm Thanksgiving soundtrack...")
    print()

    create_thanksgiving_midi()
    midi_to_wav()
    create_warm_pad()
    apply_warmth_processing()

    # Cleanup
    for f in ['midi_raw.wav', 'warm_pad.wav', 'thanksgiving.mid']:
        Path(f).unlink(missing_ok=True)

    print()
    print("Happy Thanksgiving!")


if __name__ == "__main__":
    main()
