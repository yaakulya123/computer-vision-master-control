#!/usr/bin/env python3
"""
RealSense D435 RGB Stream - Motion Detection Demo
Shows practical use of the RGB camera
"""

import cv2
import numpy as np
import sys
import time
from datetime import datetime

REALSENSE_CAMERA_INDEX = 0

def motion_detection_demo():
    """
    Simple motion detection using the RealSense RGB camera
    Highlights areas where motion is detected
    """
    print("=" * 50)
    print("RealSense D435 - Motion Detection Demo")
    print("=" * 50)
    print("\nControls:")
    print("  'q' - Quit")
    print("  's' - Save snapshot of current frame")
    print("  'r' - Reset background model")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Initialize background subtractor
    back_sub = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=16,
        detectShadows=True
    )

    # Skip first few frames
    for _ in range(10):
        cap.read()

    frame_count = 0
    motion_detected_count = 0
    snapshot_count = 0

    print("\n✓ Motion detection active!")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Apply background subtraction
        fg_mask = back_sub.apply(frame)

        # Reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            fg_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Draw contours and bounding boxes for significant motion
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 500:  # Ignore small movements
                continue

            motion_detected = True
            motion_detected_count += 1

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Add label
            cv2.putText(
                frame,
                "MOTION",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # Create display frame with motion mask
        # Resize mask to match frame for side-by-side display
        fg_mask_colored = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR)

        # Resize both to fit on screen better
        frame_display = cv2.resize(frame, (960, 540))
        mask_display = cv2.resize(fg_mask_colored, (960, 540))

        # Stack horizontally
        combined = np.hstack((frame_display, mask_display))

        # Add status text
        status = "MOTION DETECTED!" if motion_detected else "No motion"
        color = (0, 255, 0) if motion_detected else (0, 165, 255)
        cv2.putText(
            combined,
            status,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        # Add frame counter
        cv2.putText(
            combined,
            f"Frame: {frame_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Add labels
        cv2.putText(
            combined,
            "RGB Stream",
            (10, 520),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            combined,
            "Motion Mask",
            (970, 520),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Show the result
        cv2.imshow('RealSense D435 - Motion Detection', combined)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/motion_snapshot_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, combined)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('r'):
            print("  Resetting background model...")
            back_sub = cv2.createBackgroundSubtractorMOG2(
                history=500,
                varThreshold=16,
                detectShadows=True
            )

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Frames with motion: {motion_detected_count}")
    if frame_count > 0:
        print(f"Motion rate: {(motion_detected_count/frame_count)*100:.1f}%")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    import os
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = motion_detection_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
