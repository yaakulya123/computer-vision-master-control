#!/usr/bin/env python3
"""
RealSense D435 RGB Stream - Object Tracking Demo
Interactive object tracking using various OpenCV tracking algorithms
"""

import cv2
import sys
import time
from datetime import datetime
import os

REALSENSE_CAMERA_INDEX = 0

def object_tracking_demo():
    """
    Interactive object tracking demo
    User selects an object to track, system follows it
    """
    print("=" * 50)
    print("RealSense D435 - Object Tracking Demo")
    print("=" * 50)

    # Available trackers
    tracker_types = {
        '1': ('CSRT', 'High accuracy, slower'),
        '2': ('KCF', 'Balanced speed/accuracy'),
        '3': ('MOSSE', 'Fast, lower accuracy'),
        '4': ('MedianFlow', 'Good for predictable motion')
    }

    print("\nAvailable tracking algorithms:")
    for key, (name, desc) in tracker_types.items():
        print(f"  {key}. {name} - {desc}")

    choice = input("\nSelect tracker (1-4, default=2): ").strip() or '2'

    if choice not in tracker_types:
        print("Invalid choice, using KCF")
        choice = '2'

    tracker_name = tracker_types[choice][0]
    print(f"\n✓ Using {tracker_name} tracker")

    print("\nControls:")
    print("  1. Select object to track with mouse")
    print("  2. Press ENTER to start tracking")
    print("  3. Press 'r' to reset and select new object")
    print("  4. Press 's' to save snapshot")
    print("  5. Press 'q' to quit")
    print("\nOpening camera...")

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Cannot read from camera")
        return False

    print("\n✓ Camera ready!")
    print("Select the object to track by drawing a box around it...")

    # Select ROI
    bbox = cv2.selectROI('Select Object to Track', frame, False)
    cv2.destroyWindow('Select Object to Track')

    if bbox[2] == 0 or bbox[3] == 0:
        print("No object selected, exiting...")
        cap.release()
        return False

    # Create tracker
    if tracker_name == 'CSRT':
        tracker = cv2.TrackerCSRT_create()
    elif tracker_name == 'KCF':
        tracker = cv2.TrackerKCF_create()
    elif tracker_name == 'MOSSE':
        tracker = cv2.legacy.TrackerMOSSE_create()
    elif tracker_name == 'MedianFlow':
        tracker = cv2.legacy.TrackerMedianFlow_create()

    # Initialize tracker
    tracker.init(frame, bbox)

    print(f"\n✓ Tracking started with {tracker_name}!")
    print(f"  Initial box: {bbox}")

    # Stats
    frame_count = 0
    tracking_success_count = 0
    tracking_failures = 0
    snapshot_count = 0
    start_time = time.time()

    # Track center point history for path visualization
    center_history = []
    max_history = 50

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Update tracker
        success, bbox = tracker.update(frame)

        if success:
            tracking_success_count += 1

            # Get bounding box coordinates
            x, y, w, h = [int(v) for v in bbox]

            # Calculate center
            center_x = x + w // 2
            center_y = y + h // 2
            center_history.append((center_x, center_y))

            # Keep only recent history
            if len(center_history) > max_history:
                center_history.pop(0)

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # Draw center point
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # Draw path
            if len(center_history) > 1:
                for i in range(1, len(center_history)):
                    # Fade older points
                    alpha = i / len(center_history)
                    color = (0, int(165 * alpha), int(255 * alpha))
                    thickness = max(1, int(2 * alpha))
                    cv2.line(
                        frame,
                        center_history[i-1],
                        center_history[i],
                        color,
                        thickness
                    )

            # Add tracking info
            cv2.putText(
                frame,
                f"TRACKING - {tracker_name}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # Add position info
            cv2.putText(
                frame,
                f"Pos: ({center_x}, {center_y})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        else:
            tracking_failures += 1

            # Show tracking failure
            cv2.putText(
                frame,
                "TRACKING LOST - Press 'r' to reset",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # Add stats overlay
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0

        cv2.putText(
            frame,
            f"Frame: {frame_count} | FPS: {fps:.1f}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )

        success_rate = (tracking_success_count / frame_count * 100) if frame_count > 0 else 0
        cv2.putText(
            frame,
            f"Success Rate: {success_rate:.1f}%",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )

        # Show the result
        cv2.imshow('RealSense D435 - Object Tracking', frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/tracking_snapshot_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('r'):
            print("\n  Resetting tracker - select new object...")
            bbox = cv2.selectROI('Select Object to Track', frame, False)
            cv2.destroyWindow('Select Object to Track')

            if bbox[2] > 0 and bbox[3] > 0:
                # Recreate tracker
                if tracker_name == 'CSRT':
                    tracker = cv2.TrackerCSRT_create()
                elif tracker_name == 'KCF':
                    tracker = cv2.TrackerKCF_create()
                elif tracker_name == 'MOSSE':
                    tracker = cv2.legacy.TrackerMOSSE_create()
                elif tracker_name == 'MedianFlow':
                    tracker = cv2.legacy.TrackerMedianFlow_create()

                tracker.init(frame, bbox)
                center_history.clear()
                print("  ✓ Tracker reset!")

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Tracker used: {tracker_name}")
    print(f"Total frames processed: {frame_count}")
    print(f"Successful tracking frames: {tracking_success_count}")
    print(f"Tracking failures: {tracking_failures}")
    if frame_count > 0:
        print(f"Overall success rate: {tracking_success_count/frame_count*100:.1f}%")
        print(f"Average FPS: {frame_count/elapsed:.1f}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = object_tracking_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
        sys.exit(1)
