#!/usr/bin/env python3
"""
Generate Offline Mobile Search HTML
Creates a single HTML file with embedded data that works completely offline.
"""

import json
import base64
from pathlib import Path
from typing import Dict, List
import argparse


def encode_image_base64(image_path: Path) -> str:
    """Encode image to base64 data URI."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Determine MIME type
    ext = image_path.suffix.lower()
    mime_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_map.get(ext, 'image/jpeg')

    return f"data:{mime_type};base64,{image_data}"


def generate_offline_html(taxonomy_path: str, image_dir: str, output_path: str,
                         include_images: bool = True, max_images: int = None):
    """Generate a standalone offline HTML file."""

    print("🔧 Generating offline search HTML...")

    # Load taxonomy
    with open(taxonomy_path, 'r') as f:
        taxonomy_data = json.load(f)

    images = taxonomy_data['images']
    if max_images:
        images = images[:max_images]
        print(f"   Limiting to {max_images} images")

    print(f"   Processing {len(images)} images...")

    # Prepare image data
    image_dir_path = Path(image_dir).expanduser().resolve()

    if include_images:
        print("   Embedding images as base64...")
        for i, img in enumerate(images, 1):
            if i % 5 == 0:
                print(f"   Progress: {i}/{len(images)}")

            image_path = image_dir_path / img['filename']
            if image_path.exists():
                try:
                    img['image_data'] = encode_image_base64(image_path)
                except Exception as e:
                    print(f"   Warning: Could not embed {img['filename']}: {e}")
                    img['image_data'] = None
            else:
                print(f"   Warning: Image not found: {img['filename']}")
                img['image_data'] = None
    else:
        print("   Skipping image embedding (text-only mode)")
        for img in images:
            img['image_data'] = None

    # Generate HTML
    html_content = generate_html_template(images, taxonomy_data, include_images)

    # Write to file
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)

    print(f"\n✅ Generated: {output_file}")
    print(f"   File size: {file_size_mb:.1f} MB")
    print(f"   Images: {len(images)}")
    print(f"   Mode: {'Full (with images)' if include_images else 'Text-only'}")

    return output_file


def generate_html_template(images: List[Dict], taxonomy_data: Dict, include_images: bool) -> str:
    """Generate the HTML template with embedded data."""

    images_json = json.dumps(images, ensure_ascii=False)
    taxonomy_json = json.dumps(taxonomy_data.get('taxonomy', {}), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Medical Image Search - Offline</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f5f5f7;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }}

        .offline-badge {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: #4caf50;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 50;
        }}

        .header h1 {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .header p {{
            font-size: 13px;
            opacity: 0.9;
        }}

        .search-container {{
            padding: 15px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            position: sticky;
            top: 90px;
            z-index: 40;
        }}

        .search-box {{
            position: relative;
        }}

        #searchInput {{
            width: 100%;
            padding: 12px 45px 12px 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.3s;
        }}

        #searchInput:focus {{
            border-color: #667eea;
        }}

        .search-icon {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            color: #999;
        }}

        .clear-btn {{
            position: absolute;
            right: 45px;
            top: 50%;
            transform: translateY(-50%);
            background: #ddd;
            color: #666;
            border: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 16px;
            cursor: pointer;
            display: none;
        }}

        .clear-btn.visible {{
            display: block;
        }}

        .quick-filters {{
            display: flex;
            gap: 8px;
            padding: 10px 15px;
            overflow-x: auto;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
            background: white;
        }}

        .quick-filter {{
            padding: 8px 15px;
            background: #f0f0f0;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            flex-shrink: 0;
        }}

        .quick-filter.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .stats {{
            padding: 10px 15px;
            background: #f9f9f9;
            font-size: 13px;
            color: #666;
            text-align: center;
        }}

        .results-info {{
            padding: 15px;
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }}

        .results-container {{
            padding: 0 15px 80px 15px;
        }}

        .result-card {{
            background: white;
            border-radius: 12px;
            margin-bottom: 15px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .result-image {{
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
            background: #f0f0f0;
        }}

        .no-image {{
            width: 100%;
            height: 150px;
            background: linear-gradient(135deg, #e0e0e0 0%, #f0f0f0 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 48px;
        }}

        .result-content {{
            padding: 15px;
        }}

        .result-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}

        .result-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }}

        .badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        .badge-critical {{ background: #fee; color: #c33; }}
        .badge-high {{ background: #ffeaa7; color: #d63031; }}
        .badge-medium {{ background: #dfe6e9; color: #2d3436; }}
        .badge-low {{ background: #d1f2eb; color: #00b894; }}
        .badge-specialty {{ background: #e3f2fd; color: #1976d2; }}

        .result-summary {{
            font-size: 14px;
            color: #666;
            line-height: 1.5;
            margin-bottom: 10px;
        }}

        .result-concepts {{
            font-size: 13px;
            color: #888;
            border-top: 1px solid #f0f0f0;
            padding-top: 10px;
        }}

        .result-concepts strong {{
            color: #667eea;
        }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}

        .empty-state-icon {{ font-size: 64px; margin-bottom: 20px; }}
        .empty-state-text {{ font-size: 18px; font-weight: 500; margin-bottom: 10px; }}
        .empty-state-hint {{ font-size: 14px; color: #bbb; }}

        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }}

        .modal-content {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        .modal-image {{
            max-width: 95%;
            max-height: 90%;
            object-fit: contain;
        }}

        .modal-close {{
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 36px;
            font-weight: 300;
            cursor: pointer;
            z-index: 1001;
            background: rgba(0,0,0,0.5);
            width: 50px;
            height: 50px;
            border-radius: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .modal-info {{
            color: white;
            text-align: center;
            padding: 15px;
            max-width: 90%;
        }}

        .modal-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .modal-specialty {{
            font-size: 14px;
            opacity: 0.8;
        }}

        @media (prefers-color-scheme: dark) {{
            body {{ background: #1a1a1a; }}
            .search-container {{ background: #2a2a2a; }}
            #searchInput {{ background: #333; color: white; border-color: #444; }}
            .result-card {{ background: #2a2a2a; color: white; }}
            .result-title {{ color: white; }}
            .result-summary {{ color: #ccc; }}
            .stats {{ background: #2a2a2a; color: #aaa; }}
            .quick-filter {{ background: #333; color: white; border-color: #444; }}
        }}
    </style>
</head>
<body>
    <div class="offline-badge">📡 OFFLINE MODE</div>

    <div class="header">
        <h1>🏥 Medical Image Search</h1>
        <p>Offline • No Internet Required</p>
    </div>

    <div class="search-container">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search: cardiology, critical, STEMI..." autocomplete="off">
            <button class="clear-btn" id="clearBtn">&times;</button>
            <span class="search-icon">🔍</span>
        </div>
    </div>

    <div class="quick-filters" id="quickFilters"></div>

    <div class="stats" id="stats"></div>

    <div class="results-info" id="resultsInfo"></div>

    <div class="results-container" id="resultsContainer">
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-text">Search your medical images</div>
            <div class="empty-state-hint">Try "critical", "cardiology", or tap a filter above</div>
        </div>
    </div>

    <div class="modal" id="imageModal">
        <div class="modal-close" onclick="closeModal()">&times;</div>
        <div class="modal-content">
            <div class="modal-info" id="modalInfo"></div>
            <img class="modal-image" id="modalImage" src="" alt="">
        </div>
    </div>

    <script>
        // Embedded data
        const IMAGES = {images_json};
        const TAXONOMY = {taxonomy_json};
        const HAS_IMAGES = {str(include_images).lower()};

        // Initialize
        const searchInput = document.getElementById('searchInput');
        const clearBtn = document.getElementById('clearBtn');
        const quickFilters = document.getElementById('quickFilters');
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsInfo = document.getElementById('resultsInfo');
        const statsDiv = document.getElementById('stats');
        const imageModal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalInfo = document.getElementById('modalInfo');

        let currentQuery = '';

        // Initialize quick filters
        function initQuickFilters() {{
            const filters = [
                {{ label: '🔴 Critical', query: 'critical' }},
                {{ label: '⚡ Emergency', query: 'emergency' }},
                {{ label: '❤️ Cardiology', query: 'cardiology' }},
                {{ label: '🧠 Neurology', query: 'neurology' }},
                {{ label: '🫁 Respiratory', query: 'respiratory' }},
                {{ label: '📋 Protocol', query: 'protocol' }},
            ];

            quickFilters.innerHTML = filters.map(f =>
                `<div class="quick-filter" data-query="${{f.query}}">${{f.label}}</div>`
            ).join('');

            document.querySelectorAll('.quick-filter').forEach(filter => {{
                filter.addEventListener('click', () => {{
                    searchInput.value = filter.dataset.query;
                    performSearch();
                }});
            }});
        }}

        // Show stats
        function showStats() {{
            const specialties = [...new Set(IMAGES.map(i => i.specialty))].filter(Boolean);
            const urgencyLevels = [...new Set(IMAGES.map(i => i.urgency))].filter(Boolean);

            statsDiv.innerHTML = `
                📚 ${{IMAGES.length}} images •
                🏥 ${{specialties.length}} specialties •
                ⚠️ ${{urgencyLevels.length}} urgency levels
            `;
        }}

        // Search function
        function performSearch() {{
            const query = searchInput.value.trim().toLowerCase();
            currentQuery = query;

            clearBtn.classList.toggle('visible', query.length > 0);

            if (!query) {{
                showAllImages();
                return;
            }}

            const queryTerms = query.split(/\\s+/);
            const results = [];

            IMAGES.forEach(img => {{
                let score = 0;
                const searchable = [
                    img.specialty || '',
                    img.topic || '',
                    img.urgency || '',
                    img.use_case || '',
                    img.target_audience || '',
                    img.content_summary || '',
                    ...(img.key_concepts || [])
                ].join(' ').toLowerCase();

                queryTerms.forEach(term => {{
                    if (searchable.includes(term)) {{
                        score += 1;
                    }}
                }});

                if (score > 0) {{
                    results.push({{ ...img, score }});
                }}
            }});

            results.sort((a, b) => b.score - a.score);

            if (results.length === 0) {{
                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">😕</div>
                        <div class="empty-state-text">No results found</div>
                        <div class="empty-state-hint">Try different keywords</div>
                    </div>
                `;
                resultsInfo.textContent = '';
            }} else {{
                resultsInfo.textContent = `Found ${{results.length}} image(s) for "${{query}}"`;
                displayResults(results);
            }}
        }}

        // Show all images
        function showAllImages() {{
            resultsInfo.textContent = `Showing all ${{IMAGES.length}} images`;
            displayResults(IMAGES);
        }}

        // Display results
        function displayResults(results) {{
            resultsContainer.innerHTML = results.map((img, idx) => {{
                const urgencyClass = `badge-${{(img.urgency || 'medium').toLowerCase()}}`;
                const concepts = (img.key_concepts || []).slice(0, 5).join(', ');

                let imageHTML;
                if (HAS_IMAGES && img.image_data) {{
                    imageHTML = `<img class="result-image" src="${{img.image_data}}" alt="${{img.topic}}" onclick="showImage(${{idx}})">`;
                }} else {{
                    imageHTML = `<div class="no-image" onclick="showImage(${{idx}})">🖼️</div>`;
                }}

                return `
                    <div class="result-card">
                        ${{imageHTML}}
                        <div class="result-content">
                            <div class="result-title">${{img.topic || img.filename}}</div>
                            <div class="result-meta">
                                <span class="badge ${{urgencyClass}}">${{img.urgency || 'N/A'}}</span>
                                <span class="badge badge-specialty">${{img.specialty || 'General'}}</span>
                            </div>
                            ${{img.content_summary ? `<div class="result-summary">${{img.content_summary}}</div>` : ''}}
                            ${{concepts ? `<div class="result-concepts"><strong>Key concepts:</strong> ${{concepts}}</div>` : ''}}
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        // Show image in modal
        function showImage(idx) {{
            const results = currentQuery ?
                IMAGES.filter(img => {{
                    const searchable = [
                        img.specialty || '',
                        img.topic || '',
                        img.urgency || '',
                        ...(img.key_concepts || [])
                    ].join(' ').toLowerCase();
                    return currentQuery.split(/\\s+/).some(term => searchable.includes(term));
                }}) : IMAGES;

            const img = results[idx] || IMAGES[idx];

            if (HAS_IMAGES && img.image_data) {{
                modalImage.src = img.image_data;
                modalImage.style.display = 'block';
            }} else {{
                modalImage.style.display = 'none';
            }}

            modalInfo.innerHTML = `
                <div class="modal-title">${{img.topic || img.filename}}</div>
                <div class="modal-specialty">${{img.specialty || 'General'}} • ${{img.urgency || 'N/A'}}</div>
            `;

            imageModal.style.display = 'block';
        }}

        // Close modal
        function closeModal() {{
            imageModal.style.display = 'none';
        }}

        // Event listeners
        searchInput.addEventListener('input', () => {{
            clearBtn.classList.toggle('visible', searchInput.value.length > 0);
        }});

        searchInput.addEventListener('keyup', (e) => {{
            if (e.key === 'Enter') performSearch();
        }});

        clearBtn.addEventListener('click', () => {{
            searchInput.value = '';
            clearBtn.classList.remove('visible');
            showAllImages();
        }});

        imageModal.addEventListener('click', (e) => {{
            if (e.target === imageModal) closeModal();
        }});

        // Initialize
        initQuickFilters();
        showStats();
        showAllImages();

        // Focus search on load
        window.addEventListener('load', () => {{
            searchInput.focus();
        }});
    </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate offline mobile search HTML"
    )
    parser.add_argument(
        "-t", "--taxonomy",
        default="output/taxonomy_discovery.json",
        help="Path to taxonomy JSON"
    )
    parser.add_argument(
        "-i", "--image-dir",
        required=True,
        help="Directory containing images"
    )
    parser.add_argument(
        "-o", "--output",
        default="medical_search_offline.html",
        help="Output HTML file path"
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Generate text-only version (no embedded images, much smaller file)"
    )
    parser.add_argument(
        "--max-images",
        type=int,
        help="Limit number of images to include"
    )

    args = parser.parse_args()

    # Generate
    output_file = generate_offline_html(
        args.taxonomy,
        args.image_dir,
        args.output,
        include_images=not args.text_only,
        max_images=args.max_images
    )

    print("\n📱 How to use on iPhone:")
    print(f"  1. AirDrop {output_file.name} to your iPhone")
    print("  2. Open in Safari or Files app")
    print("  3. Tap Share → Add to Home Screen")
    print("  4. Works completely offline!")

    if not args.text_only:
        print("\n💡 Tip: For smaller file size, use --text-only flag")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
