"""
Generative Audio Engine
Synthesizes real-time audio based on chaos parameters

Supports two modes:
1. SIMULATION mode (no Pyo required) - generates mock audio data for visualization
2. REAL mode (Pyo installed) - generates actual audio output

Audio Architecture:
- BiauralDroneGenerator: Base harmonic drone (100Hz + 105Hz)
- RippleModulator: Tremolo/vibrato effect for gentle motion
- ScatterGenerator: FM synthesis and granular effects for chaos
- SpatialPanner: Stereo positioning based on body position
"""

import numpy as np
from typing import Dict, Optional
import time

# Try to import Pyo
try:
    from pyo import *
    PYO_AVAILABLE = True
except ImportError:
    PYO_AVAILABLE = False
    print("⚠️  Pyo not installed - running in SIMULATION mode")
    print("   Install Pyo for real audio: pip3 install pyo")


class AudioEngine:
    """
    Main audio synthesis engine
    Generates audio based on chaos parameters
    """

    def __init__(self, sample_rate: int = 44100, buffer_size: int = 512):
        """
        Initialize audio engine

        Args:
            sample_rate: Audio sample rate in Hz
            buffer_size: Audio buffer size in samples
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.mode = "REAL" if PYO_AVAILABLE else "SIMULATION"

        # Audio state
        self.is_running = False
        self.current_params = {}

        # Pyo server (if available)
        self.server = None
        self.drone = None
        self.modulator = None

        # Simulation data
        self.sim_time = 0.0
        self.sim_waveform = np.zeros(buffer_size)

        print(f"🔊 Audio Engine initialized in {self.mode} mode")

    def start(self) -> bool:
        """
        Start audio engine

        Returns:
            True if started successfully
        """
        if self.mode == "REAL":
            return self._start_real_audio()
        else:
            return self._start_simulation()

    def stop(self):
        """Stop audio engine"""
        if self.mode == "REAL":
            self._stop_real_audio()
        else:
            self._stop_simulation()

    def update(self, audio_params: Dict, pan: float = 0.0):
        """
        Update audio synthesis parameters

        Args:
            audio_params: Dictionary with synthesis parameters
            pan: Stereo pan (-1.0 to 1.0)
        """
        self.current_params = audio_params

        if self.mode == "REAL":
            self._update_real_audio(audio_params, pan)
        else:
            self._update_simulation(audio_params, pan)

    def get_waveform(self, duration: float = 0.05) -> np.ndarray:
        """
        Get current audio waveform for visualization

        Args:
            duration: Duration of waveform in seconds

        Returns:
            Waveform array
        """
        num_samples = int(duration * self.sample_rate)

        if self.mode == "REAL":
            return self._get_real_waveform(num_samples)
        else:
            return self._get_simulated_waveform(num_samples)

    # ========== REAL AUDIO MODE (Pyo) ==========

    def _start_real_audio(self) -> bool:
        """Start Pyo audio server"""
        try:
            # Create server
            self.server = Server(sr=self.sample_rate, buffersize=self.buffer_size)
            self.server.boot()
            self.server.start()

            # Create binaural drone
            base_freq = 100
            binaural_diff = 5

            # Left channel: base frequency
            left = Sine(freq=base_freq, mul=0.3)

            # Right channel: base + difference (creates binaural beat)
            right = Sine(freq=base_freq + binaural_diff, mul=0.3)

            # LFO for tremolo/ripple effect
            self.lfo = Sine(freq=0, mul=0.5, add=0.5)

            # Apply LFO to amplitude
            left_mod = left * self.lfo
            right_mod = right * self.lfo

            # Pan object for spatial positioning
            self.panner = Pan(left_mod, outs=2, pan=0.5)

            # Output
            self.drone = self.panner.out()

            self.is_running = True
            print("✓ Real audio started")
            return True

        except Exception as e:
            print(f"❌ Failed to start real audio: {e}")
            return False

    def _stop_real_audio(self):
        """Stop Pyo audio server"""
        if self.server:
            self.server.stop()
            self.server.shutdown()
            self.is_running = False
            print("✓ Real audio stopped")

    def _update_real_audio(self, params: Dict, pan: float):
        """Update Pyo synthesis parameters"""
        if not self.is_running or not self.server:
            return

        try:
            # Update frequencies
            base_freq = params.get('base_freq', 100)
            binaural_diff = params.get('binaural_diff', 5)

            # Update LFO (tremolo/ripple)
            lfo_rate = params.get('lfo_rate', 0)
            self.lfo.setFreq(lfo_rate)

            # Update pan
            pan_normalized = (pan + 1.0) / 2.0  # Convert -1,1 to 0,1
            if self.panner:
                self.panner.setPan(pan_normalized)

            # Note: Full implementation would include FM synthesis,
            # granular synthesis, and noise generation here

        except Exception as e:
            print(f"⚠️  Audio update error: {e}")

    def _get_real_waveform(self, num_samples: int) -> np.ndarray:
        """Get waveform from Pyo for visualization"""
        # This is a simplified version
        # In full implementation, we'd capture actual audio buffer
        return self._get_simulated_waveform(num_samples)

    # ========== SIMULATION MODE ==========

    def _start_simulation(self) -> bool:
        """Start simulation mode"""
        self.is_running = True
        self.sim_time = 0.0
        print("✓ Simulation audio started (visual only)")
        return True

    def _stop_simulation(self):
        """Stop simulation mode"""
        self.is_running = False
        print("✓ Simulation audio stopped")

    def _update_simulation(self, params: Dict, pan: float):
        """Update simulation parameters"""
        # Just store params for waveform generation
        pass

    def _get_simulated_waveform(self, num_samples: int) -> np.ndarray:
        """
        Generate simulated waveform for visualization
        Mimics what the real audio would look like
        """
        if not self.current_params:
            return np.zeros(num_samples)

        # Extract parameters
        base_freq = self.current_params.get('base_freq', 100)
        lfo_rate = self.current_params.get('lfo_rate', 0)
        lfo_depth = self.current_params.get('lfo_depth', 0)
        fm_amount = self.current_params.get('fm_amount', 0)
        noise_amount = self.current_params.get('noise_amount', 0)
        chaos = self.current_params.get('chaos_level', 0)

        # Time array
        t = np.linspace(self.sim_time, self.sim_time + num_samples / self.sample_rate, num_samples)
        self.sim_time += num_samples / self.sample_rate

        # Generate base sine wave
        waveform = np.sin(2 * np.pi * base_freq * t)

        # Add binaural beat (phase-shifted second tone)
        binaural_diff = self.current_params.get('binaural_diff', 5)
        waveform += np.sin(2 * np.pi * (base_freq + binaural_diff) * t)

        # Apply LFO (tremolo) if present
        if lfo_rate > 0 and lfo_depth > 0:
            lfo = np.sin(2 * np.pi * lfo_rate * t)
            amplitude_mod = 1.0 + (lfo * lfo_depth * 0.3)
            waveform *= amplitude_mod

        # Apply FM synthesis for chaos
        if fm_amount > 0:
            modulator = np.sin(2 * np.pi * (base_freq * 2) * t)
            waveform = np.sin(2 * np.pi * base_freq * t + modulator * fm_amount * 0.01)

        # Add noise for high chaos
        if noise_amount > 0:
            noise = np.random.randn(num_samples) * noise_amount * 0.5
            waveform += noise

        # Apply granular effect (chopping) for high chaos
        if chaos > 0.7:
            grain_size = int(self.current_params.get('grain_size', 50) * self.sample_rate / 1000)
            if grain_size > 0:
                # Create grain envelope
                for i in range(0, num_samples, grain_size):
                    end = min(i + grain_size, num_samples)
                    # Random silence gaps
                    if np.random.rand() > 0.5:
                        waveform[i:end] *= 0.2

        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform))

        # Apply amplitude
        amplitude = self.current_params.get('amplitude', 0.3)
        waveform *= amplitude

        return waveform

    def is_available(self) -> bool:
        """Check if engine is available"""
        return True  # Simulation always works

    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'mode': self.mode,
            'pyo_available': PYO_AVAILABLE,
            'is_running': self.is_running,
            'sample_rate': self.sample_rate,
            'current_params': self.current_params
        }


class WaveformVisualizer:
    """
    Visualizes audio waveform and spectrum
    """

    def __init__(self, width: int = 800, height: int = 200):
        """
        Initialize visualizer

        Args:
            width: Visualization width in pixels
            height: Visualization height in pixels
        """
        self.width = width
        self.height = height

    def render_waveform(self, waveform: np.ndarray) -> np.ndarray:
        """
        Render waveform as image

        Args:
            waveform: Audio waveform array

        Returns:
            BGR image of waveform
        """
        # Create blank image
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        if len(waveform) == 0:
            return img

        # Downsample waveform to fit width
        if len(waveform) > self.width:
            indices = np.linspace(0, len(waveform) - 1, self.width).astype(int)
            waveform = waveform[indices]

        # Normalize waveform to image height
        center = self.height // 2
        waveform_scaled = (waveform * center * 0.8).astype(int)

        # Draw waveform
        for i in range(len(waveform_scaled) - 1):
            x1 = int(i * self.width / len(waveform_scaled))
            x2 = int((i + 1) * self.width / len(waveform_scaled))
            y1 = center - waveform_scaled[i]
            y2 = center - waveform_scaled[i + 1]

            # Color based on amplitude
            amplitude = abs(waveform[i])
            color = self._amplitude_to_color(amplitude)

            cv2.line(img, (x1, y1), (x2, y2), color, 2)

        # Draw center line
        cv2.line(img, (0, center), (self.width, center), (50, 50, 50), 1)

        return img

    def render_spectrum(self, waveform: np.ndarray) -> np.ndarray:
        """
        Render frequency spectrum as image

        Args:
            waveform: Audio waveform array

        Returns:
            BGR image of spectrum
        """
        # Create blank image
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        if len(waveform) == 0:
            return img

        # Calculate FFT
        fft = np.fft.fft(waveform)
        magnitude = np.abs(fft[:len(fft) // 2])

        # Normalize
        if np.max(magnitude) > 0:
            magnitude = magnitude / np.max(magnitude)

        # Downsample to fit width
        if len(magnitude) > self.width:
            indices = np.linspace(0, len(magnitude) - 1, self.width).astype(int)
            magnitude = magnitude[indices]

        # Draw spectrum bars
        bar_width = max(1, self.width // len(magnitude))

        for i, mag in enumerate(magnitude):
            x = i * bar_width
            bar_height = int(mag * self.height * 0.9)

            # Color based on frequency (low = red, high = blue)
            color = self._frequency_to_color(i / len(magnitude))

            cv2.rectangle(
                img,
                (x, self.height - bar_height),
                (x + bar_width, self.height),
                color,
                -1
            )

        return img

    def _amplitude_to_color(self, amplitude: float) -> tuple:
        """Map amplitude to color"""
        # Low amplitude = blue, high = red
        amplitude = np.clip(amplitude, 0, 1)
        r = int(255 * amplitude)
        g = int(128 * (1 - amplitude))
        b = int(255 * (1 - amplitude))
        return (b, g, r)

    def _frequency_to_color(self, freq_norm: float) -> tuple:
        """Map frequency to color"""
        # Low freq = red, mid = green, high = blue
        if freq_norm < 0.33:
            # Red to yellow
            ratio = freq_norm / 0.33
            return (0, int(255 * ratio), 255)
        elif freq_norm < 0.66:
            # Yellow to green
            ratio = (freq_norm - 0.33) / 0.33
            return (0, 255, int(255 * (1 - ratio)))
        else:
            # Green to blue
            ratio = (freq_norm - 0.66) / 0.34
            return (int(255 * ratio), 255, 0)


# Import cv2 for visualization
try:
    import cv2
except ImportError:
    pass
