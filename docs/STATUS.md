# RealSense D435 Camera - Current Status

## ✅ What's Working

### RGB Stream via OpenCV
The **RGB camera stream is fully functional** using OpenCV!

- ✅ Camera detected by macOS
- ✅ RGB stream accessible via OpenCV (AVFoundation backend)
- ✅ Can capture images at 1920x1080
- ✅ Can stream video
- ✅ Can record video to file

**Test results**:
```
Camera 1: Intel RealSense D435 RGB Module
Backend: AVFOUNDATION
Resolution: 1920x1080
FPS: 30.0
Status: ✓ WORKING
```

**Proof**: Successfully captured `realsense_rgb_capture.jpg`

## ❌ What's NOT Working

### Depth Stream via RealSense SDK
The depth camera **cannot be accessed** due to macOS USB interface claiming bug.

**Error**: `failed to claim usb interface: 0, error: RS2_USB_STATUS_ACCESS`

**Why**:
- Known bug in macOS Monterey and later
- Documented in GitHub issue #9916
- OS-level problem, not hardware issue
- Intel officially only supports macOS High Sierra (2017)

## 🎯 Current Capabilities

### You CAN:
1. ✅ Capture RGB images from the D435
2. ✅ Stream RGB video in real-time
3. ✅ Record RGB video to files
4. ✅ Access camera at full 1920x1080 resolution
5. ✅ Use standard OpenCV processing on images

### You CANNOT (yet):
1. ❌ Access depth data
2. ❌ Get point clouds
3. ❌ Use IR cameras
4. ❌ Use RealSense SDK features

## 🚀 How to Use (RGB Only)

### Quick Test
```bash
cd ~/Documents/Github/Depthcamera_testing
python3 capture_rgb_stream.py
```

Then choose option 1-4 for different capture modes.

### In Your Own Code
```python
import cv2

# Camera 1 is the RealSense RGB module
cap = cv2.VideoCapture(1)

ret, frame = cap.read()
if ret:
    cv2.imwrite("my_capture.jpg", frame)

cap.release()
```

## 🔧 Getting Depth Access (Options)

### Option 1: Safe Mode (Temporary Testing)
Boot into Safe Mode - RealSense SDK reportedly works there.

**Steps**:
1. Shut down Mac
2. Power on and hold power button
3. Select disk → Hold Shift → "Continue in Safe Mode"
4. Test with: `rs-enumerate-devices`

**Downside**: Not practical for regular use

### Option 2: Build Patched SDK (Advanced)
Follow LightBuzz guide for Apple Silicon:
https://lightbuzz.com/realsense-macos/

**Downside**: Complex build process, may still have issues

### Option 3: Linux VM with USB Passthrough
Run Ubuntu in a VM (UTM, Parallels) with USB passthrough.

**Steps**:
1. Install Ubuntu VM
2. Enable USB passthrough for RealSense
3. Install RealSense SDK in Ubuntu
4. Full depth access in Linux environment

**Downside**: Overhead of running VM

### Option 4: Docker with USB Passthrough
Similar to VM but using Docker Desktop for Mac.

**Downside**: USB passthrough support limited on macOS

### Option 5: Wait for Apple/Intel Fix
This is an OS-level bug that needs Apple or Intel to fix.

**Downside**: Unknown timeline, may never happen

## 📁 Files in This Directory

### Working Scripts (RGB Only)
- `capture_rgb_stream.py` ⭐ **USE THIS** - Interactive RGB capture tool
- `test_opencv.py` - Camera detection and testing
- `test_camera.sh` - System diagnostic script

### Reference/Troubleshooting
- `README.md` - General setup guide
- `MACOS_WORKAROUNDS.md` - Detailed workaround documentation
- `STATUS.md` - This file
- `capture_depth.py` - Depth capture (won't work until SDK issue resolved)

### Output
- `captures/` - Directory for saved images/videos
- `realsense_rgb_capture.jpg` - Test capture proving RGB works

## 🎓 Recommendations

### For RGB-only Projects
**You're all set!** Use `capture_rgb_stream.py` and start building.

### For Projects Needing Depth
**Best Option**: Set up Ubuntu VM with USB passthrough
- Most reliable for depth access
- Full RealSense SDK support
- Can still use macOS for development, switch to VM for testing

**Alternative**: Develop on macOS with RGB, test depth on Linux machine

### For Quick Testing
Use Photo Booth or OpenCV to verify hardware is working, then decide on depth access method.

## 📊 System Information

```
Camera: Intel RealSense Depth Camera D435
macOS Version: 26.0.1 (Sequoia)
Architecture: ARM64 (Apple Silicon)
SDK Version: librealsense 2.57.4 (Homebrew)
Python: 3.11.4
OpenCV: 4.12.0.88

RGB Stream: ✓ WORKING (OpenCV/AVFoundation)
Depth Stream: ✗ NOT WORKING (SDK USB access issue)
```

## 🎉 Success Metrics

- Camera powered and recognized by macOS: ✓
- RGB capture working: ✓
- OpenCV integration working: ✓
- Sample images captured: ✓
- Video streaming working: ✓

**Your D435 camera IS working** - just limited to RGB until depth access resolved!
