#!/usr/bin/env python3
"""
Generate a warm Thanksgiving soundtrack using MIDI and real instrument sounds.
Uses FluidSynth with SoundFont for realistic audio.
"""

from midiutil import MIDIFile
from midi2audio import FluidSynth
from pathlib import Path
import os

os.chdir(Path(__file__).parent)

# Find soundfont
SOUNDFONT = "/opt/homebrew/Cellar/fluid-synth/2.5.1/share/fluid-synth/sf2/VintageDreamsWaves-v2.sf2"

def create_thanksgiving_midi():
    """Create a warm, cozy Thanksgiving MIDI file."""

    # Create MIDI with 4 tracks
    midi = MIDIFile(4)

    tempo = 72  # Slow, warm tempo
    midi.addTempo(0, 0, tempo)
    midi.addTempo(1, 0, tempo)
    midi.addTempo(2, 0, tempo)
    midi.addTempo(3, 0, tempo)

    # Track 0: Warm pad (Strings - program 48)
    track_pad = 0
    channel_pad = 0
    midi.addProgramChange(track_pad, channel_pad, 0, 48)  # Strings

    # C major chord held throughout - warm and full
    pad_notes = [
        (48, 0, 12, 60),   # C3 - root
        (52, 0, 12, 50),   # E3 - third
        (55, 0, 12, 50),   # G3 - fifth
        (60, 0, 12, 45),   # C4 - octave
    ]
    for pitch, start, duration, velocity in pad_notes:
        midi.addNote(track_pad, channel_pad, pitch, start, duration, velocity)

    # Track 1: Gentle melody (Acoustic Piano - program 0)
    track_melody = 1
    channel_melody = 1
    midi.addProgramChange(track_melody, channel_melody, 0, 0)  # Piano

    # Simple, warm folk-like melody - "coming home" feeling
    # G - A - C - B - A - G pattern
    melody_notes = [
        (67, 0.5, 2.0, 70),    # G4
        (69, 3.0, 1.5, 65),    # A4
        (72, 5.0, 2.5, 75),    # C5 - the "home" note, emphasized
        (71, 8.0, 1.5, 60),    # B4
        (69, 10.0, 1.0, 55),   # A4
        (67, 11.5, 1.5, 65),   # G4 - resolve
    ]
    for pitch, start, duration, velocity in melody_notes:
        midi.addNote(track_melody, channel_melody, pitch, start, duration, velocity)

    # Track 2: Warm bass (Acoustic Bass - program 32)
    track_bass = 2
    channel_bass = 2
    midi.addProgramChange(track_bass, channel_bass, 0, 32)  # Acoustic Bass

    # Simple root movement
    bass_notes = [
        (36, 0, 4, 70),    # C2
        (36, 4, 4, 65),    # C2
        (43, 8, 4, 70),    # G2
        (36, 12, 1, 60),   # C2 - ending
    ]
    for pitch, start, duration, velocity in bass_notes:
        midi.addNote(track_bass, channel_bass, pitch, start, duration, velocity)

    # Track 3: Gentle chimes/bells (Tubular Bells - program 14)
    track_chimes = 3
    channel_chimes = 3
    midi.addProgramChange(track_chimes, channel_chimes, 0, 14)  # Tubular Bells

    # Sparse, gentle chimes
    chime_notes = [
        (72, 1.0, 1.5, 45),   # C5
        (76, 4.0, 1.5, 40),   # E5
        (79, 7.0, 1.5, 45),   # G5
        (72, 10.5, 2.0, 50),  # C5 - ending
    ]
    for pitch, start, duration, velocity in chime_notes:
        midi.addNote(track_chimes, channel_chimes, pitch, start, duration, velocity)

    # Save MIDI file
    midi_path = "thanksgiving.mid"
    with open(midi_path, "wb") as f:
        midi.writeFile(f)

    print(f"Created MIDI: {midi_path}")
    return midi_path


def convert_to_audio(midi_path, output_path="thanksgiving-soundtrack.wav"):
    """Convert MIDI to WAV using FluidSynth."""

    if not Path(SOUNDFONT).exists():
        print(f"SoundFont not found at {SOUNDFONT}")
        return None

    fs = FluidSynth(SOUNDFONT)
    fs.midi_to_audio(midi_path, output_path)

    print(f"Created WAV: {output_path}")
    return output_path


def main():
    print("Generating warm Thanksgiving soundtrack with real instruments...")

    # Create MIDI
    midi_path = create_thanksgiving_midi()

    # Convert to audio
    wav_path = convert_to_audio(midi_path, "thanksgiving-soundtrack-final.wav")

    if wav_path:
        # Convert to MP3
        import subprocess
        mp3_cmd = [
            'ffmpeg', '-y',
            '-i', wav_path,
            '-codec:a', 'libmp3lame',
            '-b:a', '192k',
            'thanksgiving-soundtrack.mp3'
        ]
        result = subprocess.run(mp3_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            mp3_size = Path('thanksgiving-soundtrack.mp3').stat().st_size / 1024
            print(f"Created MP3: {mp3_size:.0f} KB")

        print("\nHappy Thanksgiving!")
    else:
        print("Failed to convert to audio")


if __name__ == "__main__":
    main()
