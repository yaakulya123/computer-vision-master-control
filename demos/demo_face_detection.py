#!/usr/bin/env python3
"""
RealSense D435 RGB Stream - Face Detection Demo
Uses Haar Cascade classifier for real-time face detection
"""

import cv2
import sys
import time
from datetime import datetime
import os

REALSENSE_CAMERA_INDEX = 0

def face_detection_demo():
    """
    Real-time face detection using the RealSense RGB camera
    Detects and tracks faces, eyes, and smiles
    """
    print("=" * 50)
    print("RealSense D435 - Face Detection Demo")
    print("=" * 50)
    print("\nLoading face detection models...")

    # Load the cascade classifiers
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
    smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    smile_cascade = cv2.CascadeClassifier(smile_cascade_path)

    if face_cascade.empty() or eye_cascade.empty() or smile_cascade.empty():
        print("ERROR: Could not load cascade classifiers")
        return False

    print("✓ Models loaded successfully")
    print("\nControls:")
    print("  'q' - Quit")
    print("  's' - Save snapshot")
    print("  'f' - Toggle face-only mode")
    print("  'e' - Toggle eye detection")
    print("  'm' - Toggle smile detection")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Settings
    detect_eyes = True
    detect_smiles = True
    face_only_mode = False

    # Stats
    frame_count = 0
    faces_detected_total = 0
    snapshot_count = 0
    max_faces_detected = 0

    print("\n✓ Face detection active!")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Update stats
        faces_detected_total += len(faces)
        if len(faces) > max_faces_detected:
            max_faces_detected = len(faces)

        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)

            # Label
            label = f"Face {faces.tolist().index([x, y, w, h]) + 1}"
            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2
            )

            # Region of interest for eyes and smile
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            # Detect eyes
            if detect_eyes:
                eyes = eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,
                    minNeighbors=10,
                    minSize=(20, 20)
                )
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(
                        roi_color,
                        (ex, ey),
                        (ex+ew, ey+eh),
                        (0, 255, 0),
                        2
                    )

            # Detect smile
            if detect_smiles:
                smiles = smile_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.8,
                    minNeighbors=20,
                    minSize=(25, 25)
                )
                if len(smiles) > 0:
                    # Draw smile indicator
                    cv2.putText(
                        frame,
                        "SMILING :)",
                        (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

        # Add status overlay
        status_y = 30
        cv2.putText(
            frame,
            f"Faces Detected: {len(faces)}",
            (10, status_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0) if len(faces) > 0 else (0, 165, 255),
            2
        )

        status_y += 40
        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, status_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Detection mode indicators
        status_y += 40
        indicators = []
        if detect_eyes:
            indicators.append("Eyes")
        if detect_smiles:
            indicators.append("Smiles")
        if indicators:
            cv2.putText(
                frame,
                f"Detecting: {', '.join(indicators)}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )

        # Show the result
        display_frame = frame if not face_only_mode else frame
        cv2.imshow('RealSense D435 - Face Detection', display_frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/face_snapshot_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('f'):
            face_only_mode = not face_only_mode
            print(f"  Face-only mode: {'ON' if face_only_mode else 'OFF'}")
        elif key == ord('e'):
            detect_eyes = not detect_eyes
            print(f"  Eye detection: {'ON' if detect_eyes else 'OFF'}")
        elif key == ord('m'):
            detect_smiles = not detect_smiles
            print(f"  Smile detection: {'ON' if detect_smiles else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Total face detections: {faces_detected_total}")
    print(f"Max faces in single frame: {max_faces_detected}")
    if frame_count > 0:
        print(f"Average faces per frame: {faces_detected_total/frame_count:.2f}")
    print(f"Snapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = face_detection_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
        sys.exit(0)
