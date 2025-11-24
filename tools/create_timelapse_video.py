#!/usr/bin/env python3
"""
Create timelapse video from captured images
"""

import cv2
import sys
import os
import argparse
import glob
from pathlib import Path

def create_video_from_images(image_dir, output_video=None, fps=30):
    """
    Create video from a directory of images

    Args:
        image_dir: Directory containing images
        output_video: Output video path (auto-generated if None)
        fps: Frames per second for output video
    """
    print("=" * 50)
    print("Create Timelapse Video")
    print("=" * 50)
    print(f"\nInput directory: {image_dir}")

    # Find all images
    image_files = sorted(glob.glob(os.path.join(image_dir, "frame_*.jpg")))

    if not image_files:
        print("ERROR: No images found in directory")
        print("Looking for files matching: frame_*.jpg")
        return False

    print(f"✓ Found {len(image_files)} images")

    # Read first image to get dimensions
    first_image = cv2.imread(image_files[0])
    if first_image is None:
        print(f"ERROR: Cannot read first image: {image_files[0]}")
        return False

    height, width = first_image.shape[:2]
    print(f"✓ Image dimensions: {width}x{height}")

    # Generate output filename if not provided
    if output_video is None:
        dir_name = Path(image_dir).name
        output_video = os.path.join(image_dir, f"{dir_name}_video.mp4")

    print(f"✓ Output video: {output_video}")
    print(f"✓ FPS: {fps}")

    # Calculate duration
    duration = len(image_files) / fps
    print(f"✓ Video duration: {duration:.1f} seconds")

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    if not out.isOpened():
        print("ERROR: Cannot create video writer")
        return False

    print("\nCreating video...")
    print("Progress: ", end='', flush=True)

    # Write images to video
    for i, image_file in enumerate(image_files):
        # Read image
        frame = cv2.imread(image_file)

        if frame is None:
            print(f"\nWARNING: Cannot read image: {image_file}")
            continue

        # Write frame
        out.write(frame)

        # Progress indicator
        if (i + 1) % 10 == 0:
            progress = (i + 1) / len(image_files) * 100
            print(f"\rProgress: {progress:.0f}% ({i+1}/{len(image_files)})", end='', flush=True)

    print(f"\rProgress: 100% ({len(image_files)}/{len(image_files)})")

    # Release video writer
    out.release()

    print("\n" + "=" * 50)
    print("Video created successfully!")
    print("=" * 50)
    print(f"Output: {output_video}")
    print(f"Frames: {len(image_files)}")
    print(f"FPS: {fps}")
    print(f"Duration: {duration:.1f} seconds")

    # Get file size
    file_size = os.path.getsize(output_video)
    file_size_mb = file_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.1f} MB")
    print("=" * 50)

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Create timelapse video from captured images'
    )
    parser.add_argument(
        'image_dir',
        type=str,
        help='Directory containing timelapse images'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output video path (auto-generated if not specified)'
    )
    parser.add_argument(
        '-f', '--fps',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.image_dir):
        print(f"ERROR: Directory not found: {args.image_dir}")
        return 1

    success = create_video_from_images(
        image_dir=args.image_dir,
        output_video=args.output,
        fps=args.fps
    )

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
