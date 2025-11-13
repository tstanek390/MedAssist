#!/usr/bin/env python3
"""
AI-Powered Clinical Query Interface for Medical Images
Understands complex clinical scenarios and matches them to relevant images.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Set
from flask import Flask, render_template_string, request, jsonify, send_file
import anthropic

app = Flask(__name__)

# Global variables
TAXONOMY_DATA = None
IMAGE_DIR = None
ANTHROPIC_CLIENT = None


def load_taxonomy(taxonomy_path: str, image_dir: str, api_key: str):
    """Load taxonomy data and initialize Claude client."""
    global TAXONOMY_DATA, IMAGE_DIR, ANTHROPIC_CLIENT

    with open(taxonomy_path, 'r') as f:
        TAXONOMY_DATA = json.load(f)

    IMAGE_DIR = Path(image_dir).expanduser().resolve()
    ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=api_key)

    print(f"✓ Loaded taxonomy with {len(TAXONOMY_DATA['images'])} images")
    print(f"✓ Image directory: {IMAGE_DIR}")
    print(f"✓ AI query system ready")


def ai_search_images(query: str) -> List[Dict]:
    """
    Use Claude AI to understand clinical query and find relevant images.
    """
    if not TAXONOMY_DATA or not ANTHROPIC_CLIENT:
        return []

    query = query.strip()
    if not query:
        return []

    try:
        # Build context about available images
        image_summaries = []
        for img in TAXONOMY_DATA['images']:
            summary = {
                'filename': img['filename'],
                'specialty': img.get('specialty', ''),
                'topic': img.get('topic', ''),
                'urgency': img.get('urgency', ''),
                'use_case': img.get('use_case', ''),
                'key_concepts': img.get('key_concepts', []),
                'summary': img.get('content_summary', '')
            }
            image_summaries.append(summary)

        # Create AI prompt
        prompt = f"""You are a clinical decision support AI helping a healthcare professional find relevant medical reference images.

The user has asked: "{query}"

Available medical reference images and their content:
{json.dumps(image_summaries, indent=2)}

Task:
1. Analyze the clinical scenario in the user's query
2. Identify the most relevant medical images that would help address their question
3. Rank them by relevance (most relevant first)
4. For each relevant image, explain WHY it's relevant to this clinical scenario

Return a JSON array of relevant images with this format:
[
  {{
    "filename": "...",
    "relevance_score": 95,  // 0-100, higher = more relevant
    "clinical_reasoning": "This image is relevant because...",
    "specific_sections": ["What specific parts of the image would help"]
  }},
  ...
]

Only include images that are actually relevant (relevance_score >= 40).
Limit to top 10 most relevant images.
If no images are relevant, return an empty array.

Be specific about HOW each image helps with the clinical scenario."""

        # Call Claude API
        message = ANTHROPIC_CLIENT.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        response_text = message.content[0].text

        # Parse JSON response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        ai_results = json.loads(response_text)

        # Merge with full image data
        results = []
        for ai_result in ai_results:
            filename = ai_result['filename']
            # Find full image data
            full_image = next((img for img in TAXONOMY_DATA['images']
                             if img['filename'] == filename), None)

            if full_image:
                result = full_image.copy()
                result['relevance_score'] = ai_result['relevance_score']
                result['clinical_reasoning'] = ai_result['clinical_reasoning']
                result['specific_sections'] = ai_result.get('specific_sections', [])
                results.append(result)

        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)

        return results

    except Exception as e:
        print(f"Error in AI search: {e}")
        # Fallback to keyword search
        return keyword_search_images(query)


def keyword_search_images(query: str) -> List[Dict]:
    """Fallback keyword search if AI search fails."""
    if not TAXONOMY_DATA:
        return []

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    results = []
    query_terms = query_lower.split()

    for image in TAXONOMY_DATA['images']:
        score = 0

        # Simple keyword matching
        specialty = image.get('specialty', '').lower()
        topic = image.get('topic', '').lower()
        urgency = image.get('urgency', '').lower()
        use_case = image.get('use_case', '').lower()
        summary = image.get('content_summary', '').lower()
        concepts = ' '.join(image.get('key_concepts', [])).lower()

        searchable = f"{specialty} {topic} {urgency} {use_case} {summary} {concepts}"

        for term in query_terms:
            if term in searchable:
                score += 1

        if score > 0:
            result = image.copy()
            result['relevance_score'] = score * 10
            result['clinical_reasoning'] = f"Keyword match ({score} terms matched)"
            results.append(result)

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:10]


# Enhanced HTML template with AI query interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Medical Image AI Search</title>
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
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .header .ai-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        .header p {
            font-size: 13px;
            opacity: 0.9;
            margin-top: 8px;
        }

        .search-container {
            padding: 15px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .search-box {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        #searchInput {
            width: 100%;
            padding: 12px 15px;
            font-size: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.3s;
            min-height: 60px;
            resize: vertical;
        }

        #searchInput:focus {
            border-color: #667eea;
        }

        #searchBtn {
            padding: 14px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }

        #searchBtn:active {
            transform: scale(0.98);
        }

        .example-queries {
            padding: 10px 15px;
            background: #f9f9f9;
            font-size: 12px;
            color: #666;
        }

        .example-queries strong {
            color: #333;
        }

        .example-query {
            background: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            border: 1px solid #e0e0e0;
        }

        .example-query:active {
            background: #f0f0f0;
        }

        .results-info {
            padding: 15px;
            color: #666;
            font-size: 14px;
        }

        .ai-processing {
            background: #e3f2fd;
            padding: 15px;
            margin: 15px;
            border-radius: 10px;
            border-left: 4px solid #2196f3;
            font-size: 14px;
            color: #1976d2;
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

        .relevance-bar {
            height: 4px;
            background: linear-gradient(90deg, #4caf50 0%, #8bc34a 50%, #cddc39 100%);
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

        .relevance-score {
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .clinical-reasoning {
            background: #f0f7ff;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 14px;
            line-height: 1.5;
            color: #1565c0;
            border-left: 3px solid #2196f3;
        }

        .clinical-reasoning strong {
            color: #0d47a1;
        }

        .result-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }

        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-critical { background: #fee; color: #c33; }
        .badge-high { background: #ffeaa7; color: #d63031; }
        .badge-medium { background: #dfe6e9; color: #2d3436; }
        .badge-low { background: #d1f2eb; color: #00b894; }
        .badge-specialty { background: #e3f2fd; color: #1976d2; }

        .specific-sections {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #f0f0f0;
            font-size: 13px;
        }

        .specific-sections strong {
            color: #667eea;
        }

        .specific-sections ul {
            margin: 5px 0 0 20px;
            color: #666;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }

        .empty-state-icon { font-size: 64px; margin-bottom: 20px; }
        .empty-state-text { font-size: 18px; font-weight: 500; margin-bottom: 10px; }
        .empty-state-hint { font-size: 14px; color: #bbb; }

        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }

        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
        <h1>🏥 Medical Image AI Search</h1>
        <div class="ai-badge">🤖 AI-Powered Clinical Query</div>
        <p>Describe your clinical scenario in natural language</p>
    </div>

    <div class="search-container">
        <div class="search-box">
            <textarea id="searchInput" placeholder="Describe your clinical scenario...

Example: 'Patient on postoperative day 3 after bowel surgery has fever and abdominal pain. What should I check?'"></textarea>
            <button id="searchBtn">🔍 Search with AI</button>
        </div>
    </div>

    <div class="example-queries">
        <strong>Try these examples:</strong>
        <div class="example-query" data-query="patient with chest pain and elevated troponin">
            💓 Chest pain + elevated troponin
        </div>
        <div class="example-query" data-query="postoperative fever day 3 after abdominal surgery">
            🌡️ Postoperative fever after surgery
        </div>
        <div class="example-query" data-query="stroke protocol for acute onset weakness">
            🧠 Acute stroke management
        </div>
    </div>

    <div class="results-info" id="resultsInfo"></div>

    <div class="results-container" id="resultsContainer">
        <div class="empty-state">
            <div class="empty-state-icon">🤖</div>
            <div class="empty-state-text">AI-Powered Clinical Search</div>
            <div class="empty-state-hint">Describe your clinical scenario above</div>
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

        async function performSearch() {
            const query = searchInput.value.trim();
            if (!query) return;

            resultsContainer.innerHTML = `
                <div class="ai-processing">
                    🤖 AI is analyzing your clinical scenario...
                    <div class="loading-spinner"></div>
                </div>
            `;
            resultsInfo.innerHTML = '';

            try {
                const response = await fetch('/api/ai-search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                if (data.results.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">🤔</div>
                            <div class="empty-state-text">No relevant images found</div>
                            <div class="empty-state-hint">Try rephrasing your query</div>
                        </div>
                    `;
                } else {
                    resultsInfo.innerHTML = `🎯 Found ${data.results.length} relevant image(s)`;
                    displayResults(data.results);
                }
            } catch (error) {
                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">⚠️</div>
                        <div class="empty-state-text">Error</div>
                        <div class="empty-state-hint">${error.message}</div>
                    </div>
                `;
            }
        }

        function displayResults(results) {
            resultsContainer.innerHTML = results.map(result => {
                const urgencyClass = `badge-${result.urgency.toLowerCase()}`;
                const relevancePercent = Math.min(100, result.relevance_score);

                let sectionsHTML = '';
                if (result.specific_sections && result.specific_sections.length > 0) {
                    sectionsHTML = `
                        <div class="specific-sections">
                            <strong>Pay attention to:</strong>
                            <ul>
                                ${result.specific_sections.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                return `
                    <div class="result-card">
                        <div class="relevance-bar" style="width: ${relevancePercent}%"></div>
                        <img class="result-image"
                             src="/api/image/${encodeURIComponent(result.filename)}"
                             alt="${result.topic}"
                             onclick="showImage('${result.filename}')">
                        <div class="result-content">
                            <div class="result-title">${result.topic || result.filename}</div>
                            <div class="relevance-score">Relevance: ${result.relevance_score}%</div>
                            <div class="result-meta">
                                <span class="badge ${urgencyClass}">${result.urgency}</span>
                                <span class="badge badge-specialty">${result.specialty}</span>
                            </div>
                            <div class="clinical-reasoning">
                                <strong>Why this is relevant:</strong><br>
                                ${result.clinical_reasoning}
                            </div>
                            ${sectionsHTML}
                        </div>
                    </div>
                `;
            }).join('');
        }

        function showImage(filename) {
            modalImage.src = '/api/image/' + encodeURIComponent(filename);
            imageModal.style.display = 'block';
        }

        function closeModal() {
            imageModal.style.display = 'none';
        }

        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) performSearch();
        });

        document.querySelectorAll('.example-query').forEach(ex => {
            ex.addEventListener('click', () => {
                searchInput.value = ex.dataset.query;
                performSearch();
            });
        });

        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) closeModal();
        });

        window.addEventListener('load', () => {
            searchInput.focus();
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main AI search interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/ai-search', methods=['POST'])
def api_ai_search():
    """API endpoint for AI-powered search."""
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        results = ai_search_images(query)
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        description="AI-powered clinical query interface for medical images"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON"
    )
    parser.add_argument(
        "-i", "--image-dir",
        required=True,
        help="Directory containing the original images"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5002,
        help="Port to run server on (default: 5002)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: API key required for AI search")
        print("\nProvide via:")
        print("  1. Environment: export ANTHROPIC_API_KEY='your-key'")
        print("  2. Command flag: --api-key YOUR_KEY")
        return 1

    # Load taxonomy
    taxonomy_path = Path(args.taxonomy).expanduser().resolve()
    if not taxonomy_path.exists():
        print(f"❌ Error: Taxonomy file not found: {taxonomy_path}")
        return 1

    image_dir = Path(args.image_dir).expanduser().resolve()
    if not image_dir.exists():
        print(f"❌ Error: Image directory not found: {image_dir}")
        return 1

    load_taxonomy(str(taxonomy_path), str(image_dir), api_key)

    # Get local IP
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "localhost"

    print("\n" + "=" * 70)
    print("Medical Image AI Search Server")
    print("=" * 70)
    print(f"✓ Loaded {len(TAXONOMY_DATA['images'])} images")
    print(f"✓ AI-powered clinical query enabled")
    print(f"✓ Server starting on port {args.port}")
    print("\n📱 Access from your iPhone:")
    print(f"\n   http://{local_ip}:{args.port}")
    print("\n💻 Access from this computer:")
    print(f"\n   http://localhost:{args.port}")
    print("\n" + "=" * 70)
    print("\nDescribe clinical scenarios in natural language!")
    print("Press Ctrl+C to stop")
    print()

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
