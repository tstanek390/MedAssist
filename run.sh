#!/bin/bash
#
# Simple wrapper script for Medical Image Organizer
# Usage: ./run.sh /path/to/images
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "Medical Image Organizer"
echo "======================================================================"
echo ""

# Check if directory argument provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No directory specified${NC}"
    echo ""
    echo "Usage: $0 /path/to/images"
    echo ""
    echo "Example:"
    echo "  $0 /Users/admin/Desktop/MedGraphics"
    echo ""
    exit 1
fi

IMAGE_DIR="$1"
OUTPUT_DIR="${2:-output}"

# Check if directory exists
if [ ! -d "$IMAGE_DIR" ]; then
    echo -e "${RED}Error: Directory does not exist: $IMAGE_DIR${NC}"
    exit 1
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    echo "Or get your key at: https://console.anthropic.com/"
    echo ""
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import anthropic, PIL" 2>/dev/null || {
    echo -e "${RED}Error: Missing dependencies${NC}"
    echo ""
    echo "Install with:"
    echo "  pip install anthropic pillow"
    echo ""
    exit 1
}

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Run the organizer
echo "Starting Medical Image Organizer..."
echo "Input: $IMAGE_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

python3 medical_image_organizer.py "$IMAGE_DIR" -o "$OUTPUT_DIR"

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}======================================================================"
    echo "Success! Results saved to: $OUTPUT_DIR/"
    echo -e "======================================================================${NC}"
    echo ""
    echo "View your results:"
    echo "  cat $OUTPUT_DIR/taxonomy_summary.txt"
    echo "  open $OUTPUT_DIR/quick_reference.md"
    echo ""
else
    echo ""
    echo -e "${RED}======================================================================"
    echo "Error occurred during processing"
    echo -e "======================================================================${NC}"
    echo ""
    exit 1
fi
