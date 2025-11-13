#!/usr/bin/env python3
"""
Phase 1: Medical Image Category Discovery
Analyzes medical infographic images using Claude Vision API to discover natural categories.
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import anthropic
from PIL import Image


class MedicalImageDiscoverer:
    """Discovers categories from medical images using Claude Vision API."""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    COST_PER_IMAGE = 0.012  # Approximate cost in USD

    def __init__(self, api_key: str, input_dir: str, output_dir: str = "output"):
        """
        Initialize the discoverer.

        Args:
            api_key: Anthropic API key
            input_dir: Directory containing medical images
            output_dir: Directory for output files
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.results = []
        self.errors = []
        self.total_cost = 0.0

    def get_image_files(self) -> List[Path]:
        """Get all supported image files from input directory."""
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        images = []
        for file_path in sorted(self.input_dir.iterdir()):
            if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append(file_path)

        return images

    def encode_image(self, image_path: Path) -> tuple[str, str]:
        """
        Encode image to base64 and determine media type.

        Returns:
            Tuple of (base64_data, media_type)
        """
        # Get media type from extension
        ext = image_path.suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        return image_data, media_type

    def analyze_image(self, image_path: Path) -> Optional[Dict]:
        """
        Analyze a single image using Claude Vision API.

        Returns:
            Dictionary with analysis results or None if failed
        """
        print(f"\n📸 Analyzing: {image_path.name}")

        try:
            # Encode image
            image_data, media_type = self.encode_image(image_path)

            # Create the vision prompt
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

            # Call Claude API
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

            # Extract response text
            response_text = message.content[0].text

            # Try to parse JSON from response
            # Sometimes Claude wraps JSON in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            # Add metadata
            analysis['filename'] = image_path.name
            analysis['file_path'] = str(image_path)
            analysis['analyzed_at'] = datetime.now().isoformat()

            # Update cost tracking
            self.total_cost += self.COST_PER_IMAGE

            # Log results
            print(f"  ✓ Specialty: {analysis.get('specialty', 'N/A')}")
            print(f"  ✓ Topic: {analysis.get('topic', 'N/A')}")
            print(f"  ✓ Urgency: {analysis.get('urgency', 'N/A')}")
            print(f"  ✓ Key Concepts: {', '.join(analysis.get('key_concepts', []))[:60]}...")

            return analysis

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response for {image_path.name}: {e}"
            print(f"  ✗ {error_msg}")
            self.errors.append({'file': image_path.name, 'error': error_msg})
            return None

        except Exception as e:
            error_msg = f"Error analyzing {image_path.name}: {str(e)}"
            print(f"  ✗ {error_msg}")
            self.errors.append({'file': image_path.name, 'error': error_msg})
            return None

    def generate_taxonomy(self) -> Dict:
        """
        Generate taxonomy from discovered categories.

        Returns:
            Dictionary containing the discovered taxonomy
        """
        print("\n🔍 Generating taxonomy from discovered categories...")

        # Extract unique values
        specialties = set()
        topics = set()
        urgency_levels = set()
        key_concepts = set()
        use_cases = set()
        audiences = set()

        for result in self.results:
            if 'specialty' in result:
                specialties.add(result['specialty'])
            if 'topic' in result:
                topics.add(result['topic'])
            if 'urgency' in result:
                urgency_levels.add(result['urgency'])
            if 'key_concepts' in result:
                key_concepts.update(result['key_concepts'])
            if 'use_case' in result:
                use_cases.add(result['use_case'])
            if 'target_audience' in result:
                audiences.add(result['target_audience'])

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

        # Print summary
        print(f"\n📊 Taxonomy Summary:")
        print(f"  • Specialties: {len(specialties)}")
        print(f"  • Urgency Levels: {len(urgency_levels)}")
        print(f"  • Use Cases: {len(use_cases)}")
        print(f"  • Target Audiences: {len(audiences)}")
        print(f"  • Key Concepts: {len(key_concepts)}")
        print(f"  • Total Images: {len(self.results)}")
        print(f"  • Errors: {len(self.errors)}")
        print(f"  • Estimated Cost: ${self.total_cost:.2f}")

        return taxonomy

    def save_results(self, taxonomy: Dict, filename: str = "taxonomy_discovery.json"):
        """Save taxonomy to JSON file."""
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(taxonomy, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")
        return output_path

    def run(self) -> Dict:
        """
        Run the discovery process.

        Returns:
            Generated taxonomy dictionary
        """
        print("=" * 60)
        print("Medical Image Category Discovery - Phase 1")
        print("=" * 60)
        print(f"Input Directory: {self.input_dir}")
        print(f"Output Directory: {self.output_dir}")

        # Get image files
        image_files = self.get_image_files()
        print(f"\nFound {len(image_files)} images to analyze")

        if not image_files:
            print("⚠️  No images found!")
            return {}

        # Estimate cost
        estimated_cost = len(image_files) * self.COST_PER_IMAGE
        print(f"Estimated cost: ${estimated_cost:.2f}")
        print("\nStarting analysis...")

        # Analyze each image
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]", end=" ")
            result = self.analyze_image(image_path)
            if result:
                self.results.append(result)

        # Generate and save taxonomy
        taxonomy = self.generate_taxonomy()
        self.save_results(taxonomy)

        return taxonomy


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Discover categories from medical images using Claude Vision API"
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing medical images"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Output directory for results (default: output)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: API key required. Set ANTHROPIC_API_KEY env var or use -k flag")
        sys.exit(1)

    # Run discovery
    discoverer = MedicalImageDiscoverer(api_key, args.input_dir, args.output_dir)
    taxonomy = discoverer.run()

    if taxonomy:
        print("\n✅ Discovery complete!")
        print("\nNext steps:")
        print("  1. Review the taxonomy in output/taxonomy_discovery.json")
        print("  2. Run Phase 2 with: python src/apply_taxonomy.py")
    else:
        print("\n⚠️  Discovery completed with no results")
        sys.exit(1)


if __name__ == "__main__":
    main()
