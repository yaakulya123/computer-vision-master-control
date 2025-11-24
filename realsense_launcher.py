#!/usr/bin/env python3
"""
RealSense D435 Camera - Master Launcher
Interactive menu to access all camera tools and demos
"""

import sys
import os
import subprocess

def print_header():
    """Print the application header"""
    print("\n" + "=" * 60)
    print("  Intel RealSense D435 Camera Control Center")
    print("=" * 60)

def print_menu():
    """Print the main menu"""
    print("\n📸 CAPTURE TOOLS:")
    print("  1. Single Image Capture")
    print("  2. Video Stream (Live Preview)")
    print("  3. Record Video to File")
    print("  4. Timelapse Capture")
    print()
    print("🎯 COMPUTER VISION DEMOS:")
    print("  5. Motion Detection")
    print("  6. Face Detection")
    print("  7. Object Tracking")
    print("  8. Generative Audio (Body-Responsive Sound) 🎵")
    print()
    print("🔧 DIAGNOSTIC TOOLS:")
    print("  9. Test All Cameras")
    print("  10. System Diagnostic")
    print("  11. Camera Information")
    print()
    print("📚 UTILITIES:")
    print("  12. Create Video from Timelapse Images")
    print("  13. Open Captures Folder")
    print("  14. View Documentation")
    print()
    print("  0. Exit")
    print()

def run_script(script_name, args=None):
    """Run a Python script"""
    cmd = ['python3', script_name]
    if args:
        cmd.extend(args)

    try:
        subprocess.run(cmd, check=False)
        return True
    except FileNotFoundError:
        print(f"ERROR: Script not found: {script_name}")
        return False
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
        return True

def run_bash_script(script_name):
    """Run a bash script"""
    try:
        subprocess.run(['bash', script_name], check=False)
        return True
    except FileNotFoundError:
        print(f"ERROR: Script not found: {script_name}")
        return False

def open_folder(folder_path):
    """Open a folder in Finder"""
    os.makedirs(folder_path, exist_ok=True)
    subprocess.run(['open', folder_path])

def view_file(file_path):
    """Open a file with default application"""
    if os.path.exists(file_path):
        subprocess.run(['open', file_path])
    else:
        print(f"File not found: {file_path}")

def handle_choice(choice):
    """Handle user menu choice"""

    if choice == '1':
        print("\n🎯 Launching Single Image Capture...")
        run_script('tools/capture_rgb_stream.py')

    elif choice == '2':
        print("\n🎥 Launching Video Stream...")
        print("TIP: Press 's' to save snapshots, 'q' to quit")
        run_script('tools/capture_rgb_stream.py')

    elif choice == '3':
        print("\n🎬 Launching Video Recorder...")
        run_script('tools/capture_rgb_stream.py')

    elif choice == '4':
        print("\n⏱️  Launching Timelapse Capture...")
        print("\nDefault settings: 5 second interval, 5 minute duration")
        custom = input("Use custom settings? (y/N): ").strip().lower()

        if custom == 'y':
            try:
                interval = input("Interval between captures (seconds, default=5): ").strip() or "5"
                duration = input("Total duration (minutes, 0=infinite, default=5): ").strip() or "5"
                run_script('tools/timelapse_capture.py', ['-i', interval, '-d', duration])
            except ValueError:
                print("Invalid input, using defaults")
                run_script('tools/timelapse_capture.py')
        else:
            run_script('tools/timelapse_capture.py')

    elif choice == '5':
        print("\n🔍 Launching Motion Detection Demo...")
        print("TIP: Move in front of the camera to see motion detection")
        run_script('demos/demo_motion_detection.py')

    elif choice == '6':
        print("\n😊 Launching Face Detection Demo...")
        print("TIP: Look at the camera to detect faces, eyes, and smiles")
        run_script('demos/demo_face_detection.py')

    elif choice == '7':
        print("\n🎯 Launching Object Tracking Demo...")
        print("TIP: Select an object with your mouse, then press ENTER")
        run_script('demos/demo_object_tracking.py')

    elif choice == '8':
        print("\n🎵 Launching Generative Audio Demo...")
        print("TIP: Move your body to create sound! Stillness = harmony, motion = chaos")
        print("     Press 'A' during demo to enable audio synthesis")
        run_script('demos/demo_generative_audio.py')

    elif choice == '9':
        print("\n🔍 Testing All Cameras...")
        run_script('diagnostics/test_opencv.py')

    elif choice == '10':
        print("\n🔧 Running System Diagnostic...")
        run_bash_script('diagnostics/test_camera.sh')

    elif choice == '11':
        print("\n📊 Camera Information:")
        print("-" * 60)
        subprocess.run(['system_profiler', 'SPCameraDataType'])
        print("-" * 60)
        input("\nPress ENTER to continue...")

    elif choice == '12':
        print("\n🎬 Create Video from Timelapse Images")
        print("\nAvailable timelapse sessions:")

        if os.path.exists('outputs/timelapse'):
            sessions = [d for d in os.listdir('outputs/timelapse')
                       if os.path.isdir(os.path.join('outputs/timelapse', d))]

            if sessions:
                for i, session in enumerate(sorted(sessions), 1):
                    print(f"  {i}. {session}")

                try:
                    choice_num = int(input("\nSelect session number: "))
                    if 1 <= choice_num <= len(sessions):
                        session_dir = os.path.join('outputs/timelapse', sorted(sessions)[choice_num-1])
                        fps = input("FPS for video (default=30): ").strip() or "30"
                        run_script('tools/create_timelapse_video.py', [session_dir, '-f', fps])
                    else:
                        print("Invalid selection")
                except (ValueError, IndexError):
                    print("Invalid input")
            else:
                print("  No timelapse sessions found")
        else:
            print("  No timelapse directory found")

        input("\nPress ENTER to continue...")

    elif choice == '13':
        print("\n📁 Opening Captures Folder...")
        open_folder('outputs/captures')

    elif choice == '14':
        print("\n📚 Documentation:")
        print("  1. Quick Start Guide")
        print("  2. Current Status")
        print("  3. macOS Workarounds")
        print("  4. Full README")

        doc_choice = input("\nSelect document (1-4): ").strip()

        doc_map = {
            '1': 'docs/QUICK_START.md',
            '2': 'docs/STATUS.md',
            '3': 'docs/MACOS_WORKAROUNDS.md',
            '4': 'docs/README.md'
        }

        if doc_choice in doc_map:
            view_file(doc_map[doc_choice])
        else:
            print("Invalid selection")

    elif choice == '0':
        return False

    else:
        print("\n❌ Invalid choice. Please try again.")

    return True

def main():
    """Main application loop"""

    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Create necessary directories
    os.makedirs('outputs/captures', exist_ok=True)
    os.makedirs('outputs/timelapse', exist_ok=True)

    while True:
        print_header()
        print_menu()

        try:
            choice = input("Select an option: ").strip()

            if not handle_choice(choice):
                print("\n👋 Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress ENTER to continue...")

    return 0

if __name__ == "__main__":
    sys.exit(main())
