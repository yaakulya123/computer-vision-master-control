#!/usr/bin/env python3
"""
RealSense D435 - QR Code & Barcode Scanner Demo
Real-time code detection and decoding
"""

import cv2
from pyzbar import pyzbar
import sys
import os
from datetime import datetime
import webbrowser

REALSENSE_CAMERA_INDEX = 0

def qr_barcode_scanner_demo():
    """
    Scan QR codes and barcodes in real-time
    Automatically decode and display data
    """
    print("=" * 50)
    print("RealSense D435 - QR/Barcode Scanner")
    print("=" * 50)
    print("\nControls:")
    print("  'q' - Quit")
    print("  's' - Save snapshot")
    print("  'o' - Open last detected URL (if any)")
    print("\nStarting scanner...")
    print("Show a QR code or barcode to the camera!\n")

    cap = cv2.VideoCapture(REALSENSE_CAMERA_INDEX)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {REALSENSE_CAMERA_INDEX}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Stats
    frame_count = 0
    codes_detected_total = 0
    snapshot_count = 0
    detected_codes = {}
    last_url = None

    print("✓ Scanner active!\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            break

        frame_count += 1

        # Decode barcodes and QR codes
        barcodes = pyzbar.decode(frame)

        codes_in_frame = len(barcodes)
        codes_detected_total += codes_in_frame

        # Process each detected code
        for barcode in barcodes:
            # Extract bounding box
            x, y, w, h = barcode.rect

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # Decode data
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type

            # Store detected code
            if barcode_data not in detected_codes:
                detected_codes[barcode_data] = barcode_type
                print(f"📊 Detected {barcode_type}: {barcode_data}")

                # Check if it's a URL
                if barcode_data.startswith(('http://', 'https://', 'www.')):
                    last_url = barcode_data
                    print(f"   🔗 URL detected! Press 'o' to open")

            # Display data on frame
            text = f"{barcode_type}: {barcode_data}"
            cv2.putText(
                frame,
                text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Draw corner points
            for point in barcode.polygon:
                cv2.circle(frame, (point.x, point.y), 5, (255, 0, 0), -1)

        # Add status overlay
        status_color = (0, 255, 0) if codes_in_frame > 0 else (0, 165, 255)
        cv2.putText(
            frame,
            f"Codes Detected: {codes_in_frame}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            status_color,
            2
        )

        cv2.putText(
            frame,
            f"Total Unique: {len(detected_codes)}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Show the result
        cv2.imshow('RealSense D435 - QR/Barcode Scanner', frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n\nStopping...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            snapshot_path = f"../outputs/captures/qr_scanner_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"  Snapshot saved: {snapshot_path}")
            snapshot_count += 1
        elif key == ord('o'):
            if last_url:
                print(f"  Opening URL: {last_url}")
                webbrowser.open(last_url)
            else:
                print("  No URL detected yet")

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n" + "=" * 50)
    print("Session Summary")
    print("=" * 50)
    print(f"Total frames processed: {frame_count}")
    print(f"Total code detections: {codes_detected_total}")
    print(f"Unique codes found: {len(detected_codes)}")
    print("\nDetected Codes:")
    for data, code_type in detected_codes.items():
        print(f"  [{code_type}] {data[:60]}{'...' if len(data) > 60 else ''}")
    print(f"\nSnapshots saved: {snapshot_count}")
    print("=" * 50)

    return True

if __name__ == "__main__":
    os.makedirs("../outputs/captures", exist_ok=True)

    try:
        success = qr_barcode_scanner_demo()
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
