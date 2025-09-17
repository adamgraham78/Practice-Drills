#!/usr/bin/env python3
"""
Hockey Drills CSV to HTML Converter
Converts a CSV file of hockey drills into a searchable, filterable HTML page.
"""

import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Set

def parse_csv(csv_file: str) -> List[Dict]:
    """Parse the CSV file and extract drill information."""
    drills = []
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        
        for row in reader:
            if len(row) >= 5 and row[0].strip():  # Ensure we have enough columns and drill name
                drill_name = row[0].strip()
                theme = row[2].strip() if len(row) > 2 else ""
                sub_category = row[3].strip() if len(row) > 3 else ""
                link = row[4].strip() if len(row) > 4 else ""
                
                # Parse themes (comma-separated categories)
                themes = []
                if theme:
                    themes = [t.strip() for t in theme.split(',') if t.strip()]
                
                # Parse sub-categories (comma-separated categories)
                sub_categories = []
                if sub_category:
                    sub_categories = [t.strip() for t in sub_category.split(',') if t.strip()]
                
                # Create tags from themes and sub-categories
                tags = set()
                for t in themes:
                    tags.add(t)
                for t in sub_categories:
                    tags.add(t)
                
                drill = {
                    'name': drill_name,
                    'link': link,
                    'tags': sorted(list(tags)),
                    'theme': theme,
                    'sub_category': sub_category
                }
                drills.append(drill)
    
    return drills

def get_all_tags(drills: List[Dict]) -> List[str]:
    """Extract all unique tags from drills."""
    all_tags = set()
    for drill in drills:
        all_tags.update(drill['tags'])
    return sorted(list(all_tags))

def generate_html(drills: List[Dict], all_tags: List[str]) -> str:
    """Generate the HTML page with modern UI and search functionality."""
    
    html_template = f"""<!doctype html>
<html lang="en" data-theme="auto">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Hockey Drills Database</title>
    <style>
        /* ===== Design Tokens (Light) ===== */
        :root {{
            --bg: #0b0c0f;
            --app-bg: #ffffff;
            --text: #0f172a;
            --muted: #465065;
            --border: #e5e7eb;
            --elev-1: #ffffff;
            --elev-2: #f8fafc;
            --primary: #2563eb;
            --primary-ink: #ffffff;
            --ring: 0 0 0 3px rgba(37, 99, 235, .25);
            --success: #16a34a;
            --warning: #f59e0b;
            --danger: #dc2626;
            --radius: 14px;
            --shadow-sm: 0 1px 2px rgba(2,6,23,.08);
            --shadow-md: 0 6px 24px rgba(2,6,23,.08), 0 2px 6px rgba(2,6,23,.06);
            --shadow-lg: 0 24px 48px rgba(2,6,23,.10);
        }}

        /* ===== Design Tokens (Dark) ===== */
        .theme-dark {{
            --app-bg: #0b1220;
            --text: #e5edff;
            --muted: #9aa6c2;
            --border: #1e293b;
            --elev-1: #0e1628;
            --elev-2: #0b1324;
            --primary: #60a5fa;
            --primary-ink: #0b1220;
            --ring: 0 0 0 3px rgba(96, 165, 250, .25);
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
        }}

        /* ===== Base Reset ===== */
        *, *::before, *::after {{ box-sizing: border-box; }}
        html, body {{ height: 100%; }}
        body {{
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font: 15px/1.6 system-ui, -apple-system, Segoe UI, Roboto, Inter, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
        }}

        /* App frame */
        .app {{
            min-height: 100vh;
            background: radial-gradient(1200px 600px at 15% -10%, rgba(37,99,235,.10), transparent 60%),
                        radial-gradient(900px 600px at 110% -20%, rgba(16,185,129,.08), transparent 60%),
                        var(--app-bg);
        }}

        /* ===== Top Nav ===== */
        .topbar {{
            position: sticky; 
            top: 0; 
            z-index: 40;
            backdrop-filter: saturate(120%) blur(8px);
            background: color-mix(in srgb, var(--app-bg) 82%, transparent);
            border-bottom: 1px solid var(--border);
        }}
        
        .container {{ 
            max-width: 1100px; 
            margin: 0 auto; 
            padding: 14px 20px; 
        }}
        
        .row {{ 
            display: flex; 
            align-items: center; 
            gap: 12px; 
            justify-content: space-between; 
        }}
        
        .brand {{ 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            font-weight: 700; 
            letter-spacing: .2px; 
        }}
        
        .brand .dot {{ 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, var(--primary), #10b981); 
            box-shadow: 0 0 0 4px color-mix(in srgb, var(--primary) 25%, transparent); 
        }}

        /* ===== Buttons ===== */
        .btn {{ 
            appearance: none; 
            border: 1px solid var(--border); 
            background: var(--elev-1); 
            color: var(--text);
            padding: 10px 14px; 
            border-radius: calc(var(--radius) - 6px); 
            cursor: pointer; 
            box-shadow: var(--shadow-sm);
            transition: transform .08s ease, box-shadow .2s ease, background .2s ease, border-color .2s ease;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .btn:hover {{ 
            transform: translateY(-1px); 
            box-shadow: var(--shadow-md); 
        }}
        
        .btn:focus-visible {{ 
            outline: none; 
            box-shadow: var(--shadow-md), var(--ring); 
        }}
        
        .btn.primary {{ 
            background: var(--primary); 
            color: var(--primary-ink); 
            border-color: color-mix(in srgb, var(--primary) 20%, var(--border)); 
        }}
        
        .btn.ghost {{ 
            background: transparent; 
        }}
        
        .btn.danger {{
            background: var(--danger);
            color: white;
            border-color: var(--danger);
        }}

        /* ===== Cards ===== */
        .card {{ 
            background: var(--elev-1); 
            border: 1px solid var(--border); 
            border-radius: var(--radius); 
            box-shadow: var(--shadow-md); 
            overflow: hidden; 
        }}
        
        .card .head {{ 
            padding: 16px 18px; 
            border-bottom: 1px solid var(--border); 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            gap: 12px; 
        }}
        
        .card .body {{ 
            padding: 18px; 
        }}

        /* ===== Inputs ===== */
        .field {{ 
            display: grid; 
            gap: 6px; 
        }}
        
        label {{ 
            color: var(--muted); 
            font-size: 13px; 
            font-weight: 500;
        }}
        
        input, select, textarea {{
            width: 100%; 
            padding: 10px 12px; 
            border-radius: calc(var(--radius) - 8px);
            border: 1px solid var(--border); 
            background: var(--elev-2); 
            color: var(--text);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
            transition: border-color .2s ease, box-shadow .2s ease;
        }}
        
        input:focus, select:focus, textarea:focus {{ 
            outline: none; 
            box-shadow: var(--ring); 
            border-color: color-mix(in srgb, var(--primary) 40%, var(--border)); 
        }}

        /* ===== Badge ===== */
        .badge {{ 
            display: inline-flex; 
            align-items: center; 
            gap: 8px; 
            padding: 6px 10px; 
            border-radius: 999px; 
            border: 1px solid var(--border); 
            background: var(--elev-2); 
            font-size: 12px; 
        }}

        /* ===== Layout ===== */
        .main-content {{
            padding: 26px 20px;
        }}

        .hero {{
            padding: 32px 20px;
            text-align: center;
        }}

        .hero h1 {{
            font-size: clamp(28px, 3.5vw, 42px);
            margin: 0 0 12px;
            letter-spacing: -.02em;
            font-weight: 600;
        }}

        .hero p {{
            color: var(--muted);
            margin: 0 auto 22px;
            max-width: 60ch;
        }}

        .layout {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
            align-items: start;
        }}

        .sidebar {{
            position: sticky;
            top: 20px;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
        }}

        .sidebar .card {{
            margin-bottom: 0;
        }}

        .sidebar-section {{
            margin-bottom: 24px;
        }}

        .sidebar-section:last-child {{
            margin-bottom: 0;
        }}

        .tags-container {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .tag {{
            appearance: none;
            border: 1px solid var(--border);
            background: var(--elev-2);
            color: var(--text);
            padding: 8px 12px;
            border-radius: calc(var(--radius) - 8px);
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            text-align: left;
            width: 100%;
            transition: all 0.2s ease;
        }}

        .tag:hover {{
            background: var(--elev-1);
            transform: translateX(2px);
        }}

        .tag.active {{
            background: var(--primary);
            color: var(--primary-ink);
            border-color: var(--primary);
            transform: translateX(2px);
        }}

        .drill-grid {{
            display: flex;
            flex-direction: column;
        }}

        .drill-item {{
            padding: 18px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            transition: background 0.2s ease;
        }}

        .drill-item:last-child {{
            border-bottom: none;
        }}

        .drill-item:hover {{
            background: var(--elev-2);
        }}

        .drill-name {{
            font-size: 16px;
            font-weight: 600;
            flex-shrink: 0;
        }}

        .drill-name a {{
            color: var(--primary);
            text-decoration: none;
            transition: color 0.2s ease;
        }}

        .drill-name a:hover {{
            color: color-mix(in srgb, var(--primary) 80%, var(--text));
            text-decoration: underline;
        }}

        .drill-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            justify-content: flex-end;
            flex-shrink: 1;
        }}

        .drill-tag {{
            background: var(--primary);
            color: var(--primary-ink);
            padding: 4px 8px;
            border-radius: calc(var(--radius) - 8px);
            font-size: 11px;
            font-weight: 500;
        }}

        .stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 14px;
            color: var(--muted);
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: var(--muted);
        }}

        .no-results h3 {{
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: var(--text);
        }}

        /* Utility */
        .flex {{ 
            display: flex; 
            gap: 12px; 
            align-items: center; 
        }}
        
        .stack {{ 
            display: grid; 
            gap: 14px; 
        }}

        /* ===== Responsive ===== */
        @media (max-width: 1024px) {{
            .layout {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}

            .sidebar {{
                position: static;
                max-height: none;
                order: 2;
            }}

            .content {{
                order: 1;
            }}

            .tags-container {{
                flex-direction: row;
                flex-wrap: wrap;
                gap: 8px;
            }}

            .tag {{
                width: auto;
                flex: 0 0 auto;
            }}
        }}

        @media (max-width: 768px) {{
            .main-content {{
                padding: 20px 15px;
            }}

            .hero {{
                padding: 24px 15px;
            }}

            .drill-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}

            .drill-tags {{
                justify-content: flex-start;
                width: 100%;
            }}

            .stats {{
                flex-direction: column;
                gap: 8px;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="app">
        <!-- ===== Top Navigation ===== -->
        <header class="topbar">
            <div class="container">
                <div class="row">
                    <div class="brand">
                        <span class="dot" aria-hidden="true"></span>
                        <span>Hockey Drills</span>
                        <span class="badge">{len(drills)} drills</span>
                    </div>
                    <div class="flex">
                        <button class="btn ghost" id="themeToggle" aria-label="Toggle theme">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <path d="M12 3a9 9 0 1 0 9 9a7 7 0 0 1-9-9Z"/>
                            </svg>
                            Theme
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- ===== Hero Section ===== -->
        <section class="hero">
            <div class="container">
                <h1>Hockey Drills Database</h1>
                <p>Search and filter through {len(drills)} professional hockey drills with {len(all_tags)} categories</p>
            </div>
        </section>

        <!-- ===== Main Content ===== -->
        <section class="main-content">
            <div class="container">
                <div class="layout">
                    <!-- ===== Sidebar ===== -->
                    <aside class="sidebar">
                        <div class="card">
                            <div class="head">
                                <span>Filters</span>
                            </div>
                            <div class="body stack">
                                <div class="sidebar-section">
                                    <div class="field">
                                        <label for="searchBox">Search Drills</label>
                                        <input type="text" id="searchBox" placeholder="Search drills by name...">
                                    </div>
                                </div>
                                
                                <div class="sidebar-section">
                                    <label>Filter by Category</label>
                                    <div class="tags-container" id="tagsContainer">
                                        <!-- Tags will be populated by JavaScript -->
                                    </div>
                                </div>
                                
                                <button class="btn danger" onclick="clearAllFilters()">Clear All Filters</button>
                            </div>
                        </div>
                    </aside>

                    <!-- ===== Main Content ===== -->
                    <main class="content">
                        <div class="stats">
                            <span id="resultsCount">Showing {len(drills)} drills</span>
                            <span id="activeFilters">No filters active</span>
                        </div>

                        <div class="card">
                            <div class="drill-grid" id="drillGrid">
                                <!-- Drills will be populated by JavaScript -->
                            </div>
                        </div>

                        <div class="no-results" id="noResults" style="display: none;">
                            <h3>No drills found</h3>
                            <p>Try adjusting your search or removing some filters</p>
                        </div>
                    </main>
                </div>
            </div>
        </section>
    </div>

    <script>
        // Data
        const drills = {json.dumps(drills, indent=2)};
        const allTags = {json.dumps(all_tags, indent=2)};
        
        // State
        let activeFilters = new Set();
        let searchTerm = '';

        // DOM Elements
        const searchBox = document.getElementById('searchBox');
        const tagsContainer = document.getElementById('tagsContainer');
        const drillGrid = document.getElementById('drillGrid');
        const noResults = document.getElementById('noResults');
        const resultsCount = document.getElementById('resultsCount');
        const activeFiltersSpan = document.getElementById('activeFilters');

        // Initialize
        function init() {{
            renderTags();
            renderDrills();
            setupEventListeners();
        }}

        function setupEventListeners() {{
            searchBox.addEventListener('input', (e) => {{
                searchTerm = e.target.value.toLowerCase();
                renderDrills();
            }});
        }}

        function renderTags() {{
            tagsContainer.innerHTML = allTags.map(tag => 
                `<span class="tag" onclick="toggleFilter('${{tag}}')" data-tag="${{tag}}">${{tag}}</span>`
            ).join('');
        }}

        function toggleFilter(tag) {{
            if (activeFilters.has(tag)) {{
                activeFilters.delete(tag);
            }} else {{
                activeFilters.add(tag);
            }}
            updateTagStyles();
            renderDrills();
        }}

        function updateTagStyles() {{
            document.querySelectorAll('.tag').forEach(tagEl => {{
                const tag = tagEl.dataset.tag;
                if (activeFilters.has(tag)) {{
                    tagEl.classList.add('active');
                }} else {{
                    tagEl.classList.remove('active');
                }}
            }});
        }}

        function clearAllFilters() {{
            activeFilters.clear();
            searchTerm = '';
            searchBox.value = '';
            updateTagStyles();
            renderDrills();
        }}

        function renderDrills() {{
            const filteredDrills = drills.filter(drill => {{
                // Search filter
                const matchesSearch = !searchTerm || 
                    drill.name.toLowerCase().includes(searchTerm) ||
                    drill.tags.some(tag => tag.toLowerCase().includes(searchTerm));

                // Tag filters
                const matchesTags = activeFilters.size === 0 || 
                    [...activeFilters].every(filter => drill.tags.includes(filter));

                return matchesSearch && matchesTags;
            }});

            if (filteredDrills.length === 0) {{
                drillGrid.style.display = 'none';
                noResults.style.display = 'block';
            }} else {{
                drillGrid.style.display = 'block';
                noResults.style.display = 'none';
                
                drillGrid.innerHTML = filteredDrills.map(drill => `
                    <div class="drill-item">
                        <div class="drill-name">
                            ${{drill.link ? `<a href="${{drill.link}}" target="_blank">${{drill.name}}</a>` : drill.name}}
                        </div>
                        <div class="drill-tags">
                            ${{drill.tags.map(tag => `<span class="drill-tag">${{tag}}</span>`).join('')}}
                        </div>
                    </div>
                `).join('');
            }}

            updateStats(filteredDrills.length);
        }}

        function updateStats(count) {{
            resultsCount.textContent = `Showing ${{count}} drill${{count !== 1 ? 's' : ''}}`;
            
            if (activeFilters.size > 0) {{
                activeFiltersSpan.textContent = `${{activeFilters.size}} filter${{activeFilters.size !== 1 ? 's' : ''}} active: ${{[...activeFilters].join(', ')}}`;
            }} else {{
                activeFiltersSpan.textContent = 'No filters active';
            }}
        }}

        // Initialize the app
        init();

        // ===== Theme Logic: respects system, remembers choice, toggles on click =====
        (function () {{
            const root = document.documentElement;
            const pref = localStorage.getItem('theme') || 'auto';
            const mq = window.matchMedia('(prefers-color-scheme: dark)');

            function apply(theme) {{
                root.classList.toggle('theme-dark', theme === 'dark' || (theme === 'auto' && mq.matches));
                root.dataset.theme = theme;
            }}

            mq.addEventListener?.('change', () => apply(root.dataset.theme || 'auto'));

            apply(pref);
            document.getElementById('themeToggle').addEventListener('click', () => {{
                const order = ['auto','light','dark'];
                const next = order[(order.indexOf(root.dataset.theme || 'auto') + 1) % order.length];
                localStorage.setItem('theme', next); 
                apply(next);
                const label = next[0].toUpperCase() + next.slice(1);
                document.getElementById('themeToggle').lastChild.textContent = ' ' + label;
            }});
        }})();
    </script>
</body>
</html>"""

    return html_template

def main():
    """Main function to convert CSV to HTML."""
    csv_file = "2025-26 B Red Practice Plan - Drills.csv"
    output_file = "hockey_drills.html"
    
    # Check if CSV file exists
    if not Path(csv_file).exists():
        print(f"Error: CSV file '{csv_file}' not found!")
        return
    
    print(f"Reading drills from {csv_file}...")
    drills = parse_csv(csv_file)
    print(f"Found {len(drills)} drills")
    
    print("Extracting tags...")
    all_tags = get_all_tags(drills)
    print(f"Found {len(all_tags)} unique tags")
    
    print("Generating HTML...")
    html_content = generate_html(drills, all_tags)
    
    print(f"Writing HTML to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully created {output_file}")
    print(f"Processed {len(drills)} drills with {len(all_tags)} unique tags")
    print(f"Open {output_file} in your browser to view the searchable drill database")

if __name__ == "__main__":
    main()
