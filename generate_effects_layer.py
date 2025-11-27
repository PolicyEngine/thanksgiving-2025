#!/usr/bin/env python3
"""Layer 4: Sound effects - turkey gobbles, gathering sounds, warmth."""

import numpy as np
from scipy.io import wavfile
from scipy import signal

def turkey_gobble(duration, sample_rate):
    """Generate a stylized turkey gobble sound."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Base frequency modulation for gobble
    base_freq = 200
    freq_mod = base_freq + 150 * np.sin(2 * np.pi * 8 * t)  # Rapid wobble

    # Generate the sound
    phase = np.cumsum(2 * np.pi * freq_mod / sample_rate)
    gobble = np.sin(phase)

    # Add harmonics
    gobble += 0.5 * np.sin(2 * phase)
    gobble += 0.3 * np.sin(3 * phase)

    # Envelope - rapid attack and decay bursts
    bursts = np.zeros_like(t)
    num_bursts = 5
    for i in range(num_bursts):
        burst_center = duration * (i + 0.5) / num_bursts
        burst_width = 0.08
        bursts += np.exp(-((t - burst_center) / burst_width) ** 2)

    gobble *= bursts

    return gobble

def generate_effects_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)
    np.random.seed(456)

    # Turkey gobbles (gentle, distant)
    gobble_times = [2.5, 8.0]
    for gobble_time in gobble_times:
        start = int(gobble_time * sample_rate)
        gobble_dur = 0.8
        gobble_samples = int(gobble_dur * sample_rate)
        if start + gobble_samples < len(audio):
            gobble = turkey_gobble(gobble_dur, sample_rate)
            # Make it sound distant
            b_lp, a_lp = signal.butter(3, 2000/(sample_rate/2), btype='low')
            gobble = signal.filtfilt(b_lp, a_lp, gobble)
            audio[start:start + gobble_samples] += gobble * 0.08

    # Gentle door chime / arrival sound
    chime_time = 1.0
    start = int(chime_time * sample_rate)
    chime_dur = int(1.5 * sample_rate)
    if start + chime_dur < len(audio):
        chime_t = np.linspace(0, 1.5, chime_dur)
        # Two-tone doorbell
        chime = 0.3 * np.sin(2 * np.pi * 659 * chime_t)  # E5
        chime += 0.3 * np.sin(2 * np.pi * 523 * chime_t) * (chime_t > 0.3)  # C5
        chime_env = np.exp(-chime_t * 2)
        audio[start:start + chime_dur] += chime * chime_env * 0.1

    # Gentle clinking (like glasses/dishes - gathering sounds)
    clink_times = [4.0, 6.5, 10.0]
    for clink_time in clink_times:
        start = int(clink_time * sample_rate)
        clink_dur = int(0.3 * sample_rate)
        if start + clink_dur < len(audio):
            clink_t = np.linspace(0, 0.3, clink_dur)
            # High metallic ping
            clink = np.sin(2 * np.pi * 2000 * clink_t)
            clink += 0.5 * np.sin(2 * np.pi * 3500 * clink_t)
            clink_env = np.exp(-clink_t * 15)
            audio[start:start + clink_dur] += clink * clink_env * 0.05

    # Warm laughter-like hum (distant, joyful)
    laugh_times = [5.5, 9.0]
    for laugh_time in laugh_times:
        start = int(laugh_time * sample_rate)
        laugh_dur = int(1.0 * sample_rate)
        if start + laugh_dur < len(audio):
            laugh_t = np.linspace(0, 1.0, laugh_dur)
            # Warm, modulated tone
            freq_base = 300
            freq_mod = freq_base + 50 * np.sin(2 * np.pi * 5 * laugh_t)
            laugh = np.sin(2 * np.pi * freq_mod * laugh_t)
            # Pulsing envelope
            laugh_env = np.sin(np.pi * laugh_t) * (1 + 0.3 * np.sin(2 * np.pi * 4 * laugh_t))
            audio[start:start + laugh_dur] += laugh * laugh_env * 0.04

    # Gentle footsteps (soft, welcoming)
    for i in range(6):
        step_time = 0.5 + i * 0.4
        start = int(step_time * sample_rate)
        step_dur = int(0.1 * sample_rate)
        if start + step_dur < len(audio):
            step = np.random.randn(step_dur)
            b_bp, a_bp = signal.butter(3, [100/(sample_rate/2), 500/(sample_rate/2)], btype='band')
            step = signal.filtfilt(b_bp, a_bp, step)
            step_t = np.linspace(0, 0.1, step_dur)
            step_env = np.exp(-step_t * 40)
            audio[start:start + step_dur] += step * step_env * 0.03

    return audio

if __name__ == "__main__":
    audio = generate_effects_layer()
    wavfile.write('effects_layer.wav', 44100, (audio / np.max(np.abs(audio)) * 0.8 * 32767).astype(np.int16))
    print("Warm effects layer created")
