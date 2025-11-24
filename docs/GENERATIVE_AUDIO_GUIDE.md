# Generative Audio System Guide

## The "Heal Mechanic" - Body-Responsive Sound Synthesis

A real-time generative audio system where your body movements control sound synthesis. Stillness creates harmonic healing drones, movement creates sonic chaos.

---

## Concept Overview

### The Core Idea
Your body becomes a musical instrument. The system analyzes your movement and translates it into procedurally generated audio in real-time.

**Movement → Sound Mapping:**
- **Stillness** (Chaos: 0.0) → Ethereal binaural drone (100Hz + 105Hz)
- **Gentle Motion** (Chaos: 0.5) → Rippling vibrato effect (arm waving)
- **High Motion** (Chaos: 1.0) → Scattered chaos (walking, running)

### The "Healing" Transition
When you stop moving, the chaos doesn't snap back instantly. Instead, it **decays smoothly over 2-3 seconds**, creating a natural "healing" effect as the sound returns to the harmonic drone.

---

## Quick Start

### Running the Demo

```bash
# From project root
python3 realsense_launcher.py
# Select option 8: Generative Audio

# Or run directly
python3 demos/demo_generative_audio.py
```

### Initial Setup (No Pyo Required)
The system works **immediately** in **SIMULATION mode**:
- ✅ Full motion detection
- ✅ Chaos score calculation
- ✅ Visual feedback (heatmap, chaos meter, waveform)
- ⚠️  Audio synthesis visualization only (no sound output)

### Full Audio Setup (Optional - Pyo)
For **real audio output**, install Pyo:

```bash
# Install Pyo audio library
pip3 install pyo

# Restart the demo - it will automatically detect Pyo
python3 demos/demo_generative_audio.py
```

---

## Controls

| Key | Action |
|-----|--------|
| **Q** | Quit demo |
| **S** | Save snapshot |
| **A** | Toggle audio engine ON/OFF |
| **H** | Toggle motion heatmap overlay |
| **M** | Toggle chaos meter (vertical bar) |
| **W** | Toggle waveform visualization |
| **SPACE** | Reset chaos to 0 instantly |

---

## System Architecture

### Four Core Modules

#### 1. Motion Analyzer (`motion_analyzer.py`)
**Purpose:** Analyze video frames to detect and classify movement

**Features:**
- **Dense Optical Flow**: Sophisticated per-pixel movement tracking
- **Frame Delta**: Simple pixel difference for quick energy calculation
- **Center of Mass Tracking**: Track your body's global position
- **Motion Classification**: Differentiate between:
  - `still`: No movement
  - `local`: Arm waving (high energy, low displacement)
  - `global`: Walking/running (high energy, high displacement)

**Key Functions:**
```python
motion_analyzer = MotionAnalyzer(width=320, height=240)
metrics = motion_analyzer.analyze_frame(frame)

# Returns:
# {
#   'motion_energy': 0.0-1.0,
#   'global_velocity': 0.0-1.0,
#   'center': (x, y),
#   'motion_type': 'still'|'local'|'global',
#   'flow': optical_flow_array,
#   'flow_visualization': visualization_image
# }
```

#### 2. Chaos Calculator (`chaos_calculator.py`)
**Purpose:** Convert motion metrics into unified chaos score (0.0-1.0)

**Features:**
- **Smooth Transitions**: Exponential smoothing for natural feel
- **Time-Based Decay**: Automatic "healing" when movement stops
- **Audio Parameter Mapping**: Generates all synthesis parameters

**Chaos States:**
| Score | State | Description | Audio Characteristics |
|-------|-------|-------------|----------------------|
| 0.0-0.2 | Still | Frozen, no movement | Pure binaural drone (100Hz) |
| 0.2-0.5 | Gentle | Arm waving, standing | Drone + tremolo ripple |
| 0.5-0.8 | Active | Walking, gestures | Rising pitch + FM modulation |
| 0.8-1.0 | Chaos | Running, jumping | High pitch + granular scatter |

**Key Functions:**
```python
chaos_calc = ChaosCalculator(decay_time=2.5)
chaos_score = chaos_calc.update(motion_metrics)
audio_params = chaos_calc.get_audio_parameters()

# audio_params contains:
# {
#   'base_freq': 100-800 Hz,
#   'binaural_diff': 5-0.5 Hz,
#   'lfo_rate': 0-12 Hz,
#   'fm_amount': 0-1000,
#   'noise_amount': 0-1.0,
#   'grain_rate': 0-100/sec
# }
```

#### 3. Audio Engine (`audio_engine.py`)
**Purpose:** Generate real-time procedural audio

**Two Modes:**

**SIMULATION Mode** (Default - No Pyo):
- Generates mock audio data for visualization
- Full visual feedback (waveform, spectrum)
- No actual sound output

**REAL Mode** (Pyo Installed):
- Actual audio synthesis using Pyo DSP library
- Real-time parameter modulation
- Stereo spatial audio

**Synthesis Techniques:**
- **Binaural Beats**: Two sine waves (100Hz + 105Hz) create 5Hz pulsation
- **Amplitude Modulation (Tremolo)**: LFO modulates volume for ripple effect
- **Frequency Modulation (FM)**: Creates complex timbres for chaos
- **Granular Synthesis**: Chops sound into tiny grains for scatter effect
- **Noise Generation**: Adds static texture at high chaos levels

#### 4. Main Demo (`demo_generative_audio.py`)
**Purpose:** Integrates all components with visual feedback

**Visual Feedback Systems:**
- **Motion Heatmap**: Color-coded overlay showing movement intensity
- **Chaos Meter**: Vertical bar graph (0.0-1.0) with color gradient
- **Waveform Display**: Real-time audio waveform visualization
- **HUD Overlay**: Status panel with all metrics

---

## How It Works: Technical Deep Dive

### Motion Detection Pipeline

```
Video Frame
    ↓
[Preprocess]
- Resize to 320x240
- Convert to grayscale
- Gaussian blur (noise reduction)
    ↓
[Optical Flow Calculation]
- Dense optical flow (Farneback algorithm)
- Calculates movement vector for every pixel
    ↓
[Motion Metrics]
- Motion Energy: Average flow magnitude
- Center of Mass: Weighted position of motion
- Global Velocity: Center displacement per frame
    ↓
[Motion Classification]
- Still: energy < 0.15
- Local: high energy, low velocity (waving)
- Global: high energy, high velocity (walking)
```

### Chaos Score Calculation

```
Motion Metrics
    ↓
[Raw Chaos Calculation]
- Still: target = 0.0
- Local: target = 0.3-0.7 (weighted towards energy)
- Global: target = 0.5-1.0 (weighted towards velocity)
    ↓
[Exponential Smoothing]
- Alpha = 0.4 (active motion)
- Alpha = 0.1 (decaying)
- Smoothed = α·target + (1-α)·current
    ↓
[Time-Based Decay]
- If still: chaos *= exp(-t/2.5)
- Decays to 0 over 2.5 seconds
    ↓
Final Chaos Score (0.0-1.0)
```

### Audio Parameter Mapping

| Parameter | Chaos 0.0 | Chaos 0.5 | Chaos 1.0 | Effect |
|-----------|-----------|-----------|-----------|--------|
| **Base Freq** | 100 Hz | 450 Hz | 800 Hz | Pitch rises |
| **Binaural Diff** | 5 Hz | 2.5 Hz | 0.5 Hz | Beat slows |
| **LFO Rate** | 0 Hz | 6 Hz | 12 Hz | Faster tremolo |
| **LFO Depth** | 0 | 1.0 (max) | 0 | Peak at mid-chaos |
| **FM Amount** | 0 | 250 | 1000 | Distortion increases |
| **Noise** | 0 | 0 | 0.75 | Static at high chaos |
| **Grain Rate** | 0 | 50/sec | 100/sec | Scatter effect |

### Spatial Audio (Stereo Panning)

Your **horizontal position** in the frame maps to stereo position:

```
Left side of frame     Center          Right side of frame
      │                  │                      │
      ▼                  ▼                      ▼
   Pan = -1.0         Pan = 0.0              Pan = 1.0
   (Full left)        (Center)              (Full right)
```

---

## Using Pyo for Real Audio

### Installation

```bash
# macOS
pip3 install pyo

# Linux
sudo apt-get install python3-pyo
pip3 install pyo

# Windows
pip3 install pyo
```

### Pyo Architecture (When Implemented)

```python
# Binaural Drone
left_osc = Sine(freq=100, mul=0.3)
right_osc = Sine(freq=105, mul=0.3)

# LFO for Tremolo
lfo = Sine(freq=lfo_rate, mul=0.5, add=0.5)
modulated = left_osc * lfo

# FM Synthesis
modulator = Sine(freq=base_freq * 2)
carrier = Sine(freq=base_freq + modulator * fm_amount)

# Stereo Pan
panned = Pan(modulated, outs=2, pan=pan_value)
output = panned.out()
```

### Current Implementation Status

**✅ Implemented:**
- Basic binaural drone (two sine waves)
- LFO tremolo modulation
- Stereo panning
- Real-time parameter updates

**🚧 TODO (When Pyo is installed):**
- FM synthesis for chaos effect
- Granular synthesis for scatter effect
- Noise generator for high chaos
- Reverb/delay for atmosphere

---

## Customization

### Adjusting Decay Time

Edit `chaos_calculator.py`:

```python
# Slower healing (5 seconds)
chaos_calc = ChaosCalculator(decay_time=5.0)

# Faster healing (1 second)
chaos_calc = ChaosCalculator(decay_time=1.0)
```

### Changing Motion Weights

```python
# Favor local motion (arm waving matters more)
chaos_calc = ChaosCalculator(
    local_weight=0.8,
    global_weight=0.2
)

# Favor global motion (walking matters more)
chaos_calc = ChaosCalculator(
    local_weight=0.3,
    global_weight=0.7
)
```

### Modifying Audio Parameters

Edit `chaos_calculator.py` → `get_audio_parameters()`:

```python
# Change frequency range
base_freq = 50 + (chaos * 1000)  # Wider range: 50-1050 Hz

# Change binaural beat range
binaural_diff = 10.0 - (chaos * 9.0)  # 10Hz to 1Hz

# More aggressive FM
fm_amount = chaos ** 1.5 * 2000  # Stronger distortion
```

### Adjusting Optical Flow Sensitivity

Edit `motion_analyzer.py`:

```python
self.flow_params = {
    'pyr_scale': 0.5,
    'levels': 3,
    'winsize': 15,      # Increase for smoother flow
    'iterations': 3,    # Increase for accuracy
    'poly_n': 5,
    'poly_sigma': 1.2,
    'flags': 0
}
```

---

## Troubleshooting

### "Pyo not installed" Warning
**Expected behavior** - system runs in SIMULATION mode. Install Pyo for real audio.

### Camera Not Found
```bash
# Test cameras
python3 diagnostics/test_opencv.py

# Check camera permissions
# System Settings → Privacy & Security → Camera
```

### Motion Detection Too Sensitive
Decrease motion energy threshold in `chaos_calculator.py`:

```python
def classify_motion_type(self, motion_energy, global_velocity, threshold=0.2):
    # Default is 0.3, increase to 0.4 or 0.5 for less sensitivity
```

### Chaos Not Decaying
Check decay time setting:

```python
# In demo_generative_audio.py
self.chaos_calculator = ChaosCalculator(decay_time=2.5)
```

### Waveform Not Showing
Press **'W'** during demo to toggle waveform display.

### Audio Crackling/Glitching (Pyo)
Increase buffer size in `audio_engine.py`:

```python
self.audio_engine = AudioEngine(
    sample_rate=44100,
    buffer_size=1024  # Increase from 512
)
```

---

## Performance Optimization

### For Better Frame Rate

**Reduce Motion Analyzer Resolution:**
```python
self.motion_analyzer = MotionAnalyzer(width=160, height=120)  # Half size
```

**Disable Visual Feedback:**
- Press **'H'** to hide heatmap
- Press **'W'** to hide waveform

**Lower Camera Resolution:**
Edit `demo_generative_audio.py`:
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Down from 1920
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Down from 1080
```

### For Better Audio Quality (Pyo)

**Increase Sample Rate:**
```python
self.audio_engine = AudioEngine(sample_rate=48000)  # Up from 44100
```

---

## Future Enhancements

### Planned Features
- [ ] **Depth Camera Integration** (when Linux VM available)
  - True 3D position tracking
  - Distance-based volume control
  - Depth-based audio filtering

- [ ] **Gesture Recognition**
  - Specific hand gestures trigger musical notes
  - Pose-based sound effects

- [ ] **Recording/Playback**
  - Save motion + audio sessions
  - Replay performances

- [ ] **MIDI Output**
  - Control external synthesizers
  - Integration with DAWs

- [ ] **Multi-Person Mode**
  - Track multiple bodies
  - Polyphonic audio (each person = voice)

---

## Technical References

### Optical Flow
- **Algorithm**: Farneback Dense Optical Flow
- **Paper**: Farneback, G. (2003). "Two-Frame Motion Estimation Based on Polynomial Expansion"
- **OpenCV Docs**: https://docs.opencv.org/master/d4/dee/tutorial_optical_flow.html

### Binaural Beats
- **Frequency Range**: 1-30 Hz difference
- **Effects**: 5Hz = theta waves (relaxation), 10Hz = alpha waves (focus)
- **Science**: https://en.wikipedia.org/wiki/Beat_(acoustics)#Binaural_beats

### Pyo Audio Library
- **Docs**: http://ajaxsoundstudio.com/pyodoc/
- **GitHub**: https://github.com/belangeo/pyo
- **Tutorials**: http://ajaxsoundstudio.com/pyodoc/tutorials/index.html

---

## Credits & Inspiration

**Concept**: "Heal Mechanic" - stillness as healing, movement as chaos

**Influences**:
- Brian Eno - Generative Music
- Imogen Heap - Mi.Mu Gloves (gesture-controlled music)
- David Rokeby - "Very Nervous System" (movement-based interactive art)

**Technologies**:
- Intel RealSense D435 Camera
- OpenCV - Computer Vision
- Pyo - Digital Signal Processing
- Python - Integration

---

## Contact & Contribution

Found a bug? Have an enhancement idea?

**Project Location**: `Depthcamera_testing/`
**Demo Files**: `demos/demo_generative_audio.py` and supporting modules
**Documentation**: `docs/GENERATIVE_AUDIO_GUIDE.md` (this file)

---

**🎵 Now go make some beautiful chaos! 🎵**
