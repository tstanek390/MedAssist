#!/usr/bin/env python3
"""
Basic tests for Medical Image Organizer.
These are integration tests that require actual images and API key.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from discover_categories import MedicalImageDiscoverer
from apply_taxonomy import TaxonomyApplicator


def test_discovery_initialization():
    """Test that MedicalImageDiscoverer can be initialized."""
    try:
        # This will fail without API key, but tests the import
        api_key = os.getenv('ANTHROPIC_API_KEY', 'test-key')
        discoverer = MedicalImageDiscoverer(
            api_key=api_key,
            input_dir="/tmp/test",
            output_dir="/tmp/output"
        )
        print("✓ MedicalImageDiscoverer initialization works")
        return True
    except Exception as e:
        print(f"✗ MedicalImageDiscoverer initialization failed: {e}")
        return False


def test_applicator_initialization():
    """Test that TaxonomyApplicator can be initialized."""
    try:
        # Create a dummy taxonomy file
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            dummy_taxonomy = {
                'metadata': {'total_images_analyzed': 0},
                'taxonomy': {'specialties': [], 'urgency_levels': []},
                'images': []
            }
            json.dump(dummy_taxonomy, f)
            temp_path = f.name

        applicator = TaxonomyApplicator(
            taxonomy_path=temp_path,
            output_dir="/tmp/output"
        )

        # Clean up
        os.unlink(temp_path)

        print("✓ TaxonomyApplicator initialization works")
        return True
    except Exception as e:
        print(f"✗ TaxonomyApplicator initialization failed: {e}")
        return False


def test_supported_formats():
    """Test that supported formats are correctly defined."""
    expected_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    actual_formats = MedicalImageDiscoverer.SUPPORTED_FORMATS

    if expected_formats == actual_formats:
        print("✓ Supported formats are correct")
        return True
    else:
        print(f"✗ Supported formats mismatch: {actual_formats}")
        return False


def run_all_tests():
    """Run all basic tests."""
    print("=" * 60)
    print("Running Basic Tests")
    print("=" * 60)

    tests = [
        test_discovery_initialization,
        test_applicator_initialization,
        test_supported_formats,
    ]

    results = []
    for test in tests:
        print(f"\nRunning: {test.__name__}")
        result = test()
        results.append(result)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
