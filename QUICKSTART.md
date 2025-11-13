# Quick Start Guide

Get started with the Medical Image Organizer in 5 minutes!

## Setup (One-time)

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set your Anthropic API key:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Quick Test with 9 Sample Images

If you have test images in `/mnt/user-data/uploads`:

```bash
# Phase 1: Discover categories (~$0.11 for 9 images)
python src/discover_categories.py /mnt/user-data/uploads

# Phase 2: Generate reference files
python src/apply_taxonomy.py
```

## Process Your Medical Images

```bash
# Replace with your actual photo directory
python src/discover_categories.py ~/Photos/Medical

# Generate output files
python src/apply_taxonomy.py
```

## View Results

```bash
# View discovered categories
cat output/taxonomy_summary.txt

# Open quick reference guide
cat output/quick_reference.md

# Check Photos import file
head output/photos_import.csv
```

## What Gets Created

After running both phases, you'll have:

```
output/
├── taxonomy_discovery.json    # Full analysis data
├── photos_import.csv          # Import to Photos app
├── keyword_mapping.json       # Keyword reference
├── quick_reference.md         # Human-readable guide
└── taxonomy_summary.txt       # Category overview
```

## Next Steps

1. Review `quick_reference.md` to see how your images are organized
2. Import `photos_import.csv` to your Photos app
3. Use keywords to quickly find images (e.g., search "Critical" or "Cardiology")

## Cost Estimate

- 9 test images: ~$0.11
- 100 images: ~$1.20
- 250 images: ~$3.00
- 500 images: ~$6.00

## Troubleshooting

**No images found:**
- Check your directory path
- Ensure images are: .jpg, .png, .gif, or .webp

**API key error:**
- Verify your key is set: `echo $ANTHROPIC_API_KEY`
- Make sure key starts with `sk-ant-`

**Need help?**
- See full documentation in `README.md`
- Check image analysis logs for specific errors

---

**Ready to go?** Run Phase 1:
```bash
python src/discover_categories.py /path/to/your/images
```
