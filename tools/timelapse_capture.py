#!/usr/bin/env python3
"""
RealSense D435 - Timelapse Capture Tool
Capture images at regular intervals and create timelapse videos
"""

import cv2
import sys
import time
import os
from datetime import datetime
import argparse

REALSENSE_CAMERA_INDEX = 0

def capture_timelapse(interval_seconds=5, duration_minutes=5, output_dir="timelapse"):
    """
    Capture timelapse images from the RealSense camera

    Args:
        interval_seconds: Time between captures in seconds
        duration_minutes: Total duration in minutes (0 = infinite)
        output_dir: Directory to save images
    """
    print("=" * 50)
    print("RealSense D435 - Timelapse Capture")
    print("=" * 50)
    print(f"\nSettings:")
    print(f"  Interval: {interval_seconds} seconds")
    print(f"  Duration: {duration_minutes} minutes" if duration_minutes > 0 else "  Duration: Infinite (press Ctrl+C to stop)")
    print(f"  Output: {output_dir}/")
    print()

    # Create output directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_dir = os.path.join(output_dir, f"timelapse_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)

    print(f"✓ Created session directory: {session_dir}")

    # Open camera
    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("✓ Camera opened successfully")
    print("\nStarting capture in 3 seconds...")
    print("Press Ctrl+C to stop anytime\n")
    time.sleep(3)

    # Capture settings
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60) if duration_minutes > 0 else float('inf')
    next_capture_time = start_time
    capture_count = 0

    # Info file
    info_file = os.path.join(session_dir, "timelapse_info.txt")
    with open(info_file, 'w') as f:
        f.write(f"Timelapse Session\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Interval: {interval_seconds} seconds\n")
        f.write(f"Duration: {duration_minutes} minutes\n" if duration_minutes > 0 else "Duration: Infinite\n")
        f.write(f"\nCaptures:\n")

    try:
        while time.time() < end_time:
            current_time = time.time()

            # Check if it's time to capture
            if current_time >= next_capture_time:
                # Skip a few frames to get fresh image
                for _ in range(5):
                    cap.read()

                # Capture frame
                ret, frame = cap.read()

                if ret:
                    # Save image
                    filename = f"frame_{capture_count:06d}.jpg"
                    filepath = os.path.join(session_dir, filename)
                    cv2.imwrite(filepath, frame)

                    capture_count += 1
                    elapsed = current_time - start_time

                    # Log capture
                    capture_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{capture_time}] Captured #{capture_count}: {filename} (elapsed: {elapsed:.0f}s)")

                    # Update info file
                    with open(info_file, 'a') as f:
                        f.write(f"{capture_count}: {filename} at {capture_time}\n")

                    # Display preview
                    preview = cv2.resize(frame, (640, 360))
                    cv2.putText(
                        preview,
                        f"Timelapse: {capture_count} frames",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    cv2.putText(
                        preview,
                        f"Elapsed: {int(elapsed)}s",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        1
                    )
                    cv2.imshow('Timelapse Preview', preview)
                    cv2.waitKey(1)

                else:
                    print("WARNING: Failed to capture frame")

                # Schedule next capture
                next_capture_time = current_time + interval_seconds

            # Small sleep to prevent busy waiting
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopping timelapse (user interrupted)...")

    finally:
        cap.release()
        cv2.destroyAllWindows()

        # Final stats
        total_time = time.time() - start_time
        print("\n" + "=" * 50)
        print("Timelapse Session Complete")
        print("=" * 50)
        print(f"Total captures: {capture_count}")
        print(f"Total duration: {total_time:.0f} seconds ({total_time/60:.1f} minutes)")
        print(f"Output directory: {session_dir}")
        print(f"Info file: {info_file}")
        print("=" * 50)

        # Update info file with final stats
        with open(info_file, 'a') as f:
            f.write(f"\nSession ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total captures: {capture_count}\n")
            f.write(f"Total duration: {total_time:.0f} seconds\n")

        # Ask about creating video
        if capture_count > 1:
            print("\nWould you like to create a timelapse video from these images?")
            print("Run: python3 create_timelapse_video.py " + session_dir)

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Capture timelapse images from RealSense D435 camera'
    )
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=5,
        help='Interval between captures in seconds (default: 5)'
    )
    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=5,
        help='Total duration in minutes (default: 5, use 0 for infinite)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='timelapse',
        help='Output directory (default: timelapse)'
    )

    args = parser.parse_args()

    return 0 if capture_timelapse(
        interval_seconds=args.interval,
        duration_minutes=args.duration,
        output_dir=args.output
    ) else 1

if __name__ == "__main__":
    sys.exit(main())
