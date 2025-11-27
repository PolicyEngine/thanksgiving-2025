#!/usr/bin/env python3
"""Layer 3: Atmospheric elements - autumn wind, leaves rustling, warmth."""

import numpy as np
from scipy.io import wavfile
from scipy import signal

def generate_atmosphere_layer(duration=12, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)
    np.random.seed(123)

    # Gentle autumn breeze (warm filtered noise)
    wind = np.random.randn(len(t))
    # Filter to get gentle whooshing
    b_low, a_low = signal.butter(4, 800/(sample_rate/2), btype='low')
    b_high, a_high = signal.butter(2, 100/(sample_rate/2), btype='high')
    wind = signal.filtfilt(b_low, a_low, wind)
    wind = signal.filtfilt(b_high, a_high, wind)

    # Modulate wind intensity gently
    wind_mod = 0.3 + 0.2 * np.sin(2 * np.pi * 0.15 * t)
    audio += wind * wind_mod * 0.08

    # Leaves rustling (higher frequency gentle noise bursts)
    for i in range(8):
        rustle_start = int((i * 1.5 + np.random.random()) * sample_rate)
        rustle_dur = int(0.8 * sample_rate)
        if rustle_start + rustle_dur < len(audio):
            rustle = np.random.randn(rustle_dur)
            # High-pass for crinkly leaf sound
            b_hp, a_hp = signal.butter(3, 2000/(sample_rate/2), btype='high')
            rustle = signal.filtfilt(b_hp, a_hp, rustle)
            # Envelope
            rustle_t = np.linspace(0, 0.8, rustle_dur)
            rustle_env = np.exp(-rustle_t * 4) * np.sin(np.pi * rustle_t / 0.8)
            audio[rustle_start:rustle_start + rustle_dur] += rustle * rustle_env * 0.03

    # Distant warmth hum (like a cozy room tone)
    warmth = 0.05 * np.sin(2 * np.pi * 120 * t)
    warmth += 0.03 * np.sin(2 * np.pi * 180 * t)
    # Very slow modulation
    warmth *= (1 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
    audio += warmth

    # Subtle crackling fire in background
    for i in range(15):
        crackle_start = int(np.random.random() * duration * sample_rate)
        crackle_dur = int(0.15 * sample_rate)
        if crackle_start + crackle_dur < len(audio):
            crackle = np.random.randn(crackle_dur)
            # Bandpass for crackle
            b_bp, a_bp = signal.butter(3, [500/(sample_rate/2), 3000/(sample_rate/2)], btype='band')
            crackle = signal.filtfilt(b_bp, a_bp, crackle)
            # Sharp envelope
            crackle_t = np.linspace(0, 0.15, crackle_dur)
            crackle_env = np.exp(-crackle_t * 30)
            audio[crackle_start:crackle_start + crackle_dur] += crackle * crackle_env * 0.04

    return audio

if __name__ == "__main__":
    audio = generate_atmosphere_layer()
    wavfile.write('atmosphere_layer.wav', 44100, (audio / np.max(np.abs(audio)) * 0.8 * 32767).astype(np.int16))
    print("Warm atmosphere layer created")
