#!/usr/bin/env python3
"""
RealSense D435 - Generative Audio Demo
Body-responsive real-time audio synthesis

Concept: "The Heal Mechanic"
- Stillness creates harmonic drones (binaural beats)
- Movement creates sonic chaos (scattered beeps/static)
- Smooth 2-3 second transition when returning to stillness

Controls:
- 'q': Quit
- 's': Save snapshot
- 'h': Toggle motion heatmap
- 'm': Toggle chaos meter
- 'w': Toggle waveform display
- 'a': Toggle audio engine on/off
- ' ' (space): Reset chaos to zero
"""

import cv2
import numpy as np
import sys
import os
from datetime import datetime
import time
from typing import Dict

# Import our modules
from motion_analyzer import MotionAnalyzer
from chaos_calculator import ChaosCalculator, map_position_to_pan
from audio_engine_sounddevice import SimpleAudioEngine
from audio_engine import WaveformVisualizer

REALSENSE_CAMERA_INDEX = 0


class GenerativeAudioDemo:
    """Main demo class integrating all components"""

    def __init__(self, camera_index: int = REALSENSE_CAMERA_INDEX):
        """
        Initialize demo

        Args:
            camera_index: Camera index to use
        """
        self.camera_index = camera_index

        # Initialize components
        print("🎵 Initializing Generative Audio System...")
        print("=" * 60)

        self.motion_analyzer = MotionAnalyzer(width=320, height=240)
        self.chaos_calculator = ChaosCalculator(decay_time=2.5)
        self.audio_engine = SimpleAudioEngine()
        self.waveform_viz = WaveformVisualizer(width=800, height=150)

        print("✓ Motion analyzer ready")
        print("✓ Chaos calculator ready")
        print("✓ Audio engine ready")

        # Display settings
        self.show_heatmap = True
        self.show_chaos_meter = True
        self.show_waveform = True
        self.audio_enabled = False  # Start with audio off

        # Camera
        self.cap = None

        # Stats
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0

    def initialize_camera(self) -> bool:
        """Initialize camera"""
        print("\n📹 Initializing camera...")

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"❌ Cannot open camera {self.camera_index}")
            return False

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Get actual resolution
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"✓ Camera initialized at {width}x{height}")
        return True

    def draw_hud(self, frame: np.ndarray, chaos_state: Dict, motion_metrics: Dict) -> np.ndarray:
        """
        Draw heads-up display with all information

        Args:
            frame: Input frame
            chaos_state: Chaos state dictionary
            motion_metrics: Motion metrics dictionary

        Returns:
            Frame with HUD overlay
        """
        h, w = frame.shape[:2]

        # Semi-transparent overlay for text background
        overlay = frame.copy()

        # Top-left: Status panel
        status_panel_height = 180
        cv2.rectangle(overlay, (0, 0), (400, status_panel_height), (0, 0, 0), -1)

        # Title
        cv2.putText(
            overlay,
            "GENERATIVE AUDIO SYSTEM",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        # Chaos score with color
        chaos_score = chaos_state['chaos_score']
        chaos_color = chaos_state['color']
        cv2.putText(
            overlay,
            f"Chaos: {chaos_score:.3f}",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            chaos_color,
            2
        )

        # State description
        cv2.putText(
            overlay,
            chaos_state['state'],
            (10, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        # Motion metrics
        motion_energy = motion_metrics.get('motion_energy', 0)
        global_velocity = motion_metrics.get('global_velocity', 0)
        motion_type = motion_metrics.get('motion_type', 'still')

        cv2.putText(
            overlay,
            f"Motion Energy: {motion_energy:.3f}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        cv2.putText(
            overlay,
            f"Velocity: {global_velocity:.3f}",
            (10, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        cv2.putText(
            overlay,
            f"Type: {motion_type.upper()}",
            (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        # FPS
        cv2.putText(
            overlay,
            f"FPS: {self.fps:.1f}",
            (10, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 150, 150),
            1
        )

        # Audio status indicator (top-right)
        audio_status = "AUDIO: ON" if self.audio_enabled else "AUDIO: OFF"
        audio_color = (0, 255, 0) if self.audio_enabled else (0, 0, 255)
        cv2.rectangle(overlay, (w - 200, 0), (w, 40), (0, 0, 0), -1)
        cv2.putText(
            overlay,
            audio_status,
            (w - 190, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            audio_color,
            2
        )

        # Controls (bottom-left)
        controls = [
            "CONTROLS:",
            "Q: Quit  S: Save  SPACE: Reset",
            "H: Heatmap  M: Meter  W: Wave",
            "A: Audio Toggle"
        ]

        controls_y = h - 100
        cv2.rectangle(overlay, (0, h - 110), (400, h), (0, 0, 0), -1)

        for i, text in enumerate(controls):
            cv2.putText(
                overlay,
                text,
                (10, controls_y + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (200, 200, 200),
                1
            )

        # Blend overlay
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        return frame

    def draw_chaos_meter(self, frame: np.ndarray, chaos_state: Dict) -> np.ndarray:
        """
        Draw vertical chaos meter on right side

        Args:
            frame: Input frame
            chaos_state: Chaos state dictionary

        Returns:
            Frame with chaos meter
        """
        if not self.show_chaos_meter:
            return frame

        h, w = frame.shape[:2]

        # Meter dimensions
        meter_width = 50
        meter_height = 300
        meter_x = w - meter_width - 20
        meter_y = (h - meter_height) // 2

        # Background
        cv2.rectangle(
            frame,
            (meter_x, meter_y),
            (meter_x + meter_width, meter_y + meter_height),
            (50, 50, 50),
            -1
        )

        # Border
        cv2.rectangle(
            frame,
            (meter_x, meter_y),
            (meter_x + meter_width, meter_y + meter_height),
            (200, 200, 200),
            2
        )

        # Fill based on chaos level
        chaos = chaos_state['chaos_score']
        fill_height = int(chaos * meter_height)
        fill_y = meter_y + meter_height - fill_height

        # Gradient fill
        for i in range(fill_height):
            y = fill_y + i
            # Color gradient from green -> yellow -> red
            ratio = i / meter_height
            if ratio < 0.5:
                color = (0, 255, int(255 * (ratio * 2)))  # Green to yellow
            else:
                color = (0, int(255 * (2 - ratio * 2)), 255)  # Yellow to red

            cv2.line(
                frame,
                (meter_x + 2, y),
                (meter_x + meter_width - 2, y),
                color,
                1
            )

        # Labels
        labels = ["1.0", "0.8", "0.6", "0.4", "0.2", "0.0"]
        for i, label in enumerate(labels):
            y = meter_y + int(i * meter_height / 5)
            cv2.putText(
                frame,
                label,
                (meter_x - 45, y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )

        # Current value marker
        marker_y = meter_y + meter_height - int(chaos * meter_height)
        cv2.line(
            frame,
            (meter_x - 10, marker_y),
            (meter_x + meter_width + 10, marker_y),
            (255, 255, 255),
            2
        )

        return frame

    def draw_motion_heatmap(
        self,
        frame: np.ndarray,
        motion_metrics: Dict
    ) -> np.ndarray:
        """
        Draw motion heatmap overlay

        Args:
            frame: Input frame
            motion_metrics: Motion metrics dictionary

        Returns:
            Frame with heatmap overlay
        """
        if not self.show_heatmap:
            return frame

        flow = motion_metrics.get('flow')
        if flow is None:
            return frame

        # Create heatmap
        heatmap = self.motion_analyzer.create_motion_heatmap(flow)

        # Resize to match frame
        h, w = frame.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (w, h))

        # Blend with frame
        blended = cv2.addWeighted(frame, 0.7, heatmap_resized, 0.3, 0)

        return blended

    def draw_waveform(self, frame: np.ndarray, waveform: np.ndarray) -> np.ndarray:
        """
        Draw audio waveform at bottom

        Args:
            frame: Input frame
            waveform: Audio waveform array

        Returns:
            Frame with waveform
        """
        if not self.show_waveform:
            return frame

        h, w = frame.shape[:2]

        # Render waveform
        waveform_img = self.waveform_viz.render_waveform(waveform)

        # Resize to fit frame width
        waveform_height = 100
        waveform_resized = cv2.resize(waveform_img, (w, waveform_height))

        # Composite at bottom
        frame[h - waveform_height:h, :] = cv2.addWeighted(
            frame[h - waveform_height:h, :],
            0.5,
            waveform_resized,
            0.5,
            0
        )

        # Label
        cv2.putText(
            frame,
            "AUDIO WAVEFORM",
            (w // 2 - 100, h - waveform_height + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        return frame

    def run(self) -> bool:
        """
        Run the main demo loop

        Returns:
            True if successful
        """
        if not self.initialize_camera():
            return False

        # Start audio engine
        if not self.audio_engine.start():
            print("⚠️  Audio engine failed to start, continuing without audio")

        print("\n" + "=" * 60)
        print("✓ System ready! Starting demo...")
        print("=" * 60)
        print("\nTIP: Press 'A' to enable audio synthesis")
        print("     Move around to create sound!")
        print("\nStarting in 2 seconds...")
        time.sleep(2)

        snapshot_count = 0

        try:
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break

                self.frame_count += 1

                # Calculate FPS
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.start_time
                    self.fps = self.frame_count / elapsed

                # Analyze motion
                motion_metrics = self.motion_analyzer.analyze_frame(frame)

                # Calculate chaos score
                chaos_score = self.chaos_calculator.update(motion_metrics)

                # Get chaos state
                chaos_state = self.chaos_calculator.get_chaos_state()

                # Get audio parameters
                audio_params = self.chaos_calculator.get_audio_parameters()

                # Calculate stereo pan from X position
                center = motion_metrics['center']
                pan = map_position_to_pan(center[0], self.motion_analyzer.width)

                # Update audio engine
                if self.audio_enabled:
                    self.audio_engine.update(audio_params, pan)

                # Get waveform for visualization
                waveform = self.audio_engine.get_waveform()

                # Draw visualizations
                display_frame = frame.copy()

                # Motion heatmap
                display_frame = self.draw_motion_heatmap(display_frame, motion_metrics)

                # Chaos meter
                display_frame = self.draw_chaos_meter(display_frame, chaos_state)

                # Waveform
                display_frame = self.draw_waveform(display_frame, waveform)

                # HUD
                display_frame = self.draw_hud(display_frame, chaos_state, motion_metrics)

                # Show frame
                cv2.imshow('Generative Audio System - Body-Responsive Sound', display_frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    print("\n\nStopping...")
                    break

                elif key == ord('s'):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    snapshot_path = f"../outputs/captures/generative_audio_{timestamp}.jpg"
                    cv2.imwrite(snapshot_path, display_frame)
                    print(f"  📸 Snapshot saved: {snapshot_path}")
                    snapshot_count += 1

                elif key == ord('h'):
                    self.show_heatmap = not self.show_heatmap
                    print(f"  Motion heatmap: {'ON' if self.show_heatmap else 'OFF'}")

                elif key == ord('m'):
                    self.show_chaos_meter = not self.show_chaos_meter
                    print(f"  Chaos meter: {'ON' if self.show_chaos_meter else 'OFF'}")

                elif key == ord('w'):
                    self.show_waveform = not self.show_waveform
                    print(f"  Waveform: {'ON' if self.show_waveform else 'OFF'}")

                elif key == ord('a'):
                    self.audio_enabled = not self.audio_enabled
                    print(f"  🔊 Audio: {'ON' if self.audio_enabled else 'OFF'}")

                elif key == ord(' '):  # Space bar
                    self.chaos_calculator.reset()
                    print("  🔄 Chaos reset to 0")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

        finally:
            # Cleanup
            self.cleanup()

            # Print summary
            print("\n" + "=" * 60)
            print("Session Summary")
            print("=" * 60)
            print(f"Total frames: {self.frame_count}")
            print(f"Average FPS: {self.fps:.1f}")
            print(f"Snapshots saved: {snapshot_count}")

            # Motion statistics
            stats = self.motion_analyzer.get_motion_statistics()
            print(f"\nMotion Statistics:")
            print(f"  Mean energy: {stats['mean']:.3f}")
            print(f"  Max energy: {stats['max']:.3f}")
            print(f"  Std deviation: {stats['std']:.3f}")

            print("=" * 60)

        return True

    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()

        self.audio_engine.stop()
        cv2.destroyAllWindows()


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  RealSense D435 - Generative Audio Demo")
    print("  Body-Responsive Real-Time Sound Synthesis")
    print("=" * 60)
    print("\nConcept: 'The Heal Mechanic'")
    print("  • Stillness → Ethereal harmonic drone (healing)")
    print("  • Gentle motion → Rippling vibrato (meditative)")
    print("  • High motion → Scattered chaos (intensity)")
    print("=" * 60)

    # Create output directory
    os.makedirs("../outputs/captures", exist_ok=True)

    # Camera selection
    print("\nAvailable cameras:")
    print("  0 - Camera 0 (RealSense D435 RGB - RECOMMENDED)")
    print("  1 - Camera 1 (Laptop FaceTime Camera)")
    print("  2 - Camera 2 (iPhone Camera)")

    while True:
        try:
            choice = input("\nSelect camera index (0-2, default=0): ").strip()
            if choice == "":
                camera_index = 0
                break
            camera_index = int(choice)
            if 0 <= camera_index <= 2:
                break
            else:
                print("Please enter 0, 1, or 2")
        except ValueError:
            print("Please enter a valid number")

    # Create and run demo
    demo = GenerativeAudioDemo(camera_index=camera_index)
    success = demo.run()

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
        sys.exit(1)
