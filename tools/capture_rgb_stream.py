#!/usr/bin/env python3
"""
RealSense D435 RGB Stream Capture
Working example using OpenCV - bypasses the SDK USB access issue
"""

import cv2
import sys
import time
from datetime import datetime

# Camera index for RealSense RGB module
# Based on testing: Camera 1 is the RealSense
REALSENSE_CAMERA_INDEX = 0

def capture_single_image(output_path="../outputs/captures/capture.jpg"):
    """Capture a single image from the RealSense RGB camera"""
    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Skip a few frames to let camera stabilize
    print("Warming up camera...")
    for _ in range(10):
        cap.read()

    # Capture frame
    print("Capturing image...")
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"✓ Image saved to: {output_path}")
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        success = True
    else:
        print("✗ Failed to capture image")
        success = False

    cap.release()
    return success

def stream_video(duration_seconds=10):
    """Stream video from RealSense RGB camera"""
    print(f"Starting video stream for {duration_seconds} seconds...")
    print("Press 'q' to quit early, 's' to save snapshot")

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    start_time = time.time()
    frame_count = 0
    snapshot_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Add timestamp overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('RealSense D435 - RGB Stream', frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\nStopping stream (user requested)")
            break
        elif key == ord('s'):
            snapshot_path = f"../outputs/captures/snapshot_{snapshot_count:03d}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1

        # Check if duration has elapsed
        if time.time() - start_time > duration_seconds:
            print(f"\nStream duration complete ({duration_seconds}s)")
            break

    # Calculate FPS
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0

    cap.release()
    cv2.destroyAllWindows()

    print("\n" + "=" * 50)
    print(f"Captured {frame_count} frames in {elapsed:.1f} seconds")
    print(f"Average FPS: {fps:.1f}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

def record_video(output_path="../outputs/captures/recording.mp4", duration_seconds=10):
    """Record video from RealSense RGB camera"""
    print(f"Recording video to: {output_path}")
    print(f"Duration: {duration_seconds} seconds")

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Get video properties
    fps = 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Recording at {width}x{height}, {fps} FPS...")

    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        # Write frame
        out.write(frame)
        frame_count += 1

        # Check if duration has elapsed
        if time.time() - start_time > duration_seconds:
            break

    cap.release()
    out.release()

    print(f"✓ Video saved to: {output_path}")
    print(f"  Frames recorded: {frame_count}")

    return True

def main():
    import os

    # Create captures directory if it doesn't exist
    os.makedirs("captures", exist_ok=True)

    print("=" * 50)
    print("RealSense D435 RGB Stream - Working Example")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. Capture single image")
    print("2. Stream video (10 seconds)")
    print("3. Record video to file (10 seconds)")
    print("4. Continuous stream (press 'q' to quit)")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        capture_single_image(f"../outputs/captures/image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")

    elif choice == "2":
        stream_video(duration_seconds=10)

    elif choice == "3":
        record_video(f"../outputs/captures/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4", duration_seconds=10)

    elif choice == "4":
        stream_video(duration_seconds=999999)  # Very long duration

    else:
        print("Invalid choice")
        return 1

    print("\n✓ Done!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
