# Quick Start Guide - RealSense D435

## ✅ Good News!
Your RealSense D435's **RGB camera is working perfectly** via OpenCV!

## 🚀 Try It Now!

### 1. Capture an Image
```bash
cd ~/Documents/Github/Depthcamera_testing
python3 capture_rgb_stream.py
# Choose option 1
```

### 2. Live Video Stream
```bash
python3 capture_rgb_stream.py
# Choose option 4
# Press 'q' to quit, 's' to save snapshots
```

### 3. Motion Detection Demo
```bash
python3 demo_motion_detection.py
```
Wave your hand in front of the camera - it will detect and highlight motion!

## 📂 Files You Need

### Main Scripts
- **`capture_rgb_stream.py`** - Interactive image/video capture
- **`demo_motion_detection.py`** - Cool motion detection demo
- **`test_opencv.py`** - Camera detection and testing

### Documentation
- **`STATUS.md`** - Current status and capabilities
- **`MACOS_WORKAROUNDS.md`** - Detailed troubleshooting

## ⚠️ Important Note

**RGB stream**: ✅ Working perfectly
**Depth stream**: ❌ Not accessible (macOS bug)

For depth access, you'll need to either:
1. Use Safe Mode (temporary testing)
2. Set up Linux VM with USB passthrough
3. Wait for macOS fix

But the RGB camera is fully functional for:
- Image capture
- Video recording
- Motion detection
- Object tracking (with additional code)
- Any standard computer vision tasks

## 🎯 Example Usage in Your Code

```python
import cv2

# Open RealSense RGB camera
cap = cv2.VideoCapture(1)

# Capture frame
ret, frame = cap.read()

if ret:
    # Do something with frame
    cv2.imwrite("my_image.jpg", frame)

cap.release()
```

## 🆘 Need Help?

Read `STATUS.md` for detailed information about what's working and what's not.

Check `MACOS_WORKAROUNDS.md` for solutions to get depth access.

## 🎉 You're Ready!

Your camera is set up and working. Start building!
