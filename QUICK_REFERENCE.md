# 🎯 Quick Reference Card

## 🚀 Main Commands

### Start the Interactive Menu (EASIEST WAY)
```bash
cd ~/Documents/Github/Depthcamera_testing
python3 realsense_launcher.py
```

---

## 📸 Direct Commands

### Capture Tools
```bash
# Interactive capture
python3 tools/capture_rgb_stream.py

# Timelapse (5s interval, 10min duration)
python3 tools/timelapse_capture.py -i 5 -d 10

# Create video from timelapse
python3 tools/create_timelapse_video.py outputs/timelapse/[session]/
```

### Computer Vision Demos
```bash
# Motion detection
python3 demos/demo_motion_detection.py

# Face detection
python3 demos/demo_face_detection.py

# Object tracking
python3 demos/demo_object_tracking.py
```

### Diagnostics
```bash
# Test all cameras
python3 diagnostics/test_opencv.py

# System check
bash diagnostics/test_camera.sh
```

---

## 📂 Folder Guide

| Folder | Purpose | What's Inside |
|--------|---------|---------------|
| `tools/` | Capture tools | Image/video/timelapse capture |
| `demos/` | CV demos | Motion, face, object tracking |
| `diagnostics/` | Testing | Camera tests & diagnostics |
| `docs/` | Documentation | All guides & references |
| `outputs/captures/` | Your photos | Saved images & videos |
| `outputs/timelapse/` | Timelapses | Timelapse sessions |

---

## 📚 Important Docs

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `docs/QUICK_START.md` | Beginner's guide |
| `docs/INDEX.md` | Complete reference |
| `docs/STATUS.md` | What's working |
| `docs/DEPTH_ACCESS_GUIDE.md` | Get depth data |

---

## ⌨️ Keyboard Shortcuts (In Demos)

| Key | Action |
|-----|--------|
| `q` | Quit/Exit |
| `s` | Save snapshot |
| `r` | Reset/Restart |
| `e` | Toggle eyes (face demo) |
| `m` | Toggle smile (face demo) |

---

## 🎯 Common Tasks

**Take a photo**
```bash
python3 realsense_launcher.py
# Choose option 1
```

**Record video**
```bash
python3 realsense_launcher.py
# Choose option 3
```

**See all options**
```bash
python3 realsense_launcher.py
```

---

## 🆘 Quick Help

**Camera not working?**
```bash
bash diagnostics/test_camera.sh
```

**Find your photos**
```bash
open outputs/captures
```

**View documentation**
```bash
open docs/
```

---

## 💡 Tips

- All captures save to `outputs/captures/`
- Timelapse sessions save to `outputs/timelapse/`
- Press `s` in any demo to save a snapshot
- Press `q` in any demo to quit
- Use the launcher for easiest access!

---

**Print this for quick reference!**
