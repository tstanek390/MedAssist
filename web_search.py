#!/usr/bin/env python3
"""
Mobile Web Search Interface for Medical Images
Provides a simple search interface accessible from iPhone/mobile devices.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Set
from flask import Flask, render_template_string, request, jsonify, send_file
import re

app = Flask(__name__)

# Global variables for data
TAXONOMY_DATA = None
IMAGE_DIR = None
OUTPUT_DIR = None


def load_taxonomy(taxonomy_path: str, image_dir: str):
    """Load taxonomy data and set image directory."""
    global TAXONOMY_DATA, IMAGE_DIR

    with open(taxonomy_path, 'r') as f:
        TAXONOMY_DATA = json.load(f)

    IMAGE_DIR = Path(image_dir).expanduser().resolve()
    print(f"✓ Loaded taxonomy with {len(TAXONOMY_DATA['images'])} images")
    print(f"✓ Image directory: {IMAGE_DIR}")


def search_images(query: str) -> List[Dict]:
    """
    Search for images matching the query.
    Searches across specialty, topic, urgency, key concepts, and use case.
    """
    if not TAXONOMY_DATA:
        return []

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    results = []
    query_terms = query_lower.split()

    for image in TAXONOMY_DATA['images']:
        score = 0
        match_details = []

        # Check specialty
        specialty = image.get('specialty', '').lower()
        if any(term in specialty for term in query_terms):
            score += 10
            match_details.append(f"Specialty: {image.get('specialty')}")

        # Check topic
        topic = image.get('topic', '').lower()
        if any(term in topic for term in query_terms):
            score += 15
            match_details.append(f"Topic: {image.get('topic')}")

        # Check urgency
        urgency = image.get('urgency', '').lower()
        if any(term in urgency for term in query_terms):
            score += 8
            match_details.append(f"Urgency: {image.get('urgency')}")

        # Check use case
        use_case = image.get('use_case', '').lower()
        if any(term in use_case for term in query_terms):
            score += 7
            match_details.append(f"Use Case: {image.get('use_case')}")

        # Check target audience
        audience = image.get('target_audience', '').lower()
        if any(term in audience for term in query_terms):
            score += 5
            match_details.append(f"Audience: {image.get('target_audience')}")

        # Check key concepts
        concepts = image.get('key_concepts', [])
        for concept in concepts:
            if any(term in concept.lower() for term in query_terms):
                score += 5
                match_details.append(f"Concept: {concept}")

        # Check content summary
        summary = image.get('content_summary', '').lower()
        if any(term in summary for term in query_terms):
            score += 3

        # Check filename
        filename = image.get('filename', '').lower()
        if any(term in filename for term in query_terms):
            score += 2

        if score > 0:
            result = image.copy()
            result['score'] = score
            result['match_details'] = match_details
            results.append(result)

    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)

    return results


# HTML template with mobile-responsive design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Medical Image Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f5f5f7;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .search-container {
            padding: 15px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .search-box {
            display: flex;
            gap: 10px;
        }

        #searchInput {
            flex: 1;
            padding: 12px 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.3s;
        }

        #searchInput:focus {
            border-color: #667eea;
        }

        #searchBtn {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }

        #searchBtn:active {
            background: #5568d3;
        }

        .quick-filters {
            display: flex;
            gap: 8px;
            padding: 10px 15px;
            overflow-x: auto;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
        }

        .quick-filter {
            padding: 8px 15px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            flex-shrink: 0;
        }

        .quick-filter:active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .results-info {
            padding: 15px;
            color: #666;
            font-size: 14px;
        }

        .results-container {
            padding: 0 15px 80px 15px;
        }

        .result-card {
            background: white;
            border-radius: 12px;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .result-image {
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
        }

        .result-content {
            padding: 15px;
        }

        .result-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        .result-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }

        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-critical {
            background: #fee;
            color: #c33;
        }

        .badge-high {
            background: #ffeaa7;
            color: #d63031;
        }

        .badge-medium {
            background: #dfe6e9;
            color: #2d3436;
        }

        .badge-low {
            background: #d1f2eb;
            color: #00b894;
        }

        .badge-specialty {
            background: #e3f2fd;
            color: #1976d2;
        }

        .result-summary {
            font-size: 14px;
            color: #666;
            line-height: 1.5;
            margin-bottom: 10px;
        }

        .result-matches {
            font-size: 13px;
            color: #888;
            border-top: 1px solid #f0f0f0;
            padding-top: 10px;
        }

        .result-matches strong {
            color: #667eea;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }

        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }

        .empty-state-text {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 10px;
        }

        .empty-state-hint {
            font-size: 14px;
            color: #bbb;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }

        .modal-content {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-image {
            max-width: 95%;
            max-height: 95%;
            object-fit: contain;
        }

        .modal-close {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 36px;
            font-weight: 300;
            cursor: pointer;
            z-index: 1001;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Medical Image Search</h1>
        <p>Quick bedside reference</p>
    </div>

    <div class="search-container">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search: cardiology, critical, STEMI..." autocomplete="off">
            <button id="searchBtn">Search</button>
        </div>
    </div>

    <div class="quick-filters">
        <div class="quick-filter" data-query="critical">🔴 Critical</div>
        <div class="quick-filter" data-query="emergency">⚡ Emergency</div>
        <div class="quick-filter" data-query="cardiology">❤️ Cardiology</div>
        <div class="quick-filter" data-query="neurology">🧠 Neurology</div>
        <div class="quick-filter" data-query="protocol">📋 Protocol</div>
        <div class="quick-filter" data-query="diagnosis">🔍 Diagnosis</div>
    </div>

    <div class="results-info" id="resultsInfo"></div>

    <div class="results-container" id="resultsContainer">
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-text">Search your medical images</div>
            <div class="empty-state-hint">Try "critical", "cardiology", or "STEMI"</div>
        </div>
    </div>

    <div class="modal" id="imageModal">
        <div class="modal-close" onclick="closeModal()">&times;</div>
        <div class="modal-content">
            <img class="modal-image" id="modalImage" src="" alt="">
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsInfo = document.getElementById('resultsInfo');
        const imageModal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');

        // Search function
        async function performSearch() {
            const query = searchInput.value.trim();
            if (!query) return;

            resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
            resultsInfo.innerHTML = '';

            try {
                const response = await fetch('/api/search?q=' + encodeURIComponent(query));
                const data = await response.json();

                if (data.results.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">😕</div>
                            <div class="empty-state-text">No results found</div>
                            <div class="empty-state-hint">Try different keywords</div>
                        </div>
                    `;
                    resultsInfo.innerHTML = '';
                } else {
                    resultsInfo.innerHTML = `Found ${data.results.length} image(s) for "${query}"`;
                    displayResults(data.results);
                }
            } catch (error) {
                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">⚠️</div>
                        <div class="empty-state-text">Error searching</div>
                        <div class="empty-state-hint">${error.message}</div>
                    </div>
                `;
            }
        }

        // Display results
        function displayResults(results) {
            resultsContainer.innerHTML = results.map(result => {
                const urgencyClass = `badge-${result.urgency.toLowerCase()}`;
                const matches = result.match_details.join(' • ');

                return `
                    <div class="result-card">
                        <img class="result-image"
                             src="/api/image/${encodeURIComponent(result.filename)}"
                             alt="${result.topic}"
                             onclick="showImage('${result.filename}')">
                        <div class="result-content">
                            <div class="result-title">${result.topic || result.filename}</div>
                            <div class="result-meta">
                                <span class="badge ${urgencyClass}">${result.urgency}</span>
                                <span class="badge badge-specialty">${result.specialty}</span>
                            </div>
                            <div class="result-summary">${result.content_summary || ''}</div>
                            <div class="result-matches">
                                <strong>Matches:</strong> ${matches}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Show full image
        function showImage(filename) {
            modalImage.src = '/api/image/' + encodeURIComponent(filename);
            imageModal.style.display = 'block';
        }

        // Close modal
        function closeModal() {
            imageModal.style.display = 'none';
        }

        // Event listeners
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') performSearch();
        });

        // Quick filters
        document.querySelectorAll('.quick-filter').forEach(filter => {
            filter.addEventListener('click', () => {
                searchInput.value = filter.dataset.query;
                performSearch();
            });
        });

        // Close modal on click outside
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) closeModal();
        });

        // Focus search on load
        window.addEventListener('load', () => {
            searchInput.focus();
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main search interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/search')
def api_search():
    """API endpoint for searching images."""
    query = request.args.get('q', '')
    results = search_images(query)
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })


@app.route('/api/image/<filename>')
def api_image(filename):
    """Serve image files."""
    image_path = IMAGE_DIR / filename

    if not image_path.exists():
        return jsonify({'error': 'Image not found'}), 404

    return send_file(image_path, mimetype=f'image/{image_path.suffix[1:]}')


def main():
    """Main entry point."""
    import argparse
    import socket

    parser = argparse.ArgumentParser(
        description="Mobile web search interface for medical images"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON (default: output/taxonomy_discovery.json)"
    )
    parser.add_argument(
        "-i", "--image-dir",
        required=True,
        help="Directory containing the original images"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5001,
        help="Port to run server on (default: 5001)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0 for network access)"
    )

    args = parser.parse_args()

    # Load taxonomy
    taxonomy_path = Path(args.taxonomy).expanduser().resolve()
    if not taxonomy_path.exists():
        print(f"❌ Error: Taxonomy file not found: {taxonomy_path}")
        print("\nRun the organizer first:")
        print("  python medical_image_organizer.py /path/to/images")
        return 1

    image_dir = Path(args.image_dir).expanduser().resolve()
    if not image_dir.exists():
        print(f"❌ Error: Image directory not found: {image_dir}")
        return 1

    load_taxonomy(str(taxonomy_path), str(image_dir))

    # Get local IP
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "localhost"

    print("\n" + "=" * 70)
    print("Medical Image Search Server")
    print("=" * 70)
    print(f"✓ Loaded {len(TAXONOMY_DATA['images'])} images")
    print(f"✓ Server starting on port {args.port}")
    print("\n📱 Access from your iPhone:")
    print(f"\n   http://{local_ip}:{args.port}")
    print(f"\n   (Make sure your iPhone is on the same WiFi network)")
    print("\n💻 Access from this computer:")
    print(f"\n   http://localhost:{args.port}")
    print("\n" + "=" * 70)
    print("\nPress Ctrl+C to stop the server")
    print()

    # Run server
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
