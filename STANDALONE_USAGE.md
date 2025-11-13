# Standalone Script - Quick Usage Guide

The easiest way to run the Medical Image Organizer is with the standalone script.

## One-Time Setup

1. **Download the script to your Mac:**
   - Save `medical_image_organizer.py` to your local machine
   - Or clone this repository and use the file

2. **Install Python dependencies:**
   ```bash
   pip install anthropic pillow
   ```

That's it! No project structure needed.

## Run It!

### Option 1: With environment variable (recommended)
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics
```

### Option 2: With command line flag
```bash
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics --api-key 'sk-ant-api03-...'
```

### Option 3: With custom output directory
```bash
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics -o ~/Desktop/organized_output
```

## What Happens

The script runs both Phase 1 and Phase 2 automatically:

1. **Analyzes all images** in your directory using Claude Vision
2. **Discovers categories** naturally from your content
3. **Generates 5 output files**:
   - `taxonomy_discovery.json` - Full analysis data
   - `photos_import.csv` - Import to Photos app
   - `keyword_mapping.json` - Keyword reference
   - `quick_reference.md` - Human-readable guide
   - `taxonomy_summary.txt` - Category overview

## Example Run

```bash
# Your command
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics

# Output you'll see:
======================================================================
Medical Image Organizer
======================================================================
Input: /Users/admin/Desktop/MedGraphics
Output: output

======================================================================
PHASE 1: Discovering Categories from Medical Images
======================================================================
Images to analyze: 15
Estimated cost: $0.18

[1/15] 📸 Analyzing: cardiac_emergency.png
  ✓ Specialty: Cardiology
  ✓ Topic: STEMI Management
  ✓ Urgency: Critical

[2/15] 📸 Analyzing: stroke_protocol.png
  ✓ Specialty: Neurology
  ✓ Topic: Acute Stroke Protocol
  ✓ Urgency: Critical

... (continues for all images)

📊 Taxonomy Summary:
  • Specialties: 8
  • Urgency Levels: 4
  • Use Cases: 6
  • Target Audiences: 5
  • Key Concepts: 47
  • Successfully Analyzed: 15
  • Errors: 0
  • Total Cost: $0.18

======================================================================
PHASE 2: Generating Output Files
======================================================================

✓ Saved: output/taxonomy_discovery.json
✓ Saved: output/photos_import.csv (15 images)
✓ Saved: output/keyword_mapping.json (73 keywords)
✓ Saved: output/quick_reference.md
✓ Saved: output/taxonomy_summary.txt

======================================================================
✅ Complete!
======================================================================

Generated files in: output/
  • taxonomy_discovery.json  - Full analysis data
  • photos_import.csv        - Import to Photos app
  • keyword_mapping.json     - Keyword reference
  • quick_reference.md       - Human-readable guide
  • taxonomy_summary.txt     - Category overview

Total cost: $0.18

Next steps:
  1. Review: cat output/taxonomy_summary.txt
  2. View guide: open output/quick_reference.md
  3. Import to Photos: output/photos_import.csv
```

## View Your Results

```bash
# View the summary
cat output/taxonomy_summary.txt

# Open the quick reference guide
open output/quick_reference.md

# Or on Linux
xdg-open output/quick_reference.md

# Check the CSV for Photos
head output/photos_import.csv
```

## Supported Image Formats

- JPG / JPEG
- PNG
- GIF
- WebP

## Cost

Approximately **$0.012 per image**:
- 15 images = ~$0.18
- 50 images = ~$0.60
- 100 images = ~$1.20
- 250 images = ~$3.00
- 500 images = ~$6.00

## Troubleshooting

### "Directory does not exist"
Make sure the path is correct and use the full path:
```bash
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics
```

### "API key required"
Either:
1. Set environment variable: `export ANTHROPIC_API_KEY='your-key'`
2. Or use flag: `--api-key 'your-key'`

### "No images found"
- Check your directory has images
- Ensure images are in supported formats (jpg, png, gif, webp)
- Make sure you're pointing to the correct directory

### "Module not found"
Install missing dependencies:
```bash
pip install anthropic pillow
```

## Pro Tips

1. **Test first**: Try with a small subset of images (5-10) before processing hundreds
2. **Backup**: Keep your original images backed up
3. **Review results**: Check `taxonomy_summary.txt` to see what was discovered
4. **Multiple runs**: You can run it multiple times - it won't modify your original images

## Questions?

- Full documentation: See `README.md`
- Technical details: See `src/` directory for the full implementation
- Issues: Check error messages in the output for specifics

---

**Ready to organize your medical images?**

```bash
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics --api-key 'YOUR_KEY'
```
