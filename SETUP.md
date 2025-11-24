# Setup Guide - Virtual Environment

This project now uses a **Python virtual environment** to keep dependencies isolated from your other projects.

---

## ✅ Already Done (One-Time Setup)

The virtual environment has been created and all dependencies are installed:

- ✅ Virtual environment created in `venv/`
- ✅ Core packages installed:
  - opencv-python (Computer Vision)
  - numpy (Array operations)
  - mediapipe (Hand/Pose tracking)
  - pyzbar (QR/Barcode scanning)
  - scipy, matplotlib, jax (ML dependencies)

---

## 🚀 How to Use the Virtual Environment

### Method 1: Quick Activation (Recommended)

```bash
cd ~/Documents/GitHub/Depthcamera_testing
source activate.sh
```

This will:
- Activate the virtual environment
- Show installed packages
- Display quick commands

### Method 2: Manual Activation

```bash
cd ~/Documents/GitHub/Depthcamera_testing
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt.

---

## 🎯 Running Demos Inside Virtual Environment

### After Activation

```bash
# Method 1: Main launcher
python3 realsense_launcher.py

# Method 2: Direct demo execution
python3 demos/demo_generative_audio.py
python3 demos/demo_hand_tracking.py
python3 demos/demo_motion_detection.py
```

### One-Line Execution (Without Staying Activated)

```bash
# Run launcher
venv/bin/python3 realsense_launcher.py

# Run specific demo
venv/bin/python3 demos/demo_generative_audio.py
```

---

## 🔊 Adding Audio Support (Optional)

To enable **real audio output** in the generative audio demo:

### Inside Virtual Environment

```bash
source venv/bin/activate
pip install pyo
```

### Or Directly

```bash
venv/bin/pip install pyo
```

---

## 🛑 Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

Your terminal will return to normal (no more `(venv)` prefix).

---

## 📦 Managing Dependencies

### View Installed Packages

```bash
source venv/bin/activate
pip list
```

### Update a Package

```bash
source venv/bin/activate
pip install --upgrade opencv-python
```

### Add New Package

```bash
source venv/bin/activate
pip install <package-name>

# Then update requirements.txt
pip freeze > requirements.txt
```

### Reinstall All Dependencies

If you need to reinstall everything:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🗑️ Starting Fresh (Optional)

If you need to recreate the environment:

```bash
# Remove old environment
rm -rf venv/

# Create new one
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Testing the Setup

### Quick Test (No Camera Required)

```bash
source venv/bin/activate
python3 demos/test_generative_audio.py
```

This will test all modules without requiring camera access.

### Full Demo Test

```bash
source venv/bin/activate
python3 demos/demo_generative_audio.py
```

---

## 🔍 Troubleshooting

### "Command not found: source"

**Solution**: Make sure you're using bash or zsh:

```bash
bash activate.sh
```

### "No module named 'cv2'"

**Solution**: You're not in the virtual environment:

```bash
source venv/bin/activate
python3 your_script.py
```

### "Permission denied: activate.sh"

**Solution**: Make it executable:

```bash
chmod +x activate.sh
./activate.sh
```

### Virtual Environment Not Working

**Solution**: Recreate it:

```bash
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Project Structure with Virtual Environment

```
Depthcamera_testing/
├── venv/                      # 🔒 Virtual environment (isolated)
│   ├── bin/                   # Python executables
│   ├── lib/                   # Installed packages
│   └── ...
│
├── activate.sh                # ⚡ Quick activation script
├── requirements.txt           # 📦 Dependency list
├── .gitignore                 # 🚫 Excludes venv/ from git
│
├── realsense_launcher.py      # ⭐ Main launcher
├── demos/                     # All demo scripts
├── tools/                     # Capture tools
├── docs/                      # Documentation
└── outputs/                   # Generated content
```

---

## ⚙️ IDE/Editor Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

### PyCharm

1. Open Project Settings
2. Project → Python Interpreter
3. Add Interpreter → Existing Environment
4. Select: `~/Documents/GitHub/Depthcamera_testing/venv/bin/python`

---

## 💡 Why Virtual Environment?

**Benefits:**
- ✅ Isolated dependencies (won't affect other projects)
- ✅ Easy to recreate exact setup
- ✅ No version conflicts
- ✅ Clean system Python installation
- ✅ Easy to share (via requirements.txt)

**Without Virtual Environment:**
- ❌ Packages installed globally
- ❌ Potential version conflicts
- ❌ Harder to manage dependencies
- ❌ Risk of breaking other Python projects

---

## 📝 Quick Reference

```bash
# Activate environment
source venv/bin/activate

# Run demos
python3 realsense_launcher.py

# Run specific demo
python3 demos/demo_generative_audio.py

# Deactivate
deactivate

# One-liner (no activation needed)
venv/bin/python3 realsense_launcher.py
```

---

## 🆘 Need Help?

If you encounter issues:

1. Check you're in the project directory
2. Verify virtual environment is activated (`(venv)` in prompt)
3. Try recreating the environment
4. Check camera permissions: System Settings → Privacy & Security → Camera

---

**Your project is now fully isolated and ready to use!** 🎉
