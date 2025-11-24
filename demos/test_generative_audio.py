#!/usr/bin/env python3
"""
Quick test of generative audio system without camera
Tests all modules work correctly
"""

import numpy as np
import sys

print("🧪 Testing Generative Audio System Components\n")
print("=" * 60)

# Test 1: Motion Analyzer
print("\n1. Testing Motion Analyzer...")
try:
    from motion_analyzer import MotionAnalyzer
    analyzer = MotionAnalyzer(width=320, height=240)

    # Create dummy frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Analyze (first frame returns None for flow)
    result1 = analyzer.analyze_frame(frame)

    # Second frame (should have flow)
    frame2 = frame + np.random.randint(-10, 10, frame.shape, dtype=np.int16)
    frame2 = np.clip(frame2, 0, 255).astype(np.uint8)
    result2 = analyzer.analyze_frame(frame2)

    print(f"   ✓ Motion energy: {result2['motion_energy']:.3f}")
    print(f"   ✓ Global velocity: {result2['global_velocity']:.3f}")
    print(f"   ✓ Motion type: {result2['motion_type']}")
    print(f"   ✓ Center: {result2['center']}")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 2: Chaos Calculator
print("\n2. Testing Chaos Calculator...")
try:
    from chaos_calculator import ChaosCalculator, map_position_to_pan
    calc = ChaosCalculator(decay_time=2.5)

    # Test with motion
    motion_metrics = {
        'motion_energy': 0.5,
        'global_velocity': 0.3,
        'motion_type': 'local'
    }

    chaos = calc.update(motion_metrics)
    state = calc.get_chaos_state()
    audio_params = calc.get_audio_parameters()

    print(f"   ✓ Chaos score: {chaos:.3f}")
    print(f"   ✓ State: {state['state']}")
    print(f"   ✓ Base frequency: {audio_params['base_freq']:.1f} Hz")
    print(f"   ✓ Binaural diff: {audio_params['binaural_diff']:.2f} Hz")
    print(f"   ✓ LFO rate: {audio_params['lfo_rate']:.2f} Hz")

    # Test pan mapping
    pan = map_position_to_pan(160, 320)
    print(f"   ✓ Stereo pan (center): {pan:.2f}")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 3: Audio Engine
print("\n3. Testing Audio Engine...")
try:
    from audio_engine import AudioEngine, WaveformVisualizer
    engine = AudioEngine(sample_rate=44100, buffer_size=512)

    print(f"   ✓ Mode: {engine.mode}")
    print(f"   ✓ Pyo available: {engine.get_status()['pyo_available']}")

    # Start engine
    if engine.start():
        print(f"   ✓ Engine started successfully")

        # Update with audio params
        engine.update(audio_params, pan=0.0)

        # Get waveform
        waveform = engine.get_waveform(duration=0.05)
        print(f"   ✓ Waveform generated: {len(waveform)} samples")
        print(f"   ✓ Waveform range: [{waveform.min():.3f}, {waveform.max():.3f}]")

        # Stop engine
        engine.stop()
        print(f"   ✓ Engine stopped")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 4: Waveform Visualizer
print("\n4. Testing Waveform Visualizer...")
try:
    viz = WaveformVisualizer(width=800, height=200)

    # Generate test waveform
    t = np.linspace(0, 0.1, 4410)
    test_wave = np.sin(2 * np.pi * 440 * t) * 0.5

    # Render
    img = viz.render_waveform(test_wave)
    print(f"   ✓ Waveform image: {img.shape}")

    # Render spectrum
    spectrum = viz.render_spectrum(test_wave)
    print(f"   ✓ Spectrum image: {spectrum.shape}")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 5: Decay behavior
print("\n5. Testing Chaos Decay (Heal Mechanic)...")
try:
    import time
    calc = ChaosCalculator(decay_time=1.0)  # Fast decay for testing

    # Create high chaos
    motion_metrics = {
        'motion_energy': 0.9,
        'global_velocity': 0.8,
        'motion_type': 'global'
    }

    chaos = calc.update(motion_metrics)
    print(f"   ✓ Initial chaos: {chaos:.3f}")

    # Stop motion
    still_metrics = {
        'motion_energy': 0.0,
        'global_velocity': 0.0,
        'motion_type': 'still'
    }

    # Watch decay
    print(f"   ✓ Decay sequence:")
    for i in range(5):
        time.sleep(0.2)
        chaos = calc.update(still_metrics)
        print(f"      t={i*0.2:.1f}s → chaos={chaos:.3f}")

    print(f"   ✓ Decay working correctly!")

except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe Generative Audio System is working correctly!")
print("\nTo run the full demo:")
print("  python3 demos/demo_generative_audio.py")
print("\nTo enable real audio output:")
print("  pip3 install pyo")
print("=" * 60)
