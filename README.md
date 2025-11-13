# Medical Image Organizer

A two-phase AI-powered system for organizing medical infographic images using Claude Vision API. Automatically discovers natural categories from your medical image collection and generates structured taxonomies for easy bedside reference.

## Overview

This tool helps healthcare professionals organize 100-500+ medical infographic images by:
- **Phase 1**: Analyzing images to discover natural categories (specialty, urgency, topics, key concepts)
- **Phase 2**: Applying the taxonomy to generate Photos app import files and quick reference guides

## Features

- 🤖 **AI-Powered Analysis**: Uses Claude Sonnet 4.5 Vision API for intelligent image understanding
- 📊 **Natural Taxonomy Discovery**: No predefined categories - discovers organization from actual content
- 📸 **Photos App Integration**: Generates CSV files for easy import with keywords
- 🏥 **Medical Context Aware**: Extracts specialty, urgency, use cases, and key concepts
- 💰 **Cost Tracking**: Monitors API usage (~$0.012 per image)
- 📋 **Multiple Output Formats**: JSON, CSV, Markdown reference guides
- ⚡ **Progress Logging**: Real-time feedback during analysis
- 🛡️ **Error Handling**: Robust handling of API failures and edge cases

## Prerequisites

- Python 3.12 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Medical images in supported formats: JPG, PNG, GIF, WebP

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set your API key:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or pass it via command line flag `-k` when running the scripts.

## Project Structure

```
medical-image-organizer/
├── src/
│   ├── discover_categories.py  # Phase 1: Discover taxonomy
│   └── apply_taxonomy.py       # Phase 2: Generate output files
├── tests/
├── output/                     # Generated files (created automatically)
├── requirements.txt
└── README.md
```

## Usage

### Phase 1: Discover Categories

Analyze your medical images and discover natural categories:

```bash
python src/discover_categories.py ~/Photos/Medical
```

**Options:**
- `-o, --output-dir`: Specify output directory (default: `output`)
- `-k, --api-key`: Provide API key directly (alternative to env var)

**Example with options:**
```bash
python src/discover_categories.py /mnt/user-data/uploads -o results -k sk-ant-...
```

**What it does:**
1. Scans all images in the specified directory
2. Analyzes each image using Claude Vision API
3. Extracts:
   - Medical specialty (Cardiology, Neurology, etc.)
   - Topic/condition (STEMI, Stroke Protocol, etc.)
   - Urgency level (Critical, High, Medium, Low)
   - Key concepts and procedures
   - Use case (Emergency, Routine Care, etc.)
   - Target audience (ED Physician, ICU Nurse, etc.)
4. Generates `output/taxonomy_discovery.json` with all findings

**Output:**
```
📸 Analyzing: cardiac_emergency.png
  ✓ Specialty: Cardiology
  ✓ Topic: STEMI Management
  ✓ Urgency: Critical
  ✓ Key Concepts: ECG Interpretation, Time to Intervention, Door...

📊 Taxonomy Summary:
  • Specialties: 8
  • Urgency Levels: 4
  • Use Cases: 6
  • Target Audiences: 5
  • Key Concepts: 47
  • Total Images: 9
  • Estimated Cost: $0.11
```

### Phase 2: Apply Taxonomy

Use the discovered taxonomy to generate import files and reference guides:

```bash
python src/apply_taxonomy.py
```

**Options:**
- `-t, --taxonomy`: Path to taxonomy JSON (default: `output/taxonomy_discovery.json`)
- `-o, --output-dir`: Output directory (default: `output`)

**Example:**
```bash
python src/apply_taxonomy.py -t results/taxonomy_discovery.json -o final_output
```

**What it does:**
1. Loads the discovered taxonomy from Phase 1
2. Generates multiple output files:
   - `photos_import.csv` - CSV for Photos app with keywords
   - `keyword_mapping.json` - Reverse mapping of keywords to images
   - `quick_reference.md` - Human-readable guide organized by category
   - `taxonomy_summary.txt` - Overview of discovered categories

**Generated Files:**

#### photos_import.csv
For importing into Photos app with automatic keyword tagging:
```csv
Filename,Keywords,Title,Description,Specialty,Urgency
stemi.png,"Cardiology,Critical,ECG,...",STEMI Management,ECG interpretation...,Cardiology,Critical
```

#### quick_reference.md
Organized reference guide with:
- Images grouped by specialty
- Images grouped by urgency level
- Images grouped by use case
- Images grouped by target audience
- Complete detailed listing

#### keyword_mapping.json
Programmatic access to taxonomy:
```json
{
  "keywords": {
    "specialty:Cardiology": ["stemi.png", "chf.png"],
    "urgency:Critical": ["stemi.png", "stroke.png"],
    "concept:ECG Interpretation": ["stemi.png", "arrythmia.png"]
  }
}
```

## Workflow Example

**Complete workflow for organizing 200 medical images:**

```bash
# Step 1: Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Step 2: Run Phase 1 - Discovery (~$2.40 for 200 images)
python src/discover_categories.py ~/Photos/Medical

# Step 3: Review discovered categories
cat output/taxonomy_summary.txt

# Step 4: Run Phase 2 - Generate outputs
python src/apply_taxonomy.py

# Step 5: Review quick reference
open output/quick_reference.md

# Step 6: Import to Photos app
# Import photos_import.csv using your Photos app's CSV import feature
```

## Cost Estimation

- **Approximate cost**: $0.012 per image
- **100 images**: ~$1.20
- **250 images**: ~$3.00
- **500 images**: ~$6.00

Actual costs may vary based on image size and complexity.

## Testing

Test with sample images before processing your full collection:

```bash
# Test directory with 9 sample images
python src/discover_categories.py /mnt/user-data/uploads

# Expected cost for 9 images: ~$0.11
```

## Input Requirements

- **Supported formats**: JPG, JPEG, PNG, GIF, WebP
- **Image content**: Medical infographics, charts, protocols, guidelines
- **Directory structure**: Flat directory (subdirectories not currently supported)
- **File naming**: Any naming convention works

## Output Files Reference

| File | Purpose | Format |
|------|---------|--------|
| `taxonomy_discovery.json` | Complete analysis data | JSON |
| `photos_import.csv` | Photos app import | CSV |
| `keyword_mapping.json` | Keyword-to-image mapping | JSON |
| `quick_reference.md` | Human-readable guide | Markdown |
| `taxonomy_summary.txt` | Category overview | Text |

## Tips for Best Results

1. **Image Quality**: Higher quality infographics yield better analysis
2. **Medical Context**: Images with clear medical content work best
3. **Batch Processing**: Process all images at once for consistent taxonomy
4. **Review Phase 1**: Check `taxonomy_summary.txt` before running Phase 2
5. **Backup**: Keep original images backed up before importing to Photos app

## Troubleshooting

### API Key Issues
```
Error: API key required
```
**Solution**: Set `ANTHROPIC_API_KEY` environment variable or use `-k` flag

### No Images Found
```
⚠️  No images found!
```
**Solution**: Check directory path and ensure images are in supported formats

### JSON Parse Errors
```
Failed to parse JSON response
```
**Solution**: Individual image failures are logged but won't stop processing. Check `errors` array in output JSON.

### Permission Errors
```
Permission denied: /path/to/images
```
**Solution**: Ensure you have read access to image directory and write access to output directory

## Advanced Usage

### Custom Output Directory
```bash
python src/discover_categories.py ~/Images -o ~/Results/medical
```

### Re-apply Taxonomy
If you want to regenerate output files without re-analyzing images:
```bash
python src/apply_taxonomy.py -t output/taxonomy_discovery.json
```

### Process Multiple Collections
Process different collections separately to maintain distinct taxonomies:
```bash
# Emergency images
python src/discover_categories.py ~/Photos/Emergency -o output/emergency

# ICU images
python src/discover_categories.py ~/Photos/ICU -o output/icu
```

## Technical Details

- **Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- **Max Tokens**: 1024 per image analysis
- **Timeout**: None (processes sequentially with error handling)
- **Image Encoding**: Base64 encoding for API transmission
- **Retry Logic**: No automatic retries (manual rerun for failures)

## Future Enhancements

Potential additions (not yet implemented):
- Recursive directory scanning
- Batch size optimization
- Custom taxonomy templates
- Integration with other photo management tools
- Web-based UI
- Automatic retry logic for API failures

## License

MIT License - feel free to modify and use for your needs.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the output logs for specific error messages
3. Ensure your API key has sufficient credits
4. Verify image files are not corrupted

## Acknowledgments

Powered by Anthropic's Claude AI with Vision capabilities.

---

**Ready to organize your medical images?** Start with Phase 1!

```bash
python src/discover_categories.py ~/Photos/Medical
```
