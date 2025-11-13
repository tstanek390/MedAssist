#!/bin/bash
#
# Start the mobile web search interface
# Usage: ./start_web_search.sh /path/to/images
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "======================================================================"
echo "Medical Image Search - Mobile Web Interface"
echo "======================================================================"
echo ""

# Check if image directory argument provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No image directory specified${NC}"
    echo ""
    echo "Usage: $0 /path/to/images"
    echo ""
    echo "Example:"
    echo "  $0 /Users/admin/Desktop/MedGraphics"
    echo ""
    exit 1
fi

IMAGE_DIR="$1"
TAXONOMY_PATH="${2:-output/taxonomy_discovery.json}"
PORT="${3:-5001}"

# Check if image directory exists
if [ ! -d "$IMAGE_DIR" ]; then
    echo -e "${RED}Error: Directory does not exist: $IMAGE_DIR${NC}"
    exit 1
fi

# Check if taxonomy exists
if [ ! -f "$TAXONOMY_PATH" ]; then
    echo -e "${RED}Error: Taxonomy file not found: $TAXONOMY_PATH${NC}"
    echo ""
    echo "Run the organizer first:"
    echo "  python medical_image_organizer.py $IMAGE_DIR"
    echo ""
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null || {
    echo -e "${YELLOW}Installing Flask...${NC}"
    pip install flask
}

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Start the web server
echo "Starting web server..."
echo ""
python3 web_search.py -i "$IMAGE_DIR" -t "$TAXONOMY_PATH" -p "$PORT"
