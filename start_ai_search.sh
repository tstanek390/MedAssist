#!/bin/bash
#
# Start the AI-powered clinical query interface
# Usage: ./start_ai_search.sh /path/to/images
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "======================================================================"
echo "Medical Image AI Search - Clinical Query Interface"
echo "======================================================================"
echo ""

if [ -z "$1" ]; then
    echo -e "${RED}Error: No image directory specified${NC}"
    echo ""
    echo "Usage: $0 /path/to/images"
    echo ""
    exit 1
fi

IMAGE_DIR="$1"
TAXONOMY_PATH="${2:-output/taxonomy_discovery.json}"
PORT="${3:-5002}"

if [ ! -d "$IMAGE_DIR" ]; then
    echo -e "${RED}Error: Directory does not exist: $IMAGE_DIR${NC}"
    exit 1
fi

if [ ! -f "$TAXONOMY_PATH" ]; then
    echo -e "${RED}Error: Taxonomy file not found: $TAXONOMY_PATH${NC}"
    echo ""
    echo "Run the organizer first:"
    echo "  python medical_image_organizer.py $IMAGE_DIR"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

echo "Checking dependencies..."
python3 -c "import flask, anthropic" 2>/dev/null || {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install flask anthropic
}

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""
echo "Starting AI-powered search server..."
echo ""
python3 web_search_ai.py -i "$IMAGE_DIR" -t "$TAXONOMY_PATH" -p "$PORT"
