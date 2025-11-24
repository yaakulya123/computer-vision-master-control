# RealSense D435 Camera Setup Guide

## Current Status
The RealSense SDK is installed, but the camera has USB access permission issues.

## Issue Identified
```
Error: failed to claim usb interface: 0, error: RS2_USB_STATUS_ACCESS
```

This means the camera is detected but cannot be accessed due to permissions.

## Troubleshooting Steps

### 1. Physical Connection
- [ ] Ensure camera is plugged into a **USB 3.0 port** (USB-C with adapter may work)
- [ ] Check if LED lights turn on (should show when powered)
- [ ] Try different USB ports on your Mac
- [ ] Try a different USB cable (must be USB 3.0 capable)

### 2. macOS Permissions (For Apple Silicon Macs)

#### Option A: Check System Extensions
1. Open **System Settings** > **Privacy & Security**
2. Scroll down to check if there are any blocked system extensions
3. If you see any Intel or RealSense related extensions, allow them

#### Option B: Reset USB Permissions
Open Terminal and run:
```bash
# Reset SMC (may help with USB issues)
# For Apple Silicon Macs: Just restart your Mac
```

### 3. Alternative: Try with realsense-viewer GUI
```bash
realsense-viewer
```
This GUI tool might prompt for necessary permissions.

### 4. Check for Firmware Update
The D435 may need a firmware update. Visit:
https://dev.intelrealsense.com/docs/firmware-releases

### 5. Known Issues on macOS
- **Apple Silicon Compatibility**: Some RealSense features may have limited support on ARM64 Macs
- **USB-C Adapters**: Not all USB-C hubs/adapters provide proper USB 3.0 connectivity
- **Power Requirements**: D435 requires adequate USB power delivery

## Files in this folder

- `test_camera.sh` - Diagnostic script to check camera connection
- `test_opencv.py` - Alternative test using OpenCV (if available)
- `capture_depth.py` - Python script to capture depth data (once camera works)

## Quick Test Commands

```bash
# Test 1: List RealSense devices
rs-enumerate-devices

# Test 2: Run diagnostic script
./test_camera.sh

# Test 3: Try the viewer
realsense-viewer
```

## System Information
- OS: macOS (Apple Silicon - ARM64)
- SDK: librealsense 2.57.4
- Camera: Intel RealSense D435

## Next Steps
1. Try unplugging and replugging the camera
2. Restart your Mac
3. Try `realsense-viewer` to see if it prompts for permissions
4. Check if a USB-C to USB-A adapter is causing issues
