#!/usr/bin/env python3
"""
Embed keywords into image EXIF metadata for Photos app import.
After running this, import the tagged images into Photos app and keywords will be preserved.
"""

import json
from pathlib import Path
from typing import Dict, List
import argparse
import shutil


def embed_keywords_in_images(taxonomy_path: str, image_dir: str, output_dir: str):
    """
    Embed keywords into image EXIF metadata using exiftool.
    Requires exiftool to be installed.
    """
    print("🏷️  Embedding keywords in image metadata for Photos app...\n")

    # Check if exiftool is available
    import subprocess
    try:
        subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: exiftool not found")
        print("\nInstall with Homebrew:")
        print("  brew install exiftool")
        print("\nOr download from: https://exiftool.org/")
        return False

    # Load taxonomy
    with open(taxonomy_path, 'r') as f:
        taxonomy_data = json.load(f)

    images = taxonomy_data['images']
    image_dir_path = Path(image_dir).expanduser().resolve()
    output_dir_path = Path(output_dir).expanduser().resolve()
    output_dir_path.mkdir(exist_ok=True, parents=True)

    print(f"Input: {image_dir_path}")
    print(f"Output: {output_dir_path}")
    print(f"Images to process: {len(images)}\n")

    success_count = 0
    error_count = 0

    for i, img in enumerate(images, 1):
        filename = img['filename']
        source_path = image_dir_path / filename
        dest_path = output_dir_path / filename

        if not source_path.exists():
            print(f"[{i}/{len(images)}] ⚠️  Not found: {filename}")
            error_count += 1
            continue

        # Build keywords
        keywords = []

        # Add specialty
        if 'specialty' in img:
            keywords.append(img['specialty'])

        # Add urgency
        if 'urgency' in img:
            keywords.append(img['urgency'])

        # Add topic
        if 'topic' in img:
            keywords.append(img['topic'])

        # Add use case
        if 'use_case' in img:
            keywords.append(img['use_case'])

        # Add target audience
        if 'target_audience' in img:
            keywords.append(img['target_audience'])

        # Add key concepts (limit to first 10 to avoid too many keywords)
        if 'key_concepts' in img:
            keywords.extend(img['key_concepts'][:10])

        # Copy file to output directory
        shutil.copy2(source_path, dest_path)

        # Build exiftool command
        exiftool_args = ['exiftool', '-overwrite_original']

        # Add keywords
        for keyword in keywords:
            # Escape special characters
            safe_keyword = keyword.replace('"', '\\"')
            exiftool_args.append(f'-Keywords={safe_keyword}')

        # Add description
        if 'content_summary' in img:
            safe_desc = img['content_summary'].replace('"', '\\"')
            exiftool_args.append(f'-Description={safe_desc}')

        # Add title
        if 'topic' in img:
            safe_title = img['topic'].replace('"', '\\"')
            exiftool_args.append(f'-Title={safe_title}')

        # Add subject
        if 'specialty' in img:
            safe_subject = img['specialty'].replace('"', '\\"')
            exiftool_args.append(f'-Subject={safe_subject}')

        exiftool_args.append(str(dest_path))

        # Run exiftool
        try:
            result = subprocess.run(
                exiftool_args,
                capture_output=True,
                text=True,
                check=True
            )

            print(f"[{i}/{len(images)}] ✓ {filename}")
            print(f"           Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
            success_count += 1

        except subprocess.CalledProcessError as e:
            print(f"[{i}/{len(images)}] ✗ Error processing {filename}: {e.stderr}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Successfully tagged: {success_count} images")
    if error_count > 0:
        print(f"⚠️  Errors: {error_count}")
    print(f"{'='*60}\n")

    print("📸 Next steps:")
    print(f"  1. Open Photos app")
    print(f"  2. File → Import")
    print(f"  3. Select images from: {output_dir_path}")
    print(f"  4. Keywords will be automatically imported!")
    print(f"\n  Or drag the folder directly into Photos app.\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Embed keywords in image EXIF metadata for Photos app import"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON"
    )
    parser.add_argument(
        "-i", "--image-dir",
        required=True,
        help="Directory containing original images"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="photos_import",
        help="Output directory for tagged images (default: photos_import)"
    )

    args = parser.parse_args()

    # Check if taxonomy exists
    if not Path(args.taxonomy).exists():
        print(f"❌ Error: Taxonomy file not found: {args.taxonomy}")
        print("\nRun the organizer first:")
        print("  python medical_image_organizer.py /path/to/images")
        return 1

    # Check if image directory exists
    if not Path(args.image_dir).exists():
        print(f"❌ Error: Image directory not found: {args.image_dir}")
        return 1

    success = embed_keywords_in_images(args.taxonomy, args.image_dir, args.output_dir)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
