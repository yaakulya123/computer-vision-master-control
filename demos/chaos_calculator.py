"""
Chaos Score Calculator
Converts motion metrics into a unified chaos score (0.0 to 1.0)

Chaos Score Mapping:
- 0.0 = Stillness (frozen, no movement)
- 0.5 = Gentle motion (arm waving, standing still)
- 1.0 = High motion (walking, running, jumping)

Features:
- Smooth transitions with configurable decay
- Differentiation between global and local motion
- Exponential smoothing for natural feel
"""

import numpy as np
from typing import Dict, Optional
import time


class ChaosCalculator:
    """
    Calculates chaos score from motion metrics with smooth transitions
    """

    def __init__(
        self,
        decay_time: float = 2.5,
        local_weight: float = 0.6,
        global_weight: float = 0.4
    ):
        """
        Initialize chaos calculator

        Args:
            decay_time: Time in seconds for chaos to decay back to 0 (healing time)
            local_weight: Weight for local motion (arm waving) in final score
            global_weight: Weight for global motion (walking) in final score
        """
        self.decay_time = decay_time
        self.local_weight = local_weight
        self.global_weight = global_weight

        # Current chaos score
        self.current_chaos = 0.0

        # Target chaos score (what we're moving towards)
        self.target_chaos = 0.0

        # Timestamp of last update
        self.last_update_time = time.time()

        # Motion type tracking
        self.current_motion_type = 'still'

        # History for smoothing
        self.chaos_history = []
        self.max_history = 10

    def calculate_raw_chaos(
        self,
        motion_energy: float,
        global_velocity: float,
        motion_type: str
    ) -> float:
        """
        Calculate raw chaos score from motion metrics

        Args:
            motion_energy: Total motion energy (0-1)
            global_velocity: Center of mass velocity (0-1)
            motion_type: Motion classification ('still', 'local', 'global')

        Returns:
            Raw chaos score (0-1)
        """
        if motion_type == 'still':
            # Completely still - chaos decays to 0
            return 0.0

        elif motion_type == 'local':
            # Local motion (waving) - medium chaos
            # Weighted towards motion energy, less on velocity
            chaos = (motion_energy * self.local_weight +
                    global_velocity * (1 - self.local_weight))

            # Clamp to mid-range for local motion (0.3 - 0.7)
            return np.clip(chaos * 0.8, 0.3, 0.7)

        else:  # motion_type == 'global'
            # Global motion (walking/running) - high chaos
            # Weighted combination favoring velocity
            chaos = (motion_energy * self.local_weight +
                    global_velocity * self.global_weight * 1.5)

            # Allow full range but emphasize high values
            return np.clip(chaos * 1.2, 0.5, 1.0)

    def apply_exponential_smoothing(
        self,
        current: float,
        target: float,
        alpha: float = 0.3
    ) -> float:
        """
        Apply exponential smoothing for natural transitions

        Args:
            current: Current value
            target: Target value
            alpha: Smoothing factor (0-1, higher = faster response)

        Returns:
            Smoothed value
        """
        return alpha * target + (1 - alpha) * current

    def apply_decay(self, current: float, delta_time: float) -> float:
        """
        Apply time-based decay when motion stops

        Args:
            current: Current chaos score
            delta_time: Time since last update

        Returns:
            Decayed chaos score
        """
        if self.current_motion_type == 'still':
            # Calculate decay factor (exponential decay)
            decay_rate = 1.0 / self.decay_time
            decay_factor = np.exp(-decay_rate * delta_time)

            # Apply decay
            return current * decay_factor
        else:
            # No decay during active motion
            return current

    def update(self, motion_metrics: Dict) -> float:
        """
        Update chaos score based on new motion metrics

        Args:
            motion_metrics: Dictionary containing motion analysis results
                - motion_energy: float (0-1)
                - global_velocity: float (0-1)
                - motion_type: str ('still', 'local', 'global')

        Returns:
            Updated chaos score (0-1)
        """
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Extract metrics
        motion_energy = motion_metrics.get('motion_energy', 0.0)
        global_velocity = motion_metrics.get('global_velocity', 0.0)
        motion_type = motion_metrics.get('motion_type', 'still')

        # Update motion type
        self.current_motion_type = motion_type

        # Calculate raw target chaos
        self.target_chaos = self.calculate_raw_chaos(
            motion_energy,
            global_velocity,
            motion_type
        )

        # Apply exponential smoothing
        if motion_type == 'still':
            # Slower response when decaying
            alpha = 0.1
        else:
            # Faster response when motion detected
            alpha = 0.4

        smoothed_chaos = self.apply_exponential_smoothing(
            self.current_chaos,
            self.target_chaos,
            alpha
        )

        # Apply time-based decay
        smoothed_chaos = self.apply_decay(smoothed_chaos, delta_time)

        # Update current chaos
        self.current_chaos = np.clip(smoothed_chaos, 0.0, 1.0)

        # Update history
        self.chaos_history.append(self.current_chaos)
        if len(self.chaos_history) > self.max_history:
            self.chaos_history.pop(0)

        return self.current_chaos

    def get_chaos_state(self) -> Dict:
        """
        Get detailed chaos state information

        Returns:
            Dictionary with chaos state details
        """
        # Determine state category
        if self.current_chaos < 0.2:
            state = 'Still (Ethereal Drone)'
            color = (0, 255, 0)  # Green
        elif self.current_chaos < 0.5:
            state = 'Gentle Motion (Ripple)'
            color = (0, 255, 255)  # Yellow
        elif self.current_chaos < 0.8:
            state = 'Active Motion (Rising Tension)'
            color = (0, 165, 255)  # Orange
        else:
            state = 'High Chaos (Scatter/Shatter)'
            color = (0, 0, 255)  # Red

        return {
            'chaos_score': self.current_chaos,
            'target_chaos': self.target_chaos,
            'motion_type': self.current_motion_type,
            'state': state,
            'color': color,
            'history': self.chaos_history.copy()
        }

    def get_audio_parameters(self) -> Dict:
        """
        Get audio synthesis parameters based on chaos score

        Returns:
            Dictionary with audio parameters for synthesis
        """
        chaos = self.current_chaos

        # Base frequency (Hz) - increases with chaos
        # Still: 100Hz, High chaos: 800Hz
        base_freq = 100 + (chaos * 700)

        # Binaural beat difference (Hz) - decreases with chaos
        # Still: 5Hz (relaxing), High chaos: 0.5Hz (dissonant)
        binaural_diff = 5.0 - (chaos * 4.5)

        # Amplitude/Volume - slightly increases with chaos
        amplitude = 0.3 + (chaos * 0.4)

        # LFO (tremolo) rate (Hz) - increases with chaos
        # Still: 0Hz (no tremolo), Gentle: 3-6Hz, High: 10Hz+
        lfo_rate = chaos * 12.0

        # LFO depth - increases in mid-range (gentle motion)
        # Peak at chaos=0.5 for max ripple effect
        lfo_depth = 4.0 * chaos * (1.0 - chaos)  # Parabolic curve

        # FM (frequency modulation) amount - increases with chaos
        # Still: 0 (pure tone), High: strong FM (distorted)
        fm_amount = chaos ** 2 * 1000  # Exponential increase

        # Noise amount - increases dramatically with high chaos
        noise_amount = max(0, (chaos - 0.5) * 2.0) ** 1.5

        # Grain rate for granular synthesis - increases with chaos
        # Still: 0 (continuous), High: 100+ grains/sec (scattered)
        grain_rate = chaos * 100

        # Grain size (ms) - decreases with chaos
        # Still: long grains, High: tiny grains (shattered)
        grain_size = 200 - (chaos * 180)  # 200ms to 20ms

        return {
            'base_freq': base_freq,
            'binaural_diff': binaural_diff,
            'amplitude': amplitude,
            'lfo_rate': lfo_rate,
            'lfo_depth': lfo_depth,
            'fm_amount': fm_amount,
            'noise_amount': noise_amount,
            'grain_rate': grain_rate,
            'grain_size': grain_size,
            'chaos_level': chaos
        }

    def reset(self):
        """Reset calculator state"""
        self.current_chaos = 0.0
        self.target_chaos = 0.0
        self.last_update_time = time.time()
        self.current_motion_type = 'still'
        self.chaos_history = []


def map_position_to_pan(x_position: int, width: int) -> float:
    """
    Map X position to stereo pan (-1.0 to 1.0)

    Args:
        x_position: X coordinate in frame
        width: Frame width

    Returns:
        Pan value (-1.0 = full left, 0.0 = center, 1.0 = full right)
    """
    # Normalize to 0-1
    normalized = x_position / width

    # Map to -1 to 1
    pan = (normalized * 2.0) - 1.0

    return np.clip(pan, -1.0, 1.0)
