"""
Motion Analyzer Module
Analyzes video frames to detect motion patterns for audio generation

This module provides comprehensive motion analysis including:
- Dense Optical Flow (sophisticated movement tracking)
- Frame Delta (simple pixel differences)
- Center of Mass tracking
- Motion Energy calculation
- Movement classification (global vs local motion)
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Optional


class MotionAnalyzer:
    """
    Analyzes motion in video frames using optical flow and frame differencing
    """

    def __init__(self, width: int = 640, height: int = 480):
        """
        Initialize the motion analyzer

        Args:
            width: Frame width for processing (smaller = faster)
            height: Frame height for processing
        """
        self.width = width
        self.height = height

        # Previous frame for comparison
        self.prev_gray = None

        # Previous center of mass for velocity calculation
        self.prev_center = None

        # Optical flow parameters
        self.flow_params = {
            'pyr_scale': 0.5,
            'levels': 3,
            'winsize': 15,
            'iterations': 3,
            'poly_n': 5,
            'poly_sigma': 1.2,
            'flags': 0
        }

        # Motion history
        self.motion_history = []
        self.max_history = 30  # Keep last 30 frames (1 second at 30fps)

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for motion analysis

        Args:
            frame: Input BGR frame

        Returns:
            Grayscale frame resized for processing
        """
        # Resize for faster processing
        resized = cv2.resize(frame, (self.width, self.height))

        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Apply slight blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        return blurred

    def calculate_optical_flow(self, current_gray: np.ndarray) -> Optional[np.ndarray]:
        """
        Calculate dense optical flow between frames

        Args:
            current_gray: Current grayscale frame

        Returns:
            Flow array (height, width, 2) or None if no previous frame
        """
        if self.prev_gray is None:
            return None

        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray,
            current_gray,
            None,
            **self.flow_params
        )

        return flow

    def calculate_frame_delta(self, current_gray: np.ndarray) -> Optional[np.ndarray]:
        """
        Calculate simple frame difference

        Args:
            current_gray: Current grayscale frame

        Returns:
            Difference array or None if no previous frame
        """
        if self.prev_gray is None:
            return None

        # Calculate absolute difference
        delta = cv2.absdiff(self.prev_gray, current_gray)

        # Threshold to reduce noise
        _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)

        return thresh

    def calculate_center_of_mass(self, motion_mask: np.ndarray) -> Tuple[int, int]:
        """
        Calculate center of mass of motion

        Args:
            motion_mask: Binary motion mask

        Returns:
            (x, y) center of mass
        """
        # Calculate moments
        moments = cv2.moments(motion_mask)

        # Calculate center of mass
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
        else:
            cx = self.width // 2
            cy = self.height // 2

        return cx, cy

    def calculate_motion_energy(self, flow: np.ndarray) -> float:
        """
        Calculate total motion energy from optical flow

        Args:
            flow: Optical flow array

        Returns:
            Motion energy value (normalized 0-1)
        """
        # Calculate magnitude of flow vectors
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)

        # Calculate average magnitude
        energy = np.mean(magnitude)

        # Normalize to 0-1 range (empirically tuned)
        normalized = np.clip(energy / 5.0, 0.0, 1.0)

        return normalized

    def calculate_global_velocity(self, current_center: Tuple[int, int]) -> float:
        """
        Calculate global velocity (whole body movement)

        Args:
            current_center: Current center of mass

        Returns:
            Velocity magnitude (normalized 0-1)
        """
        if self.prev_center is None:
            return 0.0

        # Calculate displacement
        dx = current_center[0] - self.prev_center[0]
        dy = current_center[1] - self.prev_center[1]

        # Calculate velocity magnitude
        velocity = np.sqrt(dx**2 + dy**2)

        # Normalize (empirically tuned - max velocity ~50 pixels/frame)
        normalized = np.clip(velocity / 50.0, 0.0, 1.0)

        return normalized

    def classify_motion_type(
        self,
        motion_energy: float,
        global_velocity: float,
        threshold: float = 0.3
    ) -> str:
        """
        Classify motion as still, local (waving), or global (walking)

        Args:
            motion_energy: Total motion energy
            global_velocity: Center of mass velocity
            threshold: Threshold for classification

        Returns:
            Motion type: 'still', 'local', or 'global'
        """
        if motion_energy < threshold * 0.5:
            return 'still'
        elif global_velocity < threshold and motion_energy > threshold:
            return 'local'  # High motion but low displacement = waving
        else:
            return 'global'  # High motion and displacement = walking

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Perform complete motion analysis on a frame

        Args:
            frame: Input BGR frame

        Returns:
            Dictionary containing all motion metrics
        """
        # Preprocess
        current_gray = self.preprocess_frame(frame)

        # Calculate optical flow
        flow = self.calculate_optical_flow(current_gray)

        # Calculate frame delta
        delta = self.calculate_frame_delta(current_gray)

        # Initialize results
        results = {
            'motion_energy': 0.0,
            'global_velocity': 0.0,
            'center': (self.width // 2, self.height // 2),
            'motion_type': 'still',
            'flow': None,
            'delta': None,
            'flow_visualization': None
        }

        if flow is not None:
            # Calculate motion energy
            motion_energy = self.calculate_motion_energy(flow)

            # Calculate center of mass (use delta for better mask)
            if delta is not None:
                center = self.calculate_center_of_mass(delta)
            else:
                center = (self.width // 2, self.height // 2)

            # Calculate global velocity
            global_velocity = self.calculate_global_velocity(center)

            # Classify motion type
            motion_type = self.classify_motion_type(motion_energy, global_velocity)

            # Update results
            results.update({
                'motion_energy': motion_energy,
                'global_velocity': global_velocity,
                'center': center,
                'motion_type': motion_type,
                'flow': flow,
                'delta': delta
            })

            # Create flow visualization
            results['flow_visualization'] = self.visualize_flow(flow)

            # Update history
            self.motion_history.append(motion_energy)
            if len(self.motion_history) > self.max_history:
                self.motion_history.pop(0)

            # Update previous values
            self.prev_center = center

        # Update previous frame
        self.prev_gray = current_gray

        return results

    def visualize_flow(self, flow: np.ndarray, step: int = 16) -> np.ndarray:
        """
        Create visualization of optical flow

        Args:
            flow: Optical flow array
            step: Sampling step for flow vectors

        Returns:
            Flow visualization as BGR image
        """
        # Create blank image
        vis = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Sample flow vectors
        h, w = flow.shape[:2]
        y, x = np.mgrid[step//2:h:step, step//2:w:step].reshape(2, -1).astype(int)
        fx, fy = flow[y, x].T

        # Calculate magnitude for coloring
        magnitude = np.sqrt(fx**2 + fy**2)

        # Normalize magnitude for color mapping
        if magnitude.max() > 0:
            magnitude_norm = (magnitude / magnitude.max() * 255).astype(np.uint8)
        else:
            magnitude_norm = magnitude.astype(np.uint8)

        # Draw flow vectors
        for i in range(len(x)):
            if magnitude[i] > 0.5:  # Only show significant motion
                # Start point
                pt1 = (x[i], y[i])

                # End point
                pt2 = (int(x[i] + fx[i]), int(y[i] + fy[i]))

                # Color based on magnitude (blue = slow, red = fast)
                color = cv2.applyColorMap(
                    np.array([[magnitude_norm[i]]], dtype=np.uint8),
                    cv2.COLORMAP_JET
                )[0, 0].tolist()

                # Draw arrow
                cv2.arrowedLine(vis, pt1, pt2, color, 1, tipLength=0.3)

        return vis

    def create_motion_heatmap(self, flow: np.ndarray) -> np.ndarray:
        """
        Create heatmap visualization of motion magnitude

        Args:
            flow: Optical flow array

        Returns:
            Heatmap as BGR image
        """
        # Calculate magnitude
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)

        # Normalize to 0-255
        normalized = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        normalized = normalized.astype(np.uint8)

        # Apply color map
        heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

        return heatmap

    def get_motion_statistics(self) -> Dict:
        """
        Get statistical summary of recent motion

        Returns:
            Dictionary with motion statistics
        """
        if not self.motion_history:
            return {
                'mean': 0.0,
                'max': 0.0,
                'min': 0.0,
                'std': 0.0
            }

        history = np.array(self.motion_history)

        return {
            'mean': float(np.mean(history)),
            'max': float(np.max(history)),
            'min': float(np.min(history)),
            'std': float(np.std(history))
        }

    def reset(self):
        """Reset analyzer state"""
        self.prev_gray = None
        self.prev_center = None
        self.motion_history = []
