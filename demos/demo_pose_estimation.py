#!/usr/bin/env python3
"""
RealSense D435 - Full Body Pose Estimation Demo
Using MediaPipe for 33-point body landmark detection
"""

import cv2
import mediapipe as mp
import sys
import os
from datetime import datetime
import numpy as np

REALSENSE_CAMERA_INDEX = 0

def pose_estimation_demo(camera_index=None):
    """
    Track full body pose in real-time using MediaPipe
    Detects 33 body landmarks including face, torso, arms, and legs
    """
    print("=" * 50)
    print("RealSense D435 - Pose Estimation Demo")
    print("=" * 50)

    # Camera selection
    if camera_index is None:
        print("\nAvailable cameras:")
        print("  0 - Camera 0 (RealSense D435 RGB - RECOMMENDED)")
        print("  1 - Camera 1 (Laptop FaceTime Camera)")
        print("  2 - Camera 2 (iPhone Camera)")

        while True:
            try:
                choice = input("\nSelect camera index (0-2): ").strip()
                camera_index = int(choice)
                if 0 <= camera_index <= 2:
                    break
                else:
                    print("Please enter 0, 1, or 2")
            except ValueError:
                print("Please enter a valid number")

    print(f"\nUsing Camera {camera_index}")
    print("\nInitializing MediaPipe Pose Estimation...")

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    print("✓ MediaPipe Pose initialized")
    print("\n" + "=" * 50)
    print("KEYBOARD CONTROLS - Press these keys during the demo:")
    print("=" * 50)
    print("  'q' - Quit the demo")
    print("  's' - Save snapshot to outputs/captures/")
    print("  'c' - Toggle skeleton connections ON/OFF")
    print("  'l' - Toggle landmark points ON/OFF")
    print("  'b' - Toggle bounding box ON/OFF")
    print("=" * 50)
    print("\nTIP: Stand back so your full body is visible!")
    print("Starting in 3 seconds...")

    import time
    time.sleep(3)

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {camera_index}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Settings
    show_connections = True
    show_landmarks = True
    show_bbox = True

    # Stats
    frame_count = 0
    pose_detected_count = 0
    snapshot_count = 0

    print("\n✓ Pose tracking active!\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = pose.process(rgb_frame)

        # Draw pose landmarks
        pose_detected = False
        if results.pose_landmarks:
            pose_detected = True
            pose_detected_count += 1

            # Draw landmarks and connections
            if show_landmarks or show_connections:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS if show_connections else None,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style() if show_landmarks else None
                )

            # Calculate bounding box
            if show_bbox:
                landmarks = results.pose_landmarks.landmark
                h, w, c = frame.shape

                x_coords = [lm.x * w for lm in landmarks if lm.visibility > 0.5]
                y_coords = [lm.y * h for lm in landmarks if lm.visibility > 0.5]

                if x_coords and y_coords:
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))

                    # Draw bounding box
                    cv2.rectangle(frame, (x_min-20, y_min-20), (x_max+20, y_max+20), (0, 255, 0), 2)

                    # Label
                    cv2.putText(
                        frame,
                        "Person Detected",
                        (x_min, y_min - 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

            # Detect pose/activity
            pose_status = analyze_pose(results.pose_landmarks.landmark)
            if pose_status:
                cv2.putText(
                    frame,
                    f"Pose: {pose_status}",
                    (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 255),
                    2
                )

        # Add status overlay
        status_color = (0, 255, 0) if pose_detected else (0, 165, 255)
        cv2.putText(
            frame,
            f"Pose: {'DETECTED' if pose_detected else 'NOT DETECTED'}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            status_color,
            2
        )

        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Mode indicators
        modes = []
        if show_connections:
            modes.append("Connections")
        if show_landmarks:
            modes.append("Landmarks")
        if show_bbox:
            modes.append("BBox")
        if modes:
            cv2.putText(
                frame,
                f"Display: {', '.join(modes)}",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )

        # Show the result
        cv2.imshow('RealSense D435 - Pose Estimation', frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/pose_estimation_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('c'):
            show_connections = not show_connections
            print(f"  Connections: {'ON' if show_connections else 'OFF'}")
        elif key == ord('l'):
            show_landmarks = not show_landmarks
            print(f"  Landmarks: {'ON' if show_landmarks else 'OFF'}")
        elif key == ord('b'):
            show_bbox = not show_bbox
            print(f"  Bounding box: {'ON' if show_bbox else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()
    pose.close()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Frames with pose detected: {pose_detected_count}")
    if frame_count > 0:
        print(f"Detection rate: {pose_detected_count/frame_count*100:.1f}%")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

def analyze_pose(landmarks):
    """
    Analyze pose to detect activities/positions
    Returns activity name or None
    """
    # Get key landmarks
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_knee = landmarks[25]
    right_knee = landmarks[26]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]
    left_wrist = landmarks[15]
    right_wrist = landmarks[16]

    # Calculate average shoulder and hip heights
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_y = (left_hip.y + right_hip.y) / 2
    knee_y = (left_knee.y + right_knee.y) / 2

    # Check visibility
    if left_shoulder.visibility < 0.5 or right_shoulder.visibility < 0.5:
        return None

    # Arms raised
    if left_wrist.y < shoulder_y and right_wrist.y < shoulder_y:
        return "ARMS RAISED"

    # Standing vs sitting (approximate)
    torso_knee_ratio = abs(hip_y - shoulder_y) / abs(knee_y - hip_y) if abs(knee_y - hip_y) > 0.01 else 0

    if torso_knee_ratio > 1.5:
        return "STANDING"
    elif torso_knee_ratio < 0.8:
        return "SITTING"

    return "NEUTRAL"

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = pose_estimation_demo()
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
