#!/usr/bin/env python3
"""
RealSense D435 - Color Tracking Demo
Track objects by color in real-time with HSV color space
"""

import cv2
import numpy as np
import sys
import os
from datetime import datetime

REALSENSE_CAMERA_INDEX = 0

# Predefined color ranges in HSV
COLOR_RANGES = {
    'red_lower': ([0, 120, 70], [10, 255, 255]),
    'red_upper': ([170, 120, 70], [180, 255, 255]),
    'green': ([40, 50, 50], [80, 255, 255]),
    'blue': ([100, 150, 50], [130, 255, 255]),
    'yellow': ([20, 100, 100], [30, 255, 255]),
    'orange': ([10, 100, 100], [20, 255, 255]),
    'purple': ([130, 50, 50], [160, 255, 255]),
    'cyan': ([80, 50, 50], [100, 255, 255]),
}

def color_tracking_demo():
    """
    Track objects by color in real-time
    """
    print("=" * 50)
    print("RealSense D435 - Color Tracking Demo")
    print("=" * 50)
    print("\nColor Selection:")
    print("  'r' - Red")
    print("  'g' - Green")
    print("  'b' - Blue")
    print("  'y' - Yellow")
    print("  'o' - Orange")
    print("  'p' - Purple")
    print("  'c' - Cyan")
    print("\nOther Controls:")
    print("  'q' - Quit")
    print("  's' - Save snapshot")
    print("  'm' - Toggle mask view")
    print("  't' - Toggle trail")
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
    current_color = 'blue'
    show_mask = True
    show_trail = True

    # Trail points
    trail_points = []
    max_trail_points = 50

    # Stats
    frame_count = 0
    snapshot_count = 0
    objects_tracked = 0

    print(f"\n✓ Tracking color: {current_color.upper()}\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask based on selected color
        if current_color == 'red_lower' or current_color == 'red':
            # Red wraps around in HSV, need two ranges
            lower_red_lower = np.array(COLOR_RANGES['red_lower'][0])
            upper_red_lower = np.array(COLOR_RANGES['red_lower'][1])
            lower_red_upper = np.array(COLOR_RANGES['red_upper'][0])
            upper_red_upper = np.array(COLOR_RANGES['red_upper'][1])

            mask1 = cv2.inRange(hsv, lower_red_lower, upper_red_lower)
            mask2 = cv2.inRange(hsv, lower_red_upper, upper_red_upper)
            mask = mask1 + mask2
        else:
            lower = np.array(COLOR_RANGES[current_color][0])
            upper = np.array(COLOR_RANGES[current_color][1])
            mask = cv2.inRange(hsv, lower, upper)

        # Morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Track the largest contour
        largest_object_center = None
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 500:  # Minimum area threshold
                objects_tracked += 1

                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                # Get center
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    largest_object_center = (cx, cy)

                    # Draw center
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                    # Draw crosshair
                    cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (255, 0, 0), 2)
                    cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (255, 0, 0), 2)

                    # Add to trail
                    if show_trail:
                        trail_points.append((cx, cy))
                        if len(trail_points) > max_trail_points:
                            trail_points.pop(0)

                # Label
                label = f"{current_color.upper()}: {area:.0f}px"
                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        # Draw trail
        if show_trail and len(trail_points) > 1:
            for i in range(1, len(trail_points)):
                # Fade trail
                alpha = i / len(trail_points)
                color = (int(255 * alpha), 0, int(255 * (1 - alpha)))
                thickness = max(1, int(3 * alpha))
                cv2.line(frame, trail_points[i - 1], trail_points[i], color, thickness)

        # Create display view
        if show_mask:
            mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            display = np.hstack((frame, mask_colored))
            display = cv2.resize(display, (1920, 540))

            # Labels
            cv2.putText(
                display,
                "RGB + Tracking",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )
            cv2.putText(
                display,
                f"{current_color.upper()} Mask",
                (970, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )
        else:
            display = frame

        # Status overlay
        cv2.putText(
            display,
            f"Tracking: {current_color.upper()}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            display,
            f"Objects: {len(contours) if contours else 0}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )

        # Show the result
        cv2.imshow('RealSense D435 - Color Tracking', display)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/color_tracking_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, display)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('r'):
            current_color = 'red'
            trail_points.clear()
            print(f"  Now tracking: RED")
        elif key == ord('g'):
            current_color = 'green'
            trail_points.clear()
            print(f"  Now tracking: GREEN")
        elif key == ord('b'):
            current_color = 'blue'
            trail_points.clear()
            print(f"  Now tracking: BLUE")
        elif key == ord('y'):
            current_color = 'yellow'
            trail_points.clear()
            print(f"  Now tracking: YELLOW")
        elif key == ord('o'):
            current_color = 'orange'
            trail_points.clear()
            print(f"  Now tracking: ORANGE")
        elif key == ord('p'):
            current_color = 'purple'
            trail_points.clear()
            print(f"  Now tracking: PURPLE")
        elif key == ord('c'):
            current_color = 'cyan'
            trail_points.clear()
            print(f"  Now tracking: CYAN")
        elif key == ord('m'):
            show_mask = not show_mask
            print(f"  Mask view: {'ON' if show_mask else 'OFF'}")
        elif key == ord('t'):
            show_trail = not show_trail
            if not show_trail:
                trail_points.clear()
            print(f"  Trail: {'ON' if show_trail else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Objects tracked: {objects_tracked}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = color_tracking_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
