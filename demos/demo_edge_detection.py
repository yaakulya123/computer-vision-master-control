#!/usr/bin/env python3
"""
RealSense D435 - Edge Detection Demo
Multiple edge detection algorithms and artistic effects
"""

import cv2
import numpy as np
import sys
import os
from datetime import datetime

REALSENSE_CAMERA_INDEX = 0

def edge_detection_demo():
    """
    Real-time edge detection with multiple algorithms
    """
    print("=" * 50)
    print("RealSense D435 - Edge Detection Demo")
    print("=" * 50)
    print("\nEdge Detection Methods:")
    print("  1 - Canny (default)")
    print("  2 - Sobel")
    print("  3 - Laplacian")
    print("  4 - Scharr")
    print("  5 - Sketch Effect")
    print("\nControls:")
    print("  '1-5' - Switch detection method")
    print("  'q' - Quit")
    print("  's' - Save snapshot")
    print("  '+/-' - Adjust threshold")
    print("\nStarting in 3 seconds...")

    import time
    time.sleep(3)

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Settings
    method = 1  # 1=Canny, 2=Sobel, 3=Laplacian, 4=Scharr, 5=Sketch
    threshold1 = 50
    threshold2 = 150

    # Stats
    frame_count = 0
    snapshot_count = 0

    method_names = {
        1: "Canny",
        2: "Sobel",
        3: "Laplacian",
        4: "Scharr",
        5: "Sketch"
    }

    print("\n✓ Edge detection active!\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply edge detection based on method
        if method == 1:  # Canny
            edges = cv2.Canny(gray, threshold1, threshold2)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif method == 2:  # Sobel
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            edges = cv2.magnitude(sobelx, sobely)
            edges = np.uint8(edges)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif method == 3:  # Laplacian
            edges = cv2.Laplacian(gray, cv2.CV_64F)
            edges = np.uint8(np.absolute(edges))
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif method == 4:  # Scharr
            scharrx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
            scharry = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
            edges = cv2.magnitude(scharrx, scharry)
            edges = np.uint8(edges)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif method == 5:  # Sketch effect
            # Invert image
            inverted = 255 - gray
            # Blur
            blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
            # Invert blur
            inverted_blur = 255 - blurred
            # Sketch
            edges = cv2.divide(gray, inverted_blur, scale=256.0)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Create side-by-side view
        display = np.hstack((frame, edges_colored))

        # Resize to fit screen better
        display = cv2.resize(display, (1920, 540))

        # Add labels
        cv2.putText(
            display,
            "Original",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            f"{method_names[method]} Edge Detection",
            (970, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Settings info
        if method == 1:
            settings_text = f"Thresholds: {threshold1}, {threshold2}"
            cv2.putText(
                display,
                settings_text,
                (970, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )

        cv2.putText(
            display,
            f"Frame: {frame_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Show the result
        cv2.imshow('RealSense D435 - Edge Detection', display)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/edge_detection_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, display)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
            method = int(chr(key))
            print(f"  Switched to: {method_names[method]}")
        elif key == ord('+') or key == ord('='):
            threshold1 = min(threshold1 + 10, 255)
            threshold2 = min(threshold2 + 10, 255)
            print(f"  Thresholds: {threshold1}, {threshold2}")
        elif key == ord('-'):
            threshold1 = max(threshold1 - 10, 0)
            threshold2 = max(threshold2 - 10, 0)
            print(f"  Thresholds: {threshold1}, {threshold2}")

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = edge_detection_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
