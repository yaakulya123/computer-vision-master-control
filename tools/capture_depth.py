#!/usr/bin/env python3
"""
RealSense D435 Depth Camera Test Script
This script will attempt to connect to the camera and capture depth data.
"""

import sys
import ctypes
import numpy as np

# Try to import pyrealsense2 (may not be available on all systems)
try:
    import pyrealsense2 as rs
    PYREALSENSE_AVAILABLE = True
except ImportError:
    PYREALSENSE_AVAILABLE = False
    print("WARNING: pyrealsense2 module not available")
    print("Attempting to use SDK directly via ctypes...")

def test_with_pyrealsense():
    """Test camera using pyrealsense2 Python bindings"""
    if not PYREALSENSE_AVAILABLE:
        print("ERROR: pyrealsense2 not installed")
        print("Install with: pip install pyrealsense2")
        return False

    print("Testing with pyrealsense2...")
    print("-" * 50)

    # Create a context object
    ctx = rs.context()

    # Get list of connected devices
    devices = ctx.query_devices()

    if len(devices) == 0:
        print("No RealSense devices found!")
        return False

    print(f"Found {len(devices)} RealSense device(s)")

    # Print device information
    for i, device in enumerate(devices):
        print(f"\nDevice {i}:")
        print(f"  Name: {device.get_info(rs.camera_info.name)}")
        print(f"  Serial Number: {device.get_info(rs.camera_info.serial_number)}")
        print(f"  Firmware Version: {device.get_info(rs.camera_info.firmware_version)}")
        print(f"  USB Type: {device.get_info(rs.camera_info.usb_type_descriptor)}")

    # Try to start streaming
    print("\nAttempting to start streaming...")
    try:
        pipeline = rs.pipeline()
        config = rs.config()

        # Enable depth stream
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Enable color stream
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start pipeline
        profile = pipeline.start(config)

        print("SUCCESS: Camera is streaming!")

        # Capture a few frames
        print("\nCapturing 5 frames...")
        for i in range(5):
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if depth_frame and color_frame:
                # Get dimensions
                width = depth_frame.get_width()
                height = depth_frame.get_height()

                # Get depth data
                depth_image = np.asanyarray(depth_frame.get_data())

                # Get center point depth
                center_depth = depth_frame.get_distance(width // 2, height // 2)

                print(f"  Frame {i+1}: Center depth = {center_depth:.3f} meters")

        # Stop pipeline
        pipeline.stop()
        print("\nCamera test completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR starting stream: {e}")
        return False

def test_with_sdk_commands():
    """Test camera using SDK command-line tools"""
    import subprocess

    print("\nTesting with SDK command-line tools...")
    print("-" * 50)

    try:
        result = subprocess.run(
            ['rs-enumerate-devices'],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return False
    except FileNotFoundError:
        print("ERROR: rs-enumerate-devices not found")
        print("Make sure librealsense SDK is installed")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=" * 50)
    print("RealSense D435 Camera Test")
    print("=" * 50)
    print()

    # Test 1: Try with SDK commands first
    sdk_works = test_with_sdk_commands()

    print("\n")

    # Test 2: Try with Python bindings if available
    if PYREALSENSE_AVAILABLE:
        py_works = test_with_pyrealsense()
    else:
        print("Skipping pyrealsense2 test (module not available)")
        print("To install: pip install pyrealsense2")
        py_works = False

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"SDK Command Test: {'PASS' if sdk_works else 'FAIL'}")
    print(f"Python Bindings Test: {'PASS' if py_works else 'FAIL' if PYREALSENSE_AVAILABLE else 'SKIPPED'}")
    print()

    if not sdk_works:
        print("TROUBLESHOOTING TIPS:")
        print("1. Check USB connection (use USB 3.0 port)")
        print("2. Try: realsense-viewer (GUI tool)")
        print("3. Check macOS Privacy & Security settings")
        print("4. Try different USB port or cable")
        print("5. Restart your Mac")
        print("6. Check README.md for detailed troubleshooting")

    return 0 if (sdk_works or py_works) else 1

if __name__ == "__main__":
    sys.exit(main())
