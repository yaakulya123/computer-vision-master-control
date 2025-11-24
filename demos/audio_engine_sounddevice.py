"""
Simple Audio Engine using sounddevice
Works reliably on macOS without complex dependencies
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Dict

class SimpleAudioEngine:
    """
    Simple real-time audio synthesis using sounddevice
    Generates binaural beats, tremolo, FM synthesis, and noise
    """

    def __init__(self, sample_rate: int = 44100, block_size: int = 2048):
        """
        Initialize audio engine

        Args:
            sample_rate: Audio sample rate in Hz
            block_size: Audio buffer size
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.is_running = False
        self.audio_thread = None

        # Current synthesis parameters
        self.base_freq = 100.0
        self.binaural_diff = 5.0
        self.lfo_rate = 0.0
        self.lfo_depth = 0.0
        self.fm_amount = 0.0
        self.noise_amount = 0.0
        self.amplitude = 0.3
        self.pan = 0.0  # -1.0 (left) to 1.0 (right)
        self.chaos_level = 0.0

        # Phase accumulators for continuous waveforms
        self.phase_left = 0.0
        self.phase_right = 0.0
        self.phase_lfo = 0.0
        self.phase_modulator = 0.0

        # Audio stream
        self.stream = None

        print("🔊 Simple Audio Engine initialized (sounddevice)")

    def _audio_callback(self, outdata, frames, time_info, status):
        """
        Audio callback - generates audio in real-time
        Called by sounddevice in separate thread
        """
        if status:
            print(f"Audio callback status: {status}")

        # Time array for this block
        t = np.arange(frames) / self.sample_rate

        # Generate binaural drone
        # Left channel: base frequency
        left_freq = self.base_freq
        phase_increment_left = 2 * np.pi * left_freq / self.sample_rate

        left_signal = np.zeros(frames)
        for i in range(frames):
            left_signal[i] = np.sin(self.phase_left)
            self.phase_left += phase_increment_left
            if self.phase_left > 2 * np.pi:
                self.phase_left -= 2 * np.pi

        # Right channel: base + binaural difference
        right_freq = self.base_freq + self.binaural_diff
        phase_increment_right = 2 * np.pi * right_freq / self.sample_rate

        right_signal = np.zeros(frames)
        for i in range(frames):
            right_signal[i] = np.sin(self.phase_right)
            self.phase_right += phase_increment_right
            if self.phase_right > 2 * np.pi:
                self.phase_right -= 2 * np.pi

        # Apply LFO (tremolo) if active
        if self.lfo_rate > 0.01 and self.lfo_depth > 0.01:
            phase_increment_lfo = 2 * np.pi * self.lfo_rate / self.sample_rate
            lfo_signal = np.zeros(frames)

            for i in range(frames):
                lfo_signal[i] = np.sin(self.phase_lfo) * self.lfo_depth * 0.3 + 1.0
                self.phase_lfo += phase_increment_lfo
                if self.phase_lfo > 2 * np.pi:
                    self.phase_lfo -= 2 * np.pi

            left_signal *= lfo_signal
            right_signal *= lfo_signal

        # Apply FM synthesis for chaos
        if self.fm_amount > 0.01:
            modulator_freq = self.base_freq * 2
            phase_increment_mod = 2 * np.pi * modulator_freq / self.sample_rate

            for i in range(frames):
                modulator = np.sin(self.phase_modulator) * self.fm_amount * 0.01

                # Modulate left channel
                left_signal[i] = np.sin(self.phase_left + modulator)
                self.phase_left += phase_increment_left
                if self.phase_left > 2 * np.pi:
                    self.phase_left -= 2 * np.pi

                # Modulate right channel
                right_signal[i] = np.sin(self.phase_right + modulator)
                self.phase_right += phase_increment_right
                if self.phase_right > 2 * np.pi:
                    self.phase_right -= 2 * np.pi

                self.phase_modulator += phase_increment_mod
                if self.phase_modulator > 2 * np.pi:
                    self.phase_modulator -= 2 * np.pi

        # Add noise for high chaos
        if self.noise_amount > 0.01:
            noise = np.random.randn(frames) * self.noise_amount * 0.3
            left_signal += noise
            right_signal += noise

        # Apply granular chopping for very high chaos
        if self.chaos_level > 0.7:
            grain_size = int(0.02 * self.sample_rate)  # 20ms grains
            for i in range(0, frames, grain_size):
                end = min(i + grain_size, frames)
                if np.random.rand() > 0.5:
                    left_signal[i:end] *= 0.2
                    right_signal[i:end] *= 0.2

        # Apply amplitude
        left_signal *= self.amplitude
        right_signal *= self.amplitude

        # Apply stereo pan
        # Pan: -1.0 = full left, 0.0 = center, 1.0 = full right
        pan_normalized = (self.pan + 1.0) / 2.0  # Convert to 0-1
        left_gain = np.sqrt(1.0 - pan_normalized)
        right_gain = np.sqrt(pan_normalized)

        left_signal *= left_gain
        right_signal *= right_gain

        # Clip to prevent distortion
        left_signal = np.clip(left_signal, -1.0, 1.0)
        right_signal = np.clip(right_signal, -1.0, 1.0)

        # Output stereo
        outdata[:, 0] = left_signal
        outdata[:, 1] = right_signal

    def start(self) -> bool:
        """Start audio engine"""
        if self.is_running:
            return True

        try:
            # Create audio stream
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=2,
                callback=self._audio_callback,
                dtype='float32'
            )

            self.stream.start()
            self.is_running = True
            print("✅ Real audio started (sounddevice)")
            return True

        except Exception as e:
            print(f"❌ Failed to start audio: {e}")
            return False

    def stop(self):
        """Stop audio engine"""
        if not self.is_running:
            return

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()

            self.is_running = False
            print("✓ Real audio stopped")

        except Exception as e:
            print(f"⚠️  Error stopping audio: {e}")

    def update(self, audio_params: Dict, pan: float = 0.0):
        """
        Update audio synthesis parameters

        Args:
            audio_params: Dictionary with synthesis parameters
            pan: Stereo pan (-1.0 to 1.0)
        """
        # Update parameters (thread-safe for reading in callback)
        self.base_freq = audio_params.get('base_freq', 100.0)
        self.binaural_diff = audio_params.get('binaural_diff', 5.0)
        self.lfo_rate = audio_params.get('lfo_rate', 0.0)
        self.lfo_depth = audio_params.get('lfo_depth', 0.0)
        self.fm_amount = audio_params.get('fm_amount', 0.0)
        self.noise_amount = audio_params.get('noise_amount', 0.0)
        self.amplitude = audio_params.get('amplitude', 0.3)
        self.chaos_level = audio_params.get('chaos_level', 0.0)
        self.pan = np.clip(pan, -1.0, 1.0)

    def get_waveform(self, duration: float = 0.05) -> np.ndarray:
        """
        Generate a waveform snapshot for visualization

        Args:
            duration: Duration in seconds

        Returns:
            Waveform array (mono)
        """
        num_samples = int(duration * self.sample_rate)

        # Generate simple waveform for visualization
        t = np.linspace(0, duration, num_samples)

        # Base sine wave
        waveform = np.sin(2 * np.pi * self.base_freq * t)

        # Add binaural beat component
        waveform += np.sin(2 * np.pi * (self.base_freq + self.binaural_diff) * t)

        # Apply LFO if active
        if self.lfo_rate > 0.01:
            lfo = np.sin(2 * np.pi * self.lfo_rate * t) * self.lfo_depth * 0.3 + 1.0
            waveform *= lfo

        # Add noise if present
        if self.noise_amount > 0.01:
            waveform += np.random.randn(num_samples) * self.noise_amount * 0.3

        # Apply amplitude
        waveform *= self.amplitude

        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * 0.8

        return waveform

    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'mode': 'REAL',
            'is_running': self.is_running,
            'sample_rate': self.sample_rate,
            'backend': 'sounddevice'
        }
