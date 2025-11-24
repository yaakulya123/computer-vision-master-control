# RealSense D435 Camera Toolkit - Complete Index

## 🚀 Quick Start

**Just want to start using the camera?**
```bash
cd ~/Documents/Github/Depthcamera_testing
python3 realsense_launcher.py
```

This launches the interactive menu with all tools and demos!

---

## 📂 Project Structure

### 🎮 Interactive Launcher
- **`realsense_launcher.py`** - Master control center (START HERE!)

### 📸 Capture Tools
- **`capture_rgb_stream.py`** - Interactive image/video capture tool
- **`timelapse_capture.py`** - Create timelapse sequences
- **`create_timelapse_video.py`** - Convert timelapse images to video

### 🎯 Computer Vision Demos
- **`demo_motion_detection.py`** - Real-time motion detection
- **`demo_face_detection.py`** - Face, eye, and smile detection
- **`demo_object_tracking.py`** - Interactive object tracking

### 🔧 Diagnostic Tools
- **`test_opencv.py`** - Test all cameras and save samples
- **`test_camera.sh`** - System diagnostic script
- **`capture_depth.py`** - Depth capture (for when SDK works)

### 📚 Documentation

#### Getting Started
- **`QUICK_START.md`** ⭐ - Start here if you're new
- **`STATUS.md`** - Current capabilities and limitations
- **`INDEX.md`** - This file

#### Advanced Topics
- **`README.md`** - Full setup and installation guide
- **`DEPTH_ACCESS_GUIDE.md`** - How to access depth camera
- **`MACOS_WORKAROUNDS.md`** - Troubleshooting macOS issues

### 📁 Output Directories
- **`captures/`** - Saved images and videos
- **`timelapse/`** - Timelapse sessions

---

## 🎯 What Each Tool Does

### Interactive Launcher (`realsense_launcher.py`)
The main menu system. Run this to access everything.

**Features**:
- Easy menu navigation
- Launch any tool or demo
- View documentation
- Open output folders
- System diagnostics

**Usage**:
```bash
python3 realsense_launcher.py
```

### Capture Tools

#### RGB Stream Capture (`capture_rgb_stream.py`)
Capture images, stream video, or record to file.

**Options**:
1. Capture single image
2. Stream video (10 seconds)
3. Record video to file
4. Continuous stream

**Usage**:
```bash
python3 capture_rgb_stream.py
# Follow on-screen prompts
```

#### Timelapse Capture (`timelapse_capture.py`)
Capture images at regular intervals for timelapse creation.

**Usage**:
```bash
# Default: 5 second interval, 5 minute duration
python3 timelapse_capture.py

# Custom settings
python3 timelapse_capture.py -i 10 -d 30  # 10s interval, 30min duration
python3 timelapse_capture.py -i 2 -d 0    # 2s interval, infinite duration
```

**Controls during capture**:
- Ctrl+C to stop
- Preview window shows progress

#### Create Timelapse Video (`create_timelapse_video.py`)
Convert captured timelapse images into a video.

**Usage**:
```bash
python3 create_timelapse_video.py timelapse/timelapse_20241117_123456/
python3 create_timelapse_video.py path/to/images/ -f 60  # 60 FPS
```

### Computer Vision Demos

#### Motion Detection (`demo_motion_detection.py`)
Detects and highlights moving objects in real-time.

**Features**:
- Side-by-side view (RGB + motion mask)
- Bounding boxes around motion
- Motion statistics
- Snapshot capture

**Controls**:
- `q` - Quit
- `s` - Save snapshot
- `r` - Reset background model

**Usage**:
```bash
python3 demo_motion_detection.py
```

#### Face Detection (`demo_face_detection.py`)
Detects faces, eyes, and smiles using Haar Cascades.

**Features**:
- Multi-face detection
- Eye detection
- Smile detection
- Real-time statistics

**Controls**:
- `q` - Quit
- `s` - Save snapshot
- `e` - Toggle eye detection
- `m` - Toggle smile detection
- `f` - Toggle face-only mode

**Usage**:
```bash
python3 demo_face_detection.py
```

#### Object Tracking (`demo_object_tracking.py`)
Track any object you select with your mouse.

**Features**:
- 4 tracking algorithms (CSRT, KCF, MOSSE, MedianFlow)
- Visual path history
- Position tracking
- Success rate statistics

**Controls**:
- Select object with mouse
- `q` - Quit
- `s` - Save snapshot
- `r` - Reset and select new object

**Usage**:
```bash
python3 demo_object_tracking.py
# Choose tracking algorithm
# Select object with mouse
# Press ENTER to start
```

### Diagnostic Tools

#### Test OpenCV (`test_opencv.py`)
Scans all cameras and captures test images.

**Output**:
- Lists all detected cameras
- Tests each camera
- Saves sample images
- Shows camera capabilities

**Usage**:
```bash
python3 test_opencv.py
```

#### System Diagnostic (`test_camera.sh`)
Comprehensive system diagnostic.

**Checks**:
- RealSense SDK installation
- Connected devices
- USB devices
- Video devices
- System information

**Usage**:
```bash
./test_camera.sh
```

---

## 💡 Common Tasks

### Take a Photo
```bash
python3 realsense_launcher.py
# Choose option 1
```

### Record a Video
```bash
python3 realsense_launcher.py
# Choose option 3
```

### Create a Timelapse
```bash
# 1. Capture images
python3 timelapse_capture.py -i 5 -d 10  # 5s interval, 10min

# 2. Create video
python3 create_timelapse_video.py timelapse/[session_name]/
```

### Detect Faces
```bash
python3 demo_face_detection.py
```

### Track an Object
```bash
python3 demo_object_tracking.py
```

### Check Camera Status
```bash
./test_camera.sh
```

---

## 📖 Learning Path

### Beginner
1. Read **`QUICK_START.md`**
2. Run **`realsense_launcher.py`**
3. Try **capturing an image** (option 1)
4. Try **motion detection** demo (option 5)

### Intermediate
1. Explore **face detection** demo
2. Try **object tracking** demo
3. Create a **timelapse**
4. Read **`STATUS.md`** to understand capabilities

### Advanced
1. Read **`DEPTH_ACCESS_GUIDE.md`**
2. Set up Linux VM for depth access
3. Modify the Python scripts for your needs
4. Integrate with your own projects

---

## 🆘 Troubleshooting

### Camera Not Working
1. Run `./test_camera.sh`
2. Check `STATUS.md`
3. Read `MACOS_WORKAROUNDS.md`

### Want Depth Data
1. Read `DEPTH_ACCESS_GUIDE.md`
2. Consider Linux VM setup
3. Check Safe Mode option for testing

### OpenCV Errors
```bash
pip3 install --upgrade opencv-python
```

### Permission Issues
- Check System Settings → Privacy & Security → Camera
- Ensure RealSense is allowed

---

## 🎓 Code Examples

### Simple Image Capture
```python
import cv2

cap = cv2.VideoCapture(1)  # RealSense is camera 1
ret, frame = cap.read()

if ret:
    cv2.imwrite("my_photo.jpg", frame)

cap.release()
```

### Video Stream with Preview
```python
import cv2

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('RealSense', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 📊 Features Summary

| Feature | Status | Script |
|---------|--------|--------|
| RGB Image Capture | ✅ Working | capture_rgb_stream.py |
| RGB Video Stream | ✅ Working | capture_rgb_stream.py |
| Video Recording | ✅ Working | capture_rgb_stream.py |
| Timelapse Creation | ✅ Working | timelapse_capture.py |
| Motion Detection | ✅ Working | demo_motion_detection.py |
| Face Detection | ✅ Working | demo_face_detection.py |
| Object Tracking | ✅ Working | demo_object_tracking.py |
| Depth Stream | ❌ macOS bug | See DEPTH_ACCESS_GUIDE.md |
| Point Cloud | ❌ macOS bug | Requires depth access |
| IR Cameras | ❌ macOS bug | Requires SDK access |

---

## 🔗 Useful Links

- [Intel RealSense GitHub](https://github.com/IntelRealSense/librealsense)
- [macOS Bug Report](https://github.com/IntelRealSense/librealsense/issues/9916)
- [LightBuzz macOS Guide](https://lightbuzz.com/realsense-macos/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [UTM (Free VM for Mac)](https://mac.getutm.app/)

---

## 🎉 You're Ready!

Your RealSense D435 RGB camera is fully set up and ready to use!

**Start exploring**:
```bash
python3 realsense_launcher.py
```

**Happy coding!** 🚀
