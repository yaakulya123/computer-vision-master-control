# macOS RealSense D435 Workarounds

## The Problem
Your Mac can see the RealSense D435, but the SDK cannot claim the USB interface due to a **known macOS bug** in Monterey and later versions.

**Error**: `failed to claim usb interface: 0, error: RS2_USB_STATUS_ACCESS`

## GitHub Issue
This is documented in: https://github.com/IntelRealSense/librealsense/issues/9916

## Key Findings
- ✅ macOS **CAN** see and power the camera
- ✅ Camera works in **Safe Mode**
- ❌ Normal mode has USB interface claiming issues
- ❌ This is an **OS-level bug**, not hardware or SDK issue

## Workarounds to Try

### Option 1: Test with Photo Booth (Immediate)
1. Photo Booth should have just opened
2. In Photo Booth, click on **Camera** menu
3. Look for "Intel RealSense" or similar device
4. If you can see it, the camera hardware is working!

**Note**: Photo Booth won't show depth data, but confirms the camera is powered and accessible.

### Option 2: Safe Mode Testing (Most Reliable)
The camera **works in Safe Mode** according to other users.

**To boot into Safe Mode**:
1. Shut down your Mac completely
2. Turn it on and **immediately press and hold the power button**
3. Release when you see startup options
4. Select your startup disk, then **hold Shift** and click "Continue in Safe Mode"
5. Once in Safe Mode, run:
   ```bash
   cd ~/Documents/Github/Depthcamera_testing
   ./test_camera.sh
   ```

**If it works in Safe Mode**: This confirms a third-party driver or service is blocking USB access.

### Option 3: Try OpenCV (Alternative Library)
I'll create a script using OpenCV which might have better macOS compatibility:

```bash
cd ~/Documents/Github/Depthcamera_testing
python3 test_opencv.py
```

### Option 4: Use AVFoundation (macOS Native)
Create a native macOS app using AVFoundation to access the camera streams.

### Option 5: Build from Source (Advanced)
The LightBuzz guide has detailed instructions:
https://lightbuzz.com/realsense-macos/

This involves building a patched version with better macOS support.

## System Information
- Your macOS version: 26.0.1 (Sequoia or later)
- Your architecture: ARM64 (Apple Silicon)
- Issue: Intel officially supports only macOS High Sierra (2017)
- Reality: Community has workarounds for newer versions

## Quick Diagnostic
Run this to see if the camera appears to macOS:
```bash
system_profiler SPCameraDataType
```

## Next Steps
1. **Check Photo Booth** - Can you see the camera listed?
2. **Try Safe Mode** - This is the most reliable test
3. **Report back** - Let me know what you find!

## Alternative: Use with Docker (Future Option)
If all else fails, you could run the RealSense SDK inside a Linux Docker container with USB passthrough. This is more complex but bypasses macOS issues entirely.

## Community Solutions
Check these resources:
- https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_osx.md
- https://lightbuzz.com/realsense-macos/
- https://support.intelrealsense.com/
