import pandas as pd
import markdown
import math
from typing import Dict
from datetime import datetime


class HTMLRenderer:
    def __init__(self, df: pd.DataFrame, markdown_dict: Dict[str, str]):
        self.df = df
        self.markdown_dict = markdown_dict

    def save_to_file(self, output_path: str) -> None:
        html_content = self._generate_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html(self) -> str:
        stats = self._calculate_stats()
        grille_pattern = self._generate_grille_pattern()
        stats_section = self._generate_stats_section(stats)
        table_html = self._generate_table_html()
        tabs_html = self._generate_tabs_html()
        content_html = self._generate_content_html(stats_section, table_html)
        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        template = self._get_html_template()
        return template.replace('{grille_pattern}', grille_pattern) \
                       .replace('{tabs_html}', tabs_html) \
                       .replace('{content_html}', content_html) \
                       .replace('{generated_time}', generated_time)

    def _calculate_stats(self) -> dict:
        cluster_count = len(self.df)
        cell_type_count = self.df.iloc[:, 1].nunique() if len(self.df.columns) > 1 else 0
        cell_subtype_count = self.df.iloc[:, 2].nunique() if len(self.df.columns) > 2 else 0
        return {
            'cluster_count': cluster_count,
            'cell_type_count': cell_type_count,
            'cell_subtype_count': cell_subtype_count
        }

    def _generate_stats_section(self, stats: dict) -> str:
        return '''
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon stat-icon-1">📊</div>
                <div class="stat-content">
                    <div class="stat-value">{cluster_count}</div>
                    <div class="stat-label">Cluster 数量</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon stat-icon-2">🧬</div>
                <div class="stat-content">
                    <div class="stat-value">{cell_type_count}</div>
                    <div class="stat-label">细胞大类数量</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon stat-icon-3">🔬</div>
                <div class="stat-content">
                    <div class="stat-value">{cell_subtype_count}</div>
                    <div class="stat-label">细胞亚型数量</div>
                </div>
            </div>
        </div>
        '''.format(**stats)

    def _generate_table_html(self) -> str:
        columns = self.df.columns.tolist()
        rows = self.df.values.tolist()

        thead = ''.join('<th>{}</th>'.format(col) for col in columns)
        tbody_rows = ''
        for i, row in enumerate(rows):
            row_class = 'even' if i % 2 == 0 else 'odd'
            cells = ''.join('<td>{}</td>'.format(self._escape_html(str(cell))) for cell in row)
            tbody_rows += '<tr class="{}">{}</tr>'.format(row_class, cells)
        
        csv_data = self._generate_csv_data()

        return '''
        <div class="table-header">
            <h3 class="subsection-title">详细数据表格</h3>
            <button class="export-btn" onclick="exportCSV()">
                <span class="export-icon">↓</span> 导出 CSV
            </button>
        </div>
        <div class="table-container">
            <table class="data-table" id="data-table">
                <thead><tr>{}</tr></thead>
                <tbody>{}</tbody>
            </table>
        </div>
        <script>
            var csvData = `{}`;
            function exportCSV() {{
                var blob = new Blob([csvData], {{ type: 'text/csv;charset=utf-8;' }});
                var link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'celltype_annotation_results.csv';
                link.click();
                URL.revokeObjectURL(link.href);
            }}
        </script>
        '''.format(thead, tbody_rows, csv_data)

    def _escape_html(self, text: str) -> str:
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def _generate_csv_data(self) -> str:
        return self.df.to_csv(index=False)

    def _generate_tabs_html(self) -> str:
        tabs = []
        color_classes = ['btn-verdigris', 'btn-charcoal', 'btn-tuscan', 'btn-sandy', 'btn-peach']
        
        tabs.append('''
        <div class="control-group">
            <span class="control-label">ALL</span>
            <button class="hardware-btn btn-verdigris is-active" data-tab="overview" aria-label="Overview">
                <div class="btn-well"><div class="btn-cap"></div></div>
            </button>
        </div>
        ''')
        
        for i, key in enumerate(self.markdown_dict.keys()):
            safe_key = self._sanitize_key(key)
            display_name = self._escape_html(key)
            color_class = color_classes[i % len(color_classes)]
            short_label = key.replace('Cluster ', 'C-') if key.startswith('Cluster') else key[:6]
            tabs.append('''
            <div class="control-group">
                <span class="control-label">{}</span>
                <button class="hardware-btn {}" data-tab="{}" aria-label="{}">
                    <div class="btn-well"><div class="btn-cap"></div></div>
                </button>
            </div>
            '''.format(short_label, color_class, safe_key, display_name))
        
        return ''.join(tabs)

    def _generate_content_html(self, stats_section: str, table_html: str) -> str:
        overview_content = '''
        <div class="tab-content active" id="overview">
            <h2 class="section-title">注释结果总览</h2>
            {}
            {}
        </div>
        '''.format(stats_section, table_html)

        other_contents = []
        for key, md_content in self.markdown_dict.items():
            safe_key = self._sanitize_key(key)
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'nl2br', 'toc']
            )
            other_contents.append('''
            <div class="tab-content" id="{}">
                <div class="markdown-body">
                    {}
                </div>
            </div>
            '''.format(safe_key, html_content))

        return '\n'.join([overview_content] + other_contents)

    def _sanitize_key(self, key: str) -> str:
        return ''.join(c if c.isalnum() or c in '-_' else '_' for c in key)

    def _generate_grille_pattern(self) -> str:
        svg_content = ''
        hole_radius = 5.5
        dot_spacing = 12
        
        bitmap_font = {
            'o': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'h': [
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'm': [
                [1,0,0,0,1],
                [1,1,0,1,1],
                [1,0,1,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'y': [
                [1,0,0,0,1],
                [0,1,0,1,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0]
            ],
            'c': [
                [0,1,1,1,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [0,1,1,1,0]
            ],
            'e': [
                [1,1,1,1,0],
                [1,0,0,0,0],
                [1,1,1,0,0],
                [1,0,0,0,0],
                [1,1,1,1,0]
            ],
            'l': [
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,0]
            ],
            't': [
                [1,1,1,1,1],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0]
            ],
            'i': [
                [0,1,1,1,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,1,1,1,0]
            ],
            'p': [
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,1,1,1,0],
                [1,0,0,0,0],
                [1,0,0,0,0]
            ]
        }
        
        text = "ohmycelltype"
        letter_width = 5
        letter_height = 5
        spacing_between_letters = 1
        
        total_width = len(text) * (letter_width + spacing_between_letters) - spacing_between_letters
        start_x = 160 - (total_width * dot_spacing) / 2
        start_y = 160 - (letter_height * dot_spacing) / 2
        
        colors = ['var(--charcoal-blue)', 'var(--verdigris)', 'var(--tuscan-sun)', 
                  'var(--sandy-brown)', 'var(--burnt-peach)']
        
        all_letter_positions = []
        color_index = 0
        
        for char_idx, char in enumerate(text):
            if char not in bitmap_font:
                continue
            bitmap = bitmap_font[char]
            letter_positions = []
            
            for row_idx, row in enumerate(bitmap):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        x = start_x + (char_idx * (letter_width + spacing_between_letters) + col_idx) * dot_spacing
                        y = start_y + row_idx * dot_spacing
                        letter_positions.append((x, y))
            
            all_letter_positions.append((char, letter_positions, color_index))
            color_index = (color_index + 1) % len(colors)
        
        for char, positions, char_color_idx in all_letter_positions:
            color = colors[char_color_idx]
            for i, (x, y) in enumerate(positions):
                is_highlight = (i == 0 or i == len(positions) - 1)
                if is_highlight:
                    svg_content += '<g class="grille-block" style="transform-origin: {}px {}px">'.format(x, y)
                    svg_content += '<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(x, y, hole_radius + 1, color)
                    svg_content += '<circle cx="{}" cy="{}" r="{}" fill="url(#block-light)" />'.format(x, y, hole_radius + 1)
                    svg_content += '</g>'
                else:
                    svg_content += '<circle cx="{}" cy="{}" r="{}" class="grille-hole" fill="{}" />'.format(x, y, hole_radius, color)
        
        return svg_content

    def _get_html_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cell Type Annotation Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --charcoal-blue: #264653;
            --verdigris: #2a9d8f;
            --tuscan-sun: #e9c46a;
            --sandy-brown: #f4a261;
            --burnt-peach: #e76f51;
            
            --casing-bg: #E3E4DF;
            --casing-highlight: rgba(255,255,255,0.7);
            --casing-shadow: rgba(0,0,0,0.08);
            --panel-gap-dark: rgba(0,0,0,0.15);
            --panel-gap-light: rgba(255,255,255,0.8);
            
            --text-main: #264653;
            --text-muted: #555555;
            --text-label: #6A6B66;
            --hole-fill: #1C1C1A;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        body {
            background-color: #C8C9C4;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            color: var(--text-main);
            padding: 40px 20px;
        }

        .device-panel {
            background-color: var(--casing-bg);
            width: 100%;
            max-width: 920px;
            border-radius: 12px;
            position: relative;
            box-shadow: 
                0 20px 50px rgba(0,0,0,0.15),
                0 5px 15px rgba(0,0,0,0.05),
                inset 1px 1px 2px var(--casing-highlight),
                inset -1px -1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            padding: 30px 40px 0;
        }

        .brand {
            font-weight: 600;
            font-size: 14px;
            letter-spacing: -0.02em;
            color: var(--text-main);
        }

        .model-number {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 12px;
            color: var(--text-muted);
            letter-spacing: 0.05em;
        }

        .hero-section {
            display: flex;
            justify-content: center;
            padding: 30px 0 10px;
        }

        .grille-svg {
            width: 280px;
            height: 280px;
            overflow: visible;
        }

        .grille-hole {
            fill: var(--hole-fill);
        }

        .grille-block {
            filter: drop-shadow(0px 4px 3px rgba(0,0,0,0.25));
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .controls-section {
            display: flex;
            justify-content: center;
            gap: 12px;
            padding: 15px 20px 25px;
            position: relative;
            flex-wrap: wrap;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }

        .control-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 9px;
            font-weight: 700;
            color: var(--text-label);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .hardware-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 0;
            outline: none;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-well {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #DADBD4;
            box-shadow: 
                inset 2px 2px 3px rgba(0,0,0,0.1),
                inset -1px -1px 3px rgba(255,255,255,0.7);
            position: relative;
            display: flex;
            justify-content: center;
        }

        .btn-cap {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            position: absolute;
            top: -2px;
            background-color: var(--btn-color);
            box-shadow: 
                inset 0 2px 2px rgba(255,255,255,0.4),
                inset 0 -1px 2px rgba(0,0,0,0.2),
                0 3px 0 var(--btn-shade),
                0 5px 5px rgba(0,0,0,0.2);
            transition: all 0.08s cubic-bezier(0.25, 1, 0.5, 1);
        }

        .hardware-btn:active .btn-cap,
        .hardware-btn.is-active .btn-cap {
            top: 2px;
            box-shadow: 
                inset 0 1px 2px rgba(255,255,255,0.3),
                inset 0 -1px 2px rgba(0,0,0,0.3),
                0 0px 0 var(--btn-shade),
                0 1px 2px rgba(0,0,0,0.1);
        }

        .btn-charcoal  { --btn-color: var(--charcoal-blue); --btn-shade: #1A3540; }
        .btn-verdigris { --btn-color: var(--verdigris);     --btn-shade: #1E7A70; }
        .btn-tuscan    { --btn-color: var(--tuscan-sun);    --btn-shade: #B88000; }
        .btn-sandy     { --btn-color: var(--sandy-brown);   --btn-shade: #C07A30; }
        .btn-peach     { --btn-color: var(--burnt-peach);   --btn-shade: #B54535; }

        .panel-divider {
            height: 2px;
            width: 100%;
            background: var(--panel-gap-dark);
            border-bottom: 1px solid var(--panel-gap-light);
        }

        .inventory-section {
            padding: 30px 40px 40px;
            background: rgba(255,255,255,0.1);
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--panel-gap-dark);
            box-shadow: 0 1px 0 var(--panel-gap-light);
        }

        .subsection-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
            margin: 24px 0 12px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: rgba(255,255,255,0.3);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: inset 1px 1px 2px rgba(255,255,255,0.5);
        }

        .stat-icon {
            font-size: 28px;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
        }

        .stat-icon-1 { background: rgba(233, 196, 106, 0.3); }
        .stat-icon-2 { background: rgba(244, 162, 97, 0.3); }
        .stat-icon-3 { background: rgba(231, 111, 81, 0.3); }

        .stat-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            color: var(--verdigris);
            line-height: 1.2;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 2px;
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 24px 0 12px;
        }

        .table-header .subsection-title {
            margin: 0;
        }

        .export-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-main);
            background: rgba(255,255,255,0.4);
            border: 1px solid rgba(0,0,0,0.1);
            border-top-color: rgba(255,255,255,0.8);
            border-left-color: rgba(255,255,255,0.8);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }

        .export-icon {
            font-size: 14px;
            color: var(--verdigris);
        }

        .export-btn:hover {
            background: rgba(42, 157, 143, 0.15);
            border-color: rgba(0,0,0,0.15);
            box-shadow: 1px 2px 4px rgba(0,0,0,0.12);
        }

        .export-btn:active {
            background: rgba(42, 157, 143, 0.25);
            box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1);
        }

        .table-container {
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: inset 1px 1px 2px rgba(255,255,255,0.3);
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 24px 0 12px;
        }

        .table-header .subsection-title {
            margin: 0;
        }

        .export-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-main);
            background: rgba(255,255,255,0.4);
            border: 1px solid rgba(0,0,0,0.1);
            border-top-color: rgba(255,255,255,0.8);
            border-left-color: rgba(255,255,255,0.8);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }

        .export-btn:hover {
            background: rgba(42, 157, 143, 0.15);
            border-color: var(--verdigris);
        }

        .export-btn:active {
            background: rgba(42, 157, 143, 0.25);
            box-shadow: inset 1px 1px 2px rgba(0,0,0,0.08);
        }

        .export-icon {
            font-size: 14px;
            font-weight: 700;
        }

        .table-container {
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: inset 1px 1px 2px rgba(255,255,255,0.3);
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }

        .data-table th {
            text-align: left;
            padding: 12px 16px;
            color: var(--text-label);
            font-weight: 500;
            font-size: 10px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            border-bottom: 1px solid var(--panel-gap-dark);
            box-shadow: 0 1px 0 var(--panel-gap-light);
            background: rgba(0,0,0,0.03);
        }

        .data-table td {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            vertical-align: middle;
        }

        .data-table tbody tr:hover {
            background: rgba(42, 157, 143, 0.1);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .markdown-body {
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 24px;
        }

        .markdown-body h1 {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--panel-gap-dark);
            box-shadow: 0 1px 0 var(--panel-gap-light);
        }

        .markdown-body h2 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-main);
            margin: 20px 0 12px;
        }

        .markdown-body h3 {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
            margin: 16px 0 8px;
        }

        .markdown-body p {
            margin-bottom: 12px;
            color: var(--text-muted);
            line-height: 1.7;
        }

        .markdown-body ul, .markdown-body ol {
            margin: 12px 0;
            padding-left: 24px;
        }

        .markdown-body li {
            margin-bottom: 6px;
            color: var(--text-muted);
        }

        .markdown-body code {
            background: rgba(42, 157, 143, 0.15);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--verdigris);
        }

        .markdown-body pre {
            background: #1C1C1A;
            color: #E8E8E6;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0;
        }

        .markdown-body pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }

        .markdown-body blockquote {
            border-left: 4px solid var(--burnt-peach);
            padding-left: 16px;
            margin: 16px 0;
            color: var(--text-muted);
            font-style: italic;
        }

        .markdown-body table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
        }

        .markdown-body th, .markdown-body td {
            border: 1px solid var(--panel-gap-dark);
            padding: 10px 14px;
            text-align: left;
        }

        .markdown-body th {
            background: rgba(0,0,0,0.03);
            font-weight: 600;
        }

        .panel-footer {
            padding: 0 40px 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }

        .footer-text {
            font-weight: 500;
            font-size: 14px;
            letter-spacing: -0.02em;
        }

        @media (max-width: 600px) {
            .device-panel { border-radius: 0; }
            body { padding: 0; background: var(--casing-bg); }
            .panel-header, .inventory-section, .panel-footer { padding-left: 16px; padding-right: 16px; }
            .controls-section { gap: 12px; }
            .grille-svg { transform: scale(0.8); }
            .btn-well { transform: scale(0.85); }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="device-panel">
        <header class="panel-header">
            <div class="brand">OHMYCELLTYPE</div>
            <div class="model-number">v1.0.0</div>
        </header>

        <section class="hero-section">
            <svg class="grille-svg" viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <radialGradient id="block-light" cx="30%" cy="30%" r="70%">
                        <stop offset="0%" stop-color="rgba(255,255,255,0.5)"></stop>
                        <stop offset="100%" stop-color="rgba(0,0,0,0)"></stop>
                    </radialGradient>
                </defs>
                <g id="grille-pattern">{grille_pattern}</g>
            </svg>
        </section>

        <section class="controls-section">
            {tabs_html}
        </section>

        <div class="panel-divider"></div>

        <section class="inventory-section">
            {content_html}
        </section>

        <footer class="panel-footer">
            <div class="footer-text">Cell Type Annotation</div>
            <div class="model-number">{generated_time}</div>
        </footer>
    </main>

    <script>
        (function() {
            var tabBtns = document.querySelectorAll('.hardware-btn');
            var tabContents = document.querySelectorAll('.tab-content');

            tabBtns.forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var tabId = this.getAttribute('data-tab');
                    if (!tabId) return;

                    tabBtns.forEach(function(b) {
                        b.classList.remove('is-active');
                    });
                    tabContents.forEach(function(c) {
                        c.classList.remove('active');
                    });

                    this.classList.add('is-active');
                    var targetContent = document.getElementById(tabId);
                    if (targetContent) {
                        targetContent.classList.add('active');
                    }
                });
            });
        })();
    </script>
</body>
</html>'''
