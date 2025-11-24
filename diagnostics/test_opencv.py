#!/usr/bin/env python3
"""
Test RealSense D435 using OpenCV
OpenCV has better macOS compatibility than the RealSense SDK
"""

import sys

try:
    import cv2
    import numpy as np
except ImportError:
    print("ERROR: OpenCV not installed")
    print("Install with: pip3 install opencv-python")
    sys.exit(1)

def list_available_cameras(max_cameras=10):
    """List all available camera devices"""
    print("Scanning for available cameras...")
    print("-" * 50)

    available_cameras = []

    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Try to read the backend name
            backend = cap.getBackendName()

            # Get basic info
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)

            available_cameras.append({
                'index': i,
                'backend': backend,
                'resolution': f"{int(width)}x{int(height)}",
                'fps': fps
            })

            print(f"Camera {i}:")
            print(f"  Backend: {backend}")
            print(f"  Resolution: {int(width)}x{int(height)}")
            print(f"  FPS: {fps}")
            print()

            cap.release()

    return available_cameras

def test_camera(camera_index):
    """Test a specific camera by capturing frames"""
    print(f"\nTesting Camera {camera_index}")
    print("-" * 50)

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {camera_index}")
        return False

    print(f"✓ Camera {camera_index} opened successfully")

    # Try to capture 5 frames
    print("Capturing 5 test frames...")

    for i in range(5):
        ret, frame = cap.read()

        if ret:
            h, w = frame.shape[:2]
            # Calculate average brightness as a simple test
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)

            print(f"  Frame {i+1}: {w}x{h}, avg brightness: {avg_brightness:.1f}")
        else:
            print(f"  Frame {i+1}: Failed to read")

    cap.release()
    print("✓ Camera test completed")

    return True

def capture_and_save(camera_index, output_file="test_capture.jpg"):
    """Capture a single frame and save it"""
    print(f"\nCapturing image from Camera {camera_index}")
    print("-" * 50)

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {camera_index}")
        return False

    # Skip a few frames to let camera stabilize
    for _ in range(5):
        cap.read()

    # Capture frame
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_file, frame)
        print(f"✓ Image saved to: {output_file}")
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        success = True
    else:
        print("✗ Failed to capture image")
        success = False

    cap.release()
    return success

def main():
    print("=" * 50)
    print("RealSense D435 - OpenCV Test")
    print("=" * 50)
    print()

    # List all available cameras
    cameras = list_available_cameras()

    if not cameras:
        print("ERROR: No cameras found!")
        print("\nTroubleshooting:")
        print("1. Check camera connections")
        print("2. Check System Settings > Privacy & Security > Camera")
        print("3. Try running: system_profiler SPCameraDataType")
        return 1

    print(f"Found {len(cameras)} camera(s)")
    print()

    # Based on the system_profiler output, the RealSense is likely camera 1 or 2
    # (0 is usually FaceTime camera)
    print("=" * 50)
    print("Testing Individual Cameras")
    print("=" * 50)

    for cam in cameras:
        test_camera(cam['index'])
        print()

    # Try to capture from what's likely the RealSense camera
    # Usually index 1 if FaceTime is 0
    if len(cameras) >= 2:
        print("=" * 50)
        print("Attempting to capture from RealSense (likely camera 1)")
        print("=" * 50)
        capture_and_save(1, "realsense_rgb_capture.jpg")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"✓ Found {len(cameras)} camera(s)")
    print("✓ OpenCV is working with your cameras")
    print("\nNOTE: OpenCV can only access the RGB stream,")
    print("not the depth stream. For depth data, you need")
    print("the RealSense SDK which has the USB access issue.")
    print("\nPossible solutions for depth access:")
    print("1. Boot into Safe Mode and test")
    print("2. Build patched SDK from source")
    print("3. Use a Linux VM/Docker with USB passthrough")
    print("=" * 50)

    return 0

if __name__ == "__main__":
    sys.exit(main())
