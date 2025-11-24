#!/usr/bin/env python3
"""
RealSense D435 - Hand Tracking & Gesture Recognition Demo
Using MediaPipe for 21-point hand landmark detection
"""

import cv2
import mediapipe as mp
import sys
import os
from datetime import datetime
import numpy as np

REALSENSE_CAMERA_INDEX = 0

def hand_tracking_demo(camera_index=None):
    """
    Track hands in real-time using MediaPipe
    Detects up to 2 hands with 21 landmarks each
    """
    print("=" * 50)
    print("RealSense D435 - Hand Tracking Demo")
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
    print("\nInitializing MediaPipe Hand Tracking...")

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    print("✓ MediaPipe initialized")
    print("\n" + "=" * 50)
    print("KEYBOARD CONTROLS - Press these keys during the demo:")
    print("=" * 50)
    print("  'q' - Quit the demo")
    print("  's' - Save snapshot to outputs/captures/")
    print("  'h' - Toggle hand connections ON/OFF")
    print("  'l' - Toggle landmark points ON/OFF")
    print("=" * 50)
    print("\nTIP: Show your hands clearly to the camera!")
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

    # Stats
    frame_count = 0
    hands_detected_count = 0
    snapshot_count = 0

    print("\n✓ Hand tracking active!")
    print("Show your hands to the camera!\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = hands.process(rgb_frame)

        # Count hands detected
        num_hands = 0
        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)
            hands_detected_count += num_hands

            # Draw hand landmarks
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness (Left/Right)
                handedness = results.multi_handedness[hand_idx].classification[0].label

                # Draw landmarks and connections
                if show_landmarks or show_connections:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS if show_connections else None,
                        mp_drawing_styles.get_default_hand_landmarks_style() if show_landmarks else None,
                        mp_drawing_styles.get_default_hand_connections_style() if show_connections else None
                    )

                # Get landmarks for gesture recognition
                landmarks = hand_landmarks.landmark

                # Calculate bounding box
                h, w, c = frame.shape
                x_coords = [lm.x * w for lm in landmarks]
                y_coords = [lm.y * h for lm in landmarks]

                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))

                # Draw bounding box
                cv2.rectangle(frame, (x_min-10, y_min-10), (x_max+10, y_max+10), (0, 255, 0), 2)

                # Label
                label = f"{handedness} Hand"
                cv2.putText(
                    frame,
                    label,
                    (x_min, y_min - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                # Simple gesture detection
                gesture = detect_gesture(landmarks)
                if gesture:
                    cv2.putText(
                        frame,
                        f"Gesture: {gesture}",
                        (x_min, y_max + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 0, 255),
                        2
                    )

        # Add status overlay
        status_color = (0, 255, 0) if num_hands > 0 else (0, 165, 255)
        cv2.putText(
            frame,
            f"Hands Detected: {num_hands}",
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
        cv2.imshow('RealSense D435 - Hand Tracking', frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/hand_tracking_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('h'):
            show_connections = not show_connections
            print(f"  Hand connections: {'ON' if show_connections else 'OFF'}")
        elif key == ord('l'):
            show_landmarks = not show_landmarks
            print(f"  Landmarks: {'ON' if show_landmarks else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Total hand detections: {hands_detected_count}")
    if frame_count > 0:
        print(f"Average hands per frame: {hands_detected_count/frame_count:.2f}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

def detect_gesture(landmarks):
    """
    Simple gesture detection based on finger positions
    Returns gesture name or None
    """
    # Get fingertip and base positions
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    palm_base = landmarks[0]

    # Check if fingers are extended (y coordinate comparison)
    thumb_up = thumb_tip.y < landmarks[3].y
    index_up = index_tip.y < landmarks[6].y
    middle_up = middle_tip.y < landmarks[10].y
    ring_up = ring_tip.y < landmarks[14].y
    pinky_up = pinky_tip.y < landmarks[18].y

    fingers_up = sum([thumb_up, index_up, middle_up, ring_up, pinky_up])

    # Gesture recognition
    if fingers_up == 5:
        return "OPEN HAND"
    elif fingers_up == 0:
        return "FIST"
    elif index_up and middle_up and not ring_up and not pinky_up:
        return "PEACE ✌️"
    elif thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "THUMBS UP 👍"
    elif index_up and not middle_up and not ring_up and not pinky_up:
        return "POINTING ☝️"
    elif fingers_up == 1:
        return "ONE"
    elif fingers_up == 2:
        return "TWO"
    elif fingers_up == 3:
        return "THREE"
    elif fingers_up == 4:
        return "FOUR"

    return None

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = hand_tracking_demo()
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
