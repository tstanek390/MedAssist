#!/usr/bin/env python3
"""
Medical Image Organizer - Standalone Script
A simple, all-in-one script for organizing medical images using Claude Vision API.

Usage:
    python medical_image_organizer.py /path/to/images --api-key YOUR_KEY

Or set ANTHROPIC_API_KEY environment variable:
    export ANTHROPIC_API_KEY='your-key'
    python medical_image_organizer.py /path/to/images
"""

import os
import sys
import json
import base64
import csv
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

# Check for required packages
try:
    import anthropic
except ImportError:
    print("Error: Required package 'anthropic' not found.")
    print("Install it with: pip install anthropic")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Required package 'pillow' not found.")
    print("Install it with: pip install pillow")
    sys.exit(1)


class MedicalImageOrganizer:
    """All-in-one medical image organizer using Claude Vision API."""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    COST_PER_IMAGE = 0.012  # Approximate cost in USD

    def __init__(self, api_key: str, input_dir: str, output_dir: str = "output"):
        """Initialize the organizer."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.input_dir = Path(input_dir).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.output_dir.mkdir(exist_ok=True)

        self.results = []
        self.errors = []
        self.total_cost = 0.0

    def get_image_files(self) -> List[Path]:
        """Get all supported image files from input directory."""
        if not self.input_dir.exists():
            raise ValueError(f"Directory does not exist: {self.input_dir}")

        if not self.input_dir.is_dir():
            raise ValueError(f"Not a directory: {self.input_dir}")

        images = []
        for file_path in sorted(self.input_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append(file_path)

        return images

    def encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64 and determine media type."""
        ext = image_path.suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        return image_data, media_type

    def analyze_image(self, image_path: Path) -> Optional[Dict]:
        """Analyze a single image using Claude Vision API."""
        print(f"\n📸 Analyzing: {image_path.name}")

        try:
            image_data, media_type = self.encode_image(image_path)

            prompt = """Analyze this medical infographic/image and extract the following information:

1. **Specialty**: What medical specialty does this relate to? (e.g., Cardiology, Neurology, Emergency Medicine, etc.)
2. **Topic**: What is the main topic or condition? (e.g., STEMI, Stroke Protocol, Sepsis Management)
3. **Urgency Level**: How urgent is this information? (Critical/High/Medium/Low)
4. **Key Concepts**: List 3-5 key medical concepts, procedures, or guidelines shown
5. **Use Case**: When would this be referenced? (e.g., Emergency, Routine Care, Diagnosis, Treatment)
6. **Target Audience**: Who is this for? (e.g., ED Physician, ICU Nurse, General Practitioner)

Respond in JSON format:
{
    "specialty": "...",
    "topic": "...",
    "urgency": "...",
    "key_concepts": ["...", "..."],
    "use_case": "...",
    "target_audience": "...",
    "content_summary": "Brief 1-2 sentence summary of the infographic"
}

Be specific and medical-terminology accurate. If you're uncertain about any field, make your best assessment based on the image content."""

            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            response_text = message.content[0].text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)
            analysis['filename'] = image_path.name
            analysis['file_path'] = str(image_path)
            analysis['analyzed_at'] = datetime.now().isoformat()

            self.total_cost += self.COST_PER_IMAGE

            print(f"  ✓ Specialty: {analysis.get('specialty', 'N/A')}")
            print(f"  ✓ Topic: {analysis.get('topic', 'N/A')}")
            print(f"  ✓ Urgency: {analysis.get('urgency', 'N/A')}")

            return analysis

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {e}"
            print(f"  ✗ {error_msg}")
            self.errors.append({'file': image_path.name, 'error': error_msg})
            return None

        except Exception as e:
            error_msg = f"Error analyzing: {str(e)}"
            print(f"  ✗ {error_msg}")
            self.errors.append({'file': image_path.name, 'error': error_msg})
            return None

    def discover_categories(self, image_files: List[Path]) -> Dict:
        """Discover categories from images."""
        print("\n" + "=" * 70)
        print("PHASE 1: Discovering Categories from Medical Images")
        print("=" * 70)
        print(f"Images to analyze: {len(image_files)}")
        print(f"Estimated cost: ${len(image_files) * self.COST_PER_IMAGE:.2f}")
        print("")

        # Analyze each image
        for i, image_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}]", end=" ")
            result = self.analyze_image(image_path)
            if result:
                self.results.append(result)

        # Generate taxonomy
        print("\n\n🔍 Generating taxonomy from discovered categories...")

        specialties = set()
        urgency_levels = set()
        use_cases = set()
        audiences = set()
        key_concepts = set()

        for result in self.results:
            if 'specialty' in result:
                specialties.add(result['specialty'])
            if 'urgency' in result:
                urgency_levels.add(result['urgency'])
            if 'use_case' in result:
                use_cases.add(result['use_case'])
            if 'target_audience' in result:
                audiences.add(result['target_audience'])
            if 'key_concepts' in result:
                key_concepts.update(result['key_concepts'])

        taxonomy = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_images_analyzed': len(self.results),
                'total_errors': len(self.errors),
                'estimated_cost_usd': round(self.total_cost, 2)
            },
            'taxonomy': {
                'specialties': sorted(list(specialties)),
                'urgency_levels': sorted(list(urgency_levels)),
                'use_cases': sorted(list(use_cases)),
                'target_audiences': sorted(list(audiences)),
                'key_concepts': sorted(list(key_concepts))
            },
            'images': self.results,
            'errors': self.errors
        }

        print(f"\n📊 Taxonomy Summary:")
        print(f"  • Specialties: {len(specialties)}")
        print(f"  • Urgency Levels: {len(urgency_levels)}")
        print(f"  • Use Cases: {len(use_cases)}")
        print(f"  • Target Audiences: {len(audiences)}")
        print(f"  • Key Concepts: {len(key_concepts)}")
        print(f"  • Successfully Analyzed: {len(self.results)}")
        print(f"  • Errors: {len(self.errors)}")
        print(f"  • Total Cost: ${self.total_cost:.2f}")

        return taxonomy

    def generate_outputs(self, taxonomy: Dict):
        """Generate all output files."""
        print("\n" + "=" * 70)
        print("PHASE 2: Generating Output Files")
        print("=" * 70)

        images = taxonomy['images']
        if not images:
            print("⚠️  No images to process!")
            return

        # 1. Save taxonomy JSON
        taxonomy_path = self.output_dir / "taxonomy_discovery.json"
        with open(taxonomy_path, 'w') as f:
            json.dump(taxonomy, f, indent=2)
        print(f"\n✓ Saved: {taxonomy_path}")

        # 2. Generate Photos CSV
        csv_path = self.output_dir / "photos_import.csv"
        headers = ['Filename', 'Keywords', 'Title', 'Description', 'Specialty', 'Urgency']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for image in images:
                keywords = []
                if 'specialty' in image:
                    keywords.append(image['specialty'])
                if 'urgency' in image:
                    keywords.append(image['urgency'])
                if 'use_case' in image:
                    keywords.append(image['use_case'])
                if 'key_concepts' in image:
                    keywords.extend(image['key_concepts'])
                if 'target_audience' in image:
                    keywords.append(image['target_audience'])

                writer.writerow({
                    'Filename': image['filename'],
                    'Keywords': ', '.join(keywords),
                    'Title': image.get('topic', image['filename']),
                    'Description': image.get('content_summary', ''),
                    'Specialty': image.get('specialty', ''),
                    'Urgency': image.get('urgency', '')
                })

        print(f"✓ Saved: {csv_path} ({len(images)} images)")

        # 3. Generate keyword mapping
        keyword_to_images = defaultdict(list)
        for image in images:
            filename = image['filename']
            if 'specialty' in image:
                keyword_to_images[f"specialty:{image['specialty']}"].append(filename)
            if 'urgency' in image:
                keyword_to_images[f"urgency:{image['urgency']}"].append(filename)
            if 'use_case' in image:
                keyword_to_images[f"use_case:{image['use_case']}"].append(filename)
            if 'key_concepts' in image:
                for concept in image['key_concepts']:
                    keyword_to_images[f"concept:{concept}"].append(filename)
            if 'target_audience' in image:
                keyword_to_images[f"audience:{image['target_audience']}"].append(filename)

        mapping = {
            'generated_at': datetime.now().isoformat(),
            'total_keywords': len(keyword_to_images),
            'keywords': {k: sorted(v) for k, v in sorted(keyword_to_images.items())}
        }

        mapping_path = self.output_dir / "keyword_mapping.json"
        with open(mapping_path, 'w') as f:
            json.dump(mapping, f, indent=2)
        print(f"✓ Saved: {mapping_path} ({len(keyword_to_images)} keywords)")

        # 4. Generate quick reference markdown
        ref_path = self.output_dir / "quick_reference.md"
        with open(ref_path, 'w') as f:
            f.write("# Medical Image Quick Reference Guide\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Images: {len(images)}\n\n")

            # By Specialty
            f.write("## By Specialty\n\n")
            specialty_groups = defaultdict(list)
            for image in images:
                specialty = image.get('specialty', 'Uncategorized')
                specialty_groups[specialty].append(image)

            for specialty in sorted(specialty_groups.keys()):
                f.write(f"### {specialty} ({len(specialty_groups[specialty])} images)\n\n")
                for img in sorted(specialty_groups[specialty], key=lambda x: x['filename']):
                    f.write(f"- **{img['filename']}** - {img.get('topic', 'N/A')}\n")
                    if 'urgency' in img:
                        f.write(f"  - Urgency: {img['urgency']}\n")
                f.write("\n")

            # By Urgency
            f.write("## By Urgency Level\n\n")
            urgency_groups = defaultdict(list)
            for image in images:
                urgency = image.get('urgency', 'Unknown')
                urgency_groups[urgency].append(image)

            for urgency in ['Critical', 'High', 'Medium', 'Low']:
                if urgency in urgency_groups:
                    f.write(f"### {urgency} ({len(urgency_groups[urgency])} images)\n\n")
                    for img in sorted(urgency_groups[urgency], key=lambda x: x['filename']):
                        f.write(f"- **{img['filename']}** ({img.get('specialty', 'N/A')}) - {img.get('topic', 'N/A')}\n")
                    f.write("\n")

            # Complete list
            f.write("## Complete Image List\n\n")
            for img in sorted(images, key=lambda x: x['filename']):
                f.write(f"### {img['filename']}\n\n")
                f.write(f"- **Topic**: {img.get('topic', 'N/A')}\n")
                f.write(f"- **Specialty**: {img.get('specialty', 'N/A')}\n")
                f.write(f"- **Urgency**: {img.get('urgency', 'N/A')}\n")
                f.write(f"- **Use Case**: {img.get('use_case', 'N/A')}\n")
                if 'key_concepts' in img:
                    f.write(f"- **Key Concepts**: {', '.join(img['key_concepts'])}\n")
                if 'content_summary' in img:
                    f.write(f"- **Summary**: {img['content_summary']}\n")
                f.write("\n")

        print(f"✓ Saved: {ref_path}")

        # 5. Generate summary text
        summary_path = self.output_dir / "taxonomy_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("Medical Image Taxonomy Summary\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Images: {len(images)}\n")
            f.write(f"Total Cost: ${taxonomy['metadata']['estimated_cost_usd']:.2f}\n\n")

            tax = taxonomy['taxonomy']
            f.write(f"Specialties ({len(tax['specialties'])}):\n")
            for s in tax['specialties']:
                count = sum(1 for img in images if img.get('specialty') == s)
                f.write(f"  • {s} ({count} images)\n")

            f.write(f"\nUrgency Levels ({len(tax['urgency_levels'])}):\n")
            for u in tax['urgency_levels']:
                count = sum(1 for img in images if img.get('urgency') == u)
                f.write(f"  • {u} ({count} images)\n")

            f.write(f"\nUse Cases ({len(tax['use_cases'])}):\n")
            for uc in tax['use_cases']:
                count = sum(1 for img in images if img.get('use_case') == uc)
                f.write(f"  • {uc} ({count} images)\n")

        print(f"✓ Saved: {summary_path}")

    def run(self):
        """Run the complete organization process."""
        print("\n" + "=" * 70)
        print("Medical Image Organizer")
        print("=" * 70)
        print(f"Input: {self.input_dir}")
        print(f"Output: {self.output_dir}")

        # Get images
        try:
            image_files = self.get_image_files()
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return False

        if not image_files:
            print("\n⚠️  No images found!")
            print(f"Supported formats: {', '.join(sorted(self.SUPPORTED_FORMATS))}")
            return False

        # Phase 1: Discover
        taxonomy = self.discover_categories(image_files)

        # Phase 2: Generate outputs
        self.generate_outputs(taxonomy)

        # Final summary
        print("\n" + "=" * 70)
        print("✅ Complete!")
        print("=" * 70)
        print(f"\nGenerated files in: {self.output_dir}/")
        print("  • taxonomy_discovery.json  - Full analysis data")
        print("  • photos_import.csv        - Import to Photos app")
        print("  • keyword_mapping.json     - Keyword reference")
        print("  • quick_reference.md       - Human-readable guide")
        print("  • taxonomy_summary.txt     - Category overview")
        print(f"\nTotal cost: ${self.total_cost:.2f}")
        print("\nNext steps:")
        print(f"  1. Review: cat {self.output_dir}/taxonomy_summary.txt")
        print(f"  2. View guide: open {self.output_dir}/quick_reference.md")
        print(f"  3. Import to Photos: {self.output_dir}/photos_import.csv")

        return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Medical Image Organizer - AI-powered medical image categorization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable
  export ANTHROPIC_API_KEY='your-key'
  python %(prog)s ~/Photos/Medical

  # Using command line flag
  python %(prog)s /path/to/images --api-key YOUR_KEY

  # Custom output directory
  python %(prog)s ~/Photos/Medical -o ~/organized_output
        """
    )

    parser.add_argument(
        "input_dir",
        help="Directory containing medical images"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Output directory for results (default: output)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: API key required")
        print("\nProvide via:")
        print("  1. Environment: export ANTHROPIC_API_KEY='your-key'")
        print("  2. Command flag: --api-key YOUR_KEY")
        print("\nGet your key at: https://console.anthropic.com/")
        sys.exit(1)

    # Run organizer
    organizer = MedicalImageOrganizer(api_key, args.input_dir, args.output_dir)
    success = organizer.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
