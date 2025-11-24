#!/bin/bash
# RealSense D435 Diagnostic Script

echo "========================================"
echo "RealSense D435 Camera Diagnostic"
echo "========================================"
echo ""

echo "1. Checking RealSense SDK installation..."
if command -v rs-enumerate-devices &> /dev/null; then
    echo "✓ RealSense SDK is installed"
    echo "   SDK version: $(rs-enumerate-devices --version 2>&1 | head -1 || echo 'Unable to determine')"
else
    echo "✗ RealSense SDK not found"
fi
echo ""

echo "2. Checking for connected RealSense devices..."
echo "   Running: rs-enumerate-devices"
echo "   ---"
rs-enumerate-devices 2>&1
echo "   ---"
echo ""

echo "3. Checking USB devices..."
system_profiler SPUSBDataType 2>&1 | grep -B 2 -A 10 -i "intel\|realsense" || echo "   No Intel/RealSense devices found in USB list"
echo ""

echo "4. Checking video devices..."
ls -la /dev/ | grep -i "video" || echo "   No video devices found"
echo ""

echo "5. System Information..."
echo "   OS: $(sw_vers -productName) $(sw_vers -productVersion)"
echo "   Architecture: $(uname -m)"
echo ""

echo "========================================"
echo "Troubleshooting Tips:"
echo "========================================"
echo "1. Try unplugging and replugging the camera"
echo "2. Try a different USB port (USB 3.0 preferred)"
echo "3. Check if the camera LED lights turn on"
echo "4. Try with a different USB cable"
echo "5. Restart your computer"
echo ""
echo "If issues persist, the camera may need:"
echo "- Firmware update"
echo "- Different USB controller"
echo "- Permissions reset (try running: sudo rs-enumerate-devices)"
echo "========================================"
