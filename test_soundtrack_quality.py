#!/usr/bin/env python3
"""
Test-driven development for Thanksgiving music composition.
Define what makes a warm, cozy, Thanksgiving-y soundtrack.
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from scipy.fft import fft, fftfreq
import json

class ThanksgivingSoundtrackAnalyzer:
    def __init__(self, audio_file):
        self.sr, self.audio = wavfile.read(audio_file)
        if len(self.audio.shape) > 1:
            self.audio = self.audio[:, 0]
        self.audio = self.audio.astype(np.float32) / 32767
        self.duration = len(self.audio) / self.sr

    def test_warmth(self):
        """Test: Should have warm frequencies (100-500Hz) dominant, not harsh highs."""
        fft_data = np.abs(fft(self.audio))
        freqs = fftfreq(len(self.audio), 1/self.sr)

        bands = {
            'sub_bass': (20, 80),      # Rumble - should be moderate
            'warm_bass': (80, 250),    # Warmth foundation - should be strong
            'warm_mid': (250, 500),    # Body/warmth - should be present
            'mid': (500, 2000),        # Clarity - moderate
            'high_mid': (2000, 6000),  # Brightness - should be gentle
            'high': (6000, 12000)      # Air - should be minimal (not harsh)
        }

        results = {}
        for band_name, (low, high) in bands.items():
            mask = (np.abs(freqs) >= low) & (np.abs(freqs) <= high)
            energy = np.sum(fft_data[mask])
            results[band_name] = float(energy)

        total_energy = sum(results.values())
        percentages = {k: v/total_energy * 100 for k, v in results.items()}

        # Thanksgiving warmth requirements
        checks = {
            'has_warm_bass': percentages['warm_bass'] > 25,      # Strong warm foundation
            'has_body': percentages['warm_mid'] > 15,            # Full body
            'not_harsh': percentages['high'] < 10,               # Not too bright/harsh
            'gentle_highs': percentages['high_mid'] < 20,        # Gentle, not piercing
            'warm_ratio': (percentages['warm_bass'] + percentages['warm_mid']) > 45  # Overall warmth
        }

        return {
            'test': 'warmth',
            'passed': all(checks.values()),
            'details': percentages,
            'checks': checks
        }

    def test_smoothness(self):
        """Test: Should be smooth and flowing, not jarring or abrupt."""
        # Analyze envelope smoothness
        envelope = np.abs(signal.hilbert(self.audio))

        # Calculate derivative (rate of change)
        envelope_diff = np.diff(envelope)

        # Count harsh transients (sudden changes)
        threshold = np.std(envelope_diff) * 4
        harsh_transients = np.sum(np.abs(envelope_diff) > threshold)
        harsh_ratio = harsh_transients / len(envelope_diff)

        # Calculate overall smoothness
        smoothness = 1.0 - (np.std(envelope_diff) / (np.mean(np.abs(envelope_diff)) + 0.0001))

        checks = {
            'smooth_envelope': harsh_ratio < 0.01,  # Less than 1% harsh transients
            'gentle_transitions': smoothness > 0.5   # Generally smooth
        }

        return {
            'test': 'smoothness',
            'passed': all(checks.values()),
            'details': {
                'harsh_transient_ratio': float(harsh_ratio),
                'smoothness_score': float(smoothness)
            },
            'checks': checks
        }

    def test_consonance(self):
        """Test: Should use consonant (pleasant) intervals, not dissonant."""
        # Analyze harmonic content
        fft_data = np.abs(fft(self.audio))
        freqs = fftfreq(len(self.audio), 1/self.sr)

        # Look at positive frequencies only
        positive_mask = freqs > 0
        freqs_pos = freqs[positive_mask]
        fft_pos = fft_data[positive_mask]

        # Find dominant frequencies (peaks)
        peaks, _ = signal.find_peaks(fft_pos, height=np.max(fft_pos) * 0.1)

        if len(peaks) < 2:
            return {
                'test': 'consonance',
                'passed': True,
                'details': {'peak_count': len(peaks)},
                'checks': {'has_harmony': True}
            }

        # Get peak frequencies
        peak_freqs = freqs_pos[peaks]
        peak_freqs = peak_freqs[peak_freqs < 2000]  # Focus on musical range

        # Check for consonant ratios (octaves, fifths, thirds)
        consonant_ratios = [1.0, 2.0, 1.5, 1.25, 1.33, 1.2]  # Unison, octave, fifth, third, etc.

        consonant_count = 0
        total_pairs = 0

        for i, f1 in enumerate(peak_freqs[:10]):
            for f2 in peak_freqs[i+1:10]:
                if f1 > 0 and f2 > 0:
                    ratio = max(f1, f2) / min(f1, f2)
                    for cr in consonant_ratios:
                        if abs(ratio - cr) < 0.1 or abs(ratio - cr*2) < 0.1:
                            consonant_count += 1
                            break
                    total_pairs += 1

        consonance_ratio = consonant_count / total_pairs if total_pairs > 0 else 1.0

        checks = {
            'mostly_consonant': consonance_ratio > 0.3  # At least 30% consonant relationships
        }

        return {
            'test': 'consonance',
            'passed': all(checks.values()),
            'details': {
                'consonance_ratio': float(consonance_ratio),
                'consonant_pairs': int(consonant_count),
                'total_pairs': int(total_pairs)
            },
            'checks': checks
        }

    def test_gentle_dynamics(self):
        """Test: Should have gentle, not extreme dynamics."""
        rms = np.sqrt(np.mean(self.audio ** 2))
        peak = np.max(np.abs(self.audio))
        crest_factor = peak / rms if rms > 0 else 0
        crest_db = 20 * np.log10(crest_factor) if crest_factor > 0 else 0

        # For warm/cozy: moderate dynamics (not too flat, not too punchy)
        checks = {
            'not_too_flat': crest_db > 3,
            'not_too_punchy': crest_db < 12,  # More compressed than spooky
            'good_volume': rms > 0.08
        }

        return {
            'test': 'gentle_dynamics',
            'passed': all(checks.values()),
            'details': {
                'crest_factor_db': float(crest_db),
                'rms_level': float(rms),
                'peak_level': float(peak)
            },
            'checks': checks
        }

    def test_melodic_content(self):
        """Test: Should have recognizable melodic movement."""
        # Analyze pitch variation over time
        window_size = int(0.25 * self.sr)
        hop_size = window_size // 2
        num_windows = (len(self.audio) - window_size) // hop_size

        dominant_freqs = []
        for i in range(num_windows):
            start = i * hop_size
            window = self.audio[start:start + window_size]

            fft_data = np.abs(fft(window))
            freqs = fftfreq(len(window), 1/self.sr)

            # Focus on melodic range (200-2000 Hz)
            mask = (freqs > 200) & (freqs < 2000)
            if np.any(mask):
                melodic_fft = fft_data[mask]
                melodic_freqs = freqs[mask]
                if len(melodic_fft) > 0 and np.max(melodic_fft) > 0:
                    dominant_idx = np.argmax(melodic_fft)
                    dominant_freqs.append(melodic_freqs[dominant_idx])

        if len(dominant_freqs) < 3:
            return {
                'test': 'melodic_content',
                'passed': False,
                'details': {'note': 'Not enough melodic content detected'},
                'checks': {'has_melody': False}
            }

        # Check for melodic movement (pitch changes)
        pitch_changes = np.diff(dominant_freqs)
        meaningful_changes = np.sum(np.abs(pitch_changes) > 20)  # > 20Hz change

        checks = {
            'has_melody': meaningful_changes > 3,  # At least a few pitch changes
            'not_monotonous': np.std(dominant_freqs) > 50  # Some variation
        }

        return {
            'test': 'melodic_content',
            'passed': all(checks.values()),
            'details': {
                'pitch_changes': int(meaningful_changes),
                'pitch_std': float(np.std(dominant_freqs))
            },
            'checks': checks
        }

    def test_fullness(self):
        """Test: Should sound full and rich, not thin or empty."""
        fft_data = np.abs(fft(self.audio))
        freqs = fftfreq(len(self.audio), 1/self.sr)

        # Count frequency bands with significant energy
        bands = [(50*i, 50*(i+1)) for i in range(1, 40)]  # 50Hz bands up to 2000Hz
        active_bands = 0

        for low, high in bands:
            mask = (np.abs(freqs) >= low) & (np.abs(freqs) <= high)
            band_energy = np.sum(fft_data[mask])
            if band_energy > np.mean(fft_data) * 0.5:
                active_bands += 1

        fullness_ratio = active_bands / len(bands)

        checks = {
            'sounds_full': fullness_ratio > 0.3,  # At least 30% of bands active
            'rich_spectrum': active_bands > 10    # Multiple active frequency bands
        }

        return {
            'test': 'fullness',
            'passed': all(checks.values()),
            'details': {
                'active_bands': int(active_bands),
                'fullness_ratio': float(fullness_ratio)
            },
            'checks': checks
        }

    def run_all_tests(self):
        """Run all Thanksgiving quality tests."""
        tests = [
            self.test_warmth(),
            self.test_smoothness(),
            self.test_consonance(),
            self.test_gentle_dynamics(),
            self.test_melodic_content(),
            self.test_fullness()
        ]

        all_passed = all(t['passed'] for t in tests)

        return {
            'overall': 'PASS' if all_passed else 'NEEDS IMPROVEMENT',
            'score': f"{sum(t['passed'] for t in tests)}/{len(tests)}",
            'tests': tests
        }


def generate_review(results):
    """Generate human-readable review with suggestions."""
    print("\n" + "="*60)
    print("THANKSGIVING SOUNDTRACK QUALITY REPORT")
    print("="*60)
    print(f"\nOverall Score: {results['score']} tests passed")
    print(f"Status: {results['overall']}\n")

    for test in results['tests']:
        status = "PASS" if test['passed'] else "FAIL"
        print(f"[{status}] {test['test'].upper()}")

        for check_name, passed in test['checks'].items():
            check_status = "  OK" if passed else "  XX"
            print(f"{check_status} {check_name}")

        if test['details']:
            for k, v in test['details'].items():
                if isinstance(v, float):
                    print(f"      {k}: {v:.2f}")
                else:
                    print(f"      {k}: {v}")
        print()

    print("="*60)
    print("IMPROVEMENT SUGGESTIONS:")
    print("="*60)

    suggestions = []
    for test in results['tests']:
        if not test['passed']:
            if test['test'] == 'warmth':
                if not test['checks'].get('has_warm_bass'):
                    suggestions.append("- Boost warm bass frequencies (80-250Hz)")
                if not test['checks'].get('not_harsh'):
                    suggestions.append("- Reduce high frequencies (>6kHz) for less harshness")
                if not test['checks'].get('has_body'):
                    suggestions.append("- Add more mid-low frequencies (250-500Hz) for body")

            if test['test'] == 'smoothness':
                suggestions.append("- Soften attack transients, use longer fade-ins")
                suggestions.append("- Add more legato/sustained sounds")

            if test['test'] == 'consonance':
                suggestions.append("- Use more major chords and consonant intervals")
                suggestions.append("- Avoid tritones and minor seconds")

            if test['test'] == 'gentle_dynamics':
                if not test['checks'].get('not_too_punchy'):
                    suggestions.append("- Apply more compression, soften peaks")

            if test['test'] == 'melodic_content':
                suggestions.append("- Add a clearer melody line")
                suggestions.append("- Include more pitch variation over time")

            if test['test'] == 'fullness':
                suggestions.append("- Layer more sounds to fill the frequency spectrum")
                suggestions.append("- Add pad sounds or sustained chords")

    if not suggestions:
        print("All tests passed! The soundtrack sounds warm and Thanksgiving-y!")
    else:
        for suggestion in suggestions:
            print(suggestion)

    print("\n" + "="*60)


if __name__ == "__main__":
    import sys

    audio_file = sys.argv[1] if len(sys.argv) > 1 else 'thanksgiving-soundtrack-final.wav'

    print(f"Analyzing: {audio_file}")
    analyzer = ThanksgivingSoundtrackAnalyzer(audio_file)
    results = analyzer.run_all_tests()
    generate_review(results)

    with open('soundtrack_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nDetailed analysis saved to soundtrack_analysis.json")
