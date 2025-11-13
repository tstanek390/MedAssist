#!/usr/bin/env python3
"""
Add keywords to existing photos in Photos app using AppleScript.
Works with photos already imported into Photos app.
"""

import json
from pathlib import Path
import argparse
import subprocess


def generate_applescript(taxonomy_path: str, album_name: str = None):
    """
    Generate AppleScript to add keywords to photos in Photos app.
    """
    print("🍎 Generating AppleScript for Photos app...\n")

    # Load taxonomy
    with open(taxonomy_path, 'r') as f:
        taxonomy_data = json.load(f)

    images = taxonomy_data['images']

    # Build AppleScript
    applescript = """tell application "Photos"
    activate

    -- Wait for Photos to be ready
    delay 1

"""

    if album_name:
        applescript += f"""    -- Select album
    set targetAlbum to album "{album_name}"

"""

    for img in images:
        filename = img['filename']

        # Build keywords list
        keywords = []

        if 'specialty' in img:
            keywords.append(img['specialty'])
        if 'urgency' in img:
            keywords.append(img['urgency'])
        if 'topic' in img:
            keywords.append(img['topic'])
        if 'use_case' in img:
            keywords.append(img['use_case'])
        if 'target_audience' in img:
            keywords.append(img['target_audience'])
        if 'key_concepts' in img:
            keywords.extend(img['key_concepts'][:8])

        # Escape quotes in keywords
        safe_keywords = [k.replace('"', '\\"') for k in keywords]
        keywords_str = '", "'.join(safe_keywords)

        # AppleScript to find and tag this photo
        applescript += f"""
    -- Process: {filename}
    try
        set foundPhotos to search for "{filename}"
        if (count of foundPhotos) > 0 then
            set thePhoto to item 1 of foundPhotos
            set theKeywords to {{"{keywords_str}"}}
            repeat with kw in theKeywords
                make new keyword with properties {{name:kw}}
                add kw to thePhoto
            end repeat
        end if
    end try

"""

    applescript += """end tell
"""

    return applescript


def run_applescript(script: str, save_to_file: str = None):
    """Run or save AppleScript."""

    if save_to_file:
        # Save to file
        script_path = Path(save_to_file)
        with open(script_path, 'w') as f:
            f.write(script)
        print(f"✓ Saved AppleScript to: {script_path}")
        print(f"\nTo run:")
        print(f"  1. Open Script Editor app")
        print(f"  2. File → Open → {script_path}")
        print(f"  3. Click Run button")
        print(f"\n  Or run from terminal:")
        print(f"  osascript {script_path}")
        return True
    else:
        # Run directly
        print("⚡ Running AppleScript...")
        print("(This may take a while for many images)\n")

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                print("✅ Successfully added keywords to Photos app!")
                return True
            else:
                print(f"❌ Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  Script timed out. Try saving to file and running manually.")
            return False
        except Exception as e:
            print(f"❌ Error running AppleScript: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Add keywords to photos in Photos app using AppleScript"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON"
    )
    parser.add_argument(
        "-a", "--album",
        help="Specific album name in Photos app (optional)"
    )
    parser.add_argument(
        "-s", "--save",
        help="Save AppleScript to file instead of running (recommended for many images)"
    )

    args = parser.parse_args()

    # Check if taxonomy exists
    if not Path(args.taxonomy).exists():
        print(f"❌ Error: Taxonomy file not found: {args.taxonomy}")
        return 1

    # Generate AppleScript
    script = generate_applescript(args.taxonomy, args.album)

    # Run or save
    success = run_applescript(script, args.save)

    if success and not args.save:
        print("\n📸 Keywords added! Check Photos app:")
        print("  1. Select any image")
        print("  2. Press Cmd+I for info")
        print("  3. See keywords in the Info panel")
        print("\n  Now you can search by keyword in Photos app!")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
