#!/usr/bin/env python3
"""
Phase 2: Apply Taxonomy to Medical Images
Uses discovered taxonomy to generate Photos app import files and reference guides.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict


class TaxonomyApplicator:
    """Applies discovered taxonomy to generate import files and reference guides."""

    def __init__(self, taxonomy_path: str, output_dir: str = "output"):
        """
        Initialize the applicator.

        Args:
            taxonomy_path: Path to taxonomy_discovery.json
            output_dir: Directory for output files
        """
        self.taxonomy_path = Path(taxonomy_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load taxonomy
        with open(self.taxonomy_path, 'r') as f:
            self.taxonomy_data = json.load(f)

        self.images = self.taxonomy_data.get('images', [])
        self.taxonomy = self.taxonomy_data.get('taxonomy', {})
        self.metadata = self.taxonomy_data.get('metadata', {})

    def generate_photos_csv(self) -> Path:
        """
        Generate CSV file for Photos app import with keywords.

        Returns:
            Path to generated CSV file
        """
        print("\n📸 Generating Photos app import CSV...")

        csv_path = self.output_dir / "photos_import.csv"

        # CSV headers for Photos app
        # Typical format: Filename, Keywords, Title, Description
        headers = ['Filename', 'Keywords', 'Title', 'Description', 'Specialty', 'Urgency']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for image in self.images:
                # Build keywords list
                keywords = []

                # Add specialty
                if 'specialty' in image:
                    keywords.append(image['specialty'])

                # Add urgency
                if 'urgency' in image:
                    keywords.append(image['urgency'])

                # Add use case
                if 'use_case' in image:
                    keywords.append(image['use_case'])

                # Add key concepts
                if 'key_concepts' in image:
                    keywords.extend(image['key_concepts'])

                # Add target audience
                if 'target_audience' in image:
                    keywords.append(image['target_audience'])

                # Write row
                writer.writerow({
                    'Filename': image['filename'],
                    'Keywords': ', '.join(keywords),
                    'Title': image.get('topic', image['filename']),
                    'Description': image.get('content_summary', ''),
                    'Specialty': image.get('specialty', ''),
                    'Urgency': image.get('urgency', '')
                })

        print(f"  ✓ Created: {csv_path}")
        print(f"  ✓ {len(self.images)} images with keywords")

        return csv_path

    def generate_keyword_mapping(self) -> Path:
        """
        Generate detailed keyword mapping reference.

        Returns:
            Path to generated JSON file
        """
        print("\n🏷️  Generating keyword mapping...")

        # Build reverse mapping: keyword -> images
        keyword_to_images = defaultdict(list)

        for image in self.images:
            filename = image['filename']

            # Map specialty
            if 'specialty' in image:
                keyword_to_images[f"specialty:{image['specialty']}"].append(filename)

            # Map urgency
            if 'urgency' in image:
                keyword_to_images[f"urgency:{image['urgency']}"].append(filename)

            # Map use case
            if 'use_case' in image:
                keyword_to_images[f"use_case:{image['use_case']}"].append(filename)

            # Map key concepts
            if 'key_concepts' in image:
                for concept in image['key_concepts']:
                    keyword_to_images[f"concept:{concept}"].append(filename)

            # Map target audience
            if 'target_audience' in image:
                keyword_to_images[f"audience:{image['target_audience']}"].append(filename)

        # Convert to regular dict and sort
        mapping = {
            'generated_at': datetime.now().isoformat(),
            'total_keywords': len(keyword_to_images),
            'keywords': {k: sorted(v) for k, v in sorted(keyword_to_images.items())}
        }

        mapping_path = self.output_dir / "keyword_mapping.json"
        with open(mapping_path, 'w') as f:
            json.dump(mapping, f, indent=2)

        print(f"  ✓ Created: {mapping_path}")
        print(f"  ✓ {len(keyword_to_images)} unique keywords")

        return mapping_path

    def generate_quick_reference(self) -> Path:
        """
        Generate human-readable quick reference guide.

        Returns:
            Path to generated markdown file
        """
        print("\n📋 Generating quick reference guide...")

        ref_path = self.output_dir / "quick_reference.md"

        with open(ref_path, 'w') as f:
            # Header
            f.write("# Medical Image Quick Reference Guide\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Images: {len(self.images)}\n\n")

            # Table of Contents
            f.write("## Table of Contents\n\n")
            f.write("- [By Specialty](#by-specialty)\n")
            f.write("- [By Urgency Level](#by-urgency-level)\n")
            f.write("- [By Use Case](#by-use-case)\n")
            f.write("- [By Target Audience](#by-target-audience)\n")
            f.write("- [Complete Image List](#complete-image-list)\n\n")

            f.write("---\n\n")

            # Group by specialty
            f.write("## By Specialty\n\n")
            specialty_groups = defaultdict(list)
            for image in self.images:
                specialty = image.get('specialty', 'Uncategorized')
                specialty_groups[specialty].append(image)

            for specialty in sorted(specialty_groups.keys()):
                f.write(f"### {specialty}\n\n")
                images = specialty_groups[specialty]
                for img in sorted(images, key=lambda x: x['filename']):
                    f.write(f"- **{img['filename']}** - {img.get('topic', 'N/A')}\n")
                    if 'urgency' in img:
                        f.write(f"  - Urgency: {img['urgency']}\n")
                    if 'content_summary' in img:
                        f.write(f"  - {img['content_summary']}\n")
                f.write("\n")

            # Group by urgency
            f.write("## By Urgency Level\n\n")
            urgency_groups = defaultdict(list)
            urgency_order = ['Critical', 'High', 'Medium', 'Low']

            for image in self.images:
                urgency = image.get('urgency', 'Unknown')
                urgency_groups[urgency].append(image)

            for urgency in urgency_order:
                if urgency in urgency_groups:
                    f.write(f"### {urgency}\n\n")
                    images = urgency_groups[urgency]
                    for img in sorted(images, key=lambda x: x['filename']):
                        f.write(f"- **{img['filename']}** ({img.get('specialty', 'N/A')}) - {img.get('topic', 'N/A')}\n")
                    f.write("\n")

            # Handle any urgency levels not in standard order
            for urgency in sorted(urgency_groups.keys()):
                if urgency not in urgency_order:
                    f.write(f"### {urgency}\n\n")
                    images = urgency_groups[urgency]
                    for img in sorted(images, key=lambda x: x['filename']):
                        f.write(f"- **{img['filename']}** ({img.get('specialty', 'N/A')}) - {img.get('topic', 'N/A')}\n")
                    f.write("\n")

            # Group by use case
            f.write("## By Use Case\n\n")
            usecase_groups = defaultdict(list)
            for image in self.images:
                use_case = image.get('use_case', 'General')
                usecase_groups[use_case].append(image)

            for use_case in sorted(usecase_groups.keys()):
                f.write(f"### {use_case}\n\n")
                images = usecase_groups[use_case]
                for img in sorted(images, key=lambda x: x['filename']):
                    f.write(f"- **{img['filename']}** - {img.get('topic', 'N/A')}\n")
                f.write("\n")

            # Group by target audience
            f.write("## By Target Audience\n\n")
            audience_groups = defaultdict(list)
            for image in self.images:
                audience = image.get('target_audience', 'General')
                audience_groups[audience].append(image)

            for audience in sorted(audience_groups.keys()):
                f.write(f"### {audience}\n\n")
                images = audience_groups[audience]
                for img in sorted(images, key=lambda x: x['filename']):
                    f.write(f"- **{img['filename']}** - {img.get('topic', 'N/A')}\n")
                f.write("\n")

            # Complete image list with full details
            f.write("## Complete Image List\n\n")
            for img in sorted(self.images, key=lambda x: x['filename']):
                f.write(f"### {img['filename']}\n\n")
                f.write(f"- **Topic**: {img.get('topic', 'N/A')}\n")
                f.write(f"- **Specialty**: {img.get('specialty', 'N/A')}\n")
                f.write(f"- **Urgency**: {img.get('urgency', 'N/A')}\n")
                f.write(f"- **Use Case**: {img.get('use_case', 'N/A')}\n")
                f.write(f"- **Target Audience**: {img.get('target_audience', 'N/A')}\n")

                if 'key_concepts' in img and img['key_concepts']:
                    f.write(f"- **Key Concepts**: {', '.join(img['key_concepts'])}\n")

                if 'content_summary' in img:
                    f.write(f"- **Summary**: {img['content_summary']}\n")

                f.write("\n")

        print(f"  ✓ Created: {ref_path}")

        return ref_path

    def generate_taxonomy_summary(self) -> Path:
        """
        Generate taxonomy summary for review.

        Returns:
            Path to generated text file
        """
        print("\n📊 Generating taxonomy summary...")

        summary_path = self.output_dir / "taxonomy_summary.txt"

        with open(summary_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Medical Image Taxonomy Summary\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Images Analyzed: {self.metadata.get('total_images_analyzed', 0)}\n")
            f.write(f"Estimated Cost: ${self.metadata.get('estimated_cost_usd', 0):.2f}\n\n")

            f.write("Discovered Categories:\n")
            f.write("-" * 60 + "\n\n")

            # Specialties
            specialties = self.taxonomy.get('specialties', [])
            f.write(f"SPECIALTIES ({len(specialties)}):\n")
            for specialty in specialties:
                count = sum(1 for img in self.images if img.get('specialty') == specialty)
                f.write(f"  • {specialty} ({count} images)\n")
            f.write("\n")

            # Urgency Levels
            urgency_levels = self.taxonomy.get('urgency_levels', [])
            f.write(f"URGENCY LEVELS ({len(urgency_levels)}):\n")
            for urgency in urgency_levels:
                count = sum(1 for img in self.images if img.get('urgency') == urgency)
                f.write(f"  • {urgency} ({count} images)\n")
            f.write("\n")

            # Use Cases
            use_cases = self.taxonomy.get('use_cases', [])
            f.write(f"USE CASES ({len(use_cases)}):\n")
            for use_case in use_cases:
                count = sum(1 for img in self.images if img.get('use_case') == use_case)
                f.write(f"  • {use_case} ({count} images)\n")
            f.write("\n")

            # Target Audiences
            audiences = self.taxonomy.get('target_audiences', [])
            f.write(f"TARGET AUDIENCES ({len(audiences)}):\n")
            for audience in audiences:
                count = sum(1 for img in self.images if img.get('target_audience') == audience)
                f.write(f"  • {audience} ({count} images)\n")
            f.write("\n")

            # Key Concepts (top 20)
            key_concepts = self.taxonomy.get('key_concepts', [])
            f.write(f"KEY CONCEPTS (showing top 20 of {len(key_concepts)}):\n")
            # Count occurrences
            concept_counts = defaultdict(int)
            for img in self.images:
                for concept in img.get('key_concepts', []):
                    concept_counts[concept] += 1

            # Sort by frequency
            sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
            for concept, count in sorted_concepts[:20]:
                f.write(f"  • {concept} ({count} images)\n")

            if len(sorted_concepts) > 20:
                f.write(f"  ... and {len(sorted_concepts) - 20} more\n")

        print(f"  ✓ Created: {summary_path}")

        return summary_path

    def run(self):
        """Run the taxonomy application process."""
        print("=" * 60)
        print("Apply Taxonomy - Phase 2")
        print("=" * 60)
        print(f"Taxonomy Source: {self.taxonomy_path}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Images to Process: {len(self.images)}")

        if not self.images:
            print("\n⚠️  No images found in taxonomy!")
            return

        # Generate all output files
        self.generate_photos_csv()
        self.generate_keyword_mapping()
        self.generate_quick_reference()
        self.generate_taxonomy_summary()

        print("\n✅ Phase 2 Complete!")
        print("\nGenerated Files:")
        print(f"  • {self.output_dir}/photos_import.csv - Import to Photos app")
        print(f"  • {self.output_dir}/keyword_mapping.json - Keyword reference")
        print(f"  • {self.output_dir}/quick_reference.md - Human-readable guide")
        print(f"  • {self.output_dir}/taxonomy_summary.txt - Category summary")

        print("\nNext Steps:")
        print("  1. Review quick_reference.md for organization overview")
        print("  2. Import photos_import.csv into your Photos app")
        print("  3. Use keyword_mapping.json for programmatic access")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Apply discovered taxonomy to generate import files and guides"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON file (default: output/taxonomy_discovery.json)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )

    args = parser.parse_args()

    # Check if taxonomy file exists
    if not Path(args.taxonomy).exists():
        print(f"Error: Taxonomy file not found: {args.taxonomy}")
        print("\nRun Phase 1 first: python src/discover_categories.py <image_dir>")
        return 1

    # Run applicator
    applicator = TaxonomyApplicator(args.taxonomy, args.output_dir)
    applicator.run()

    return 0


if __name__ == "__main__":
    exit(main())
