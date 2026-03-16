import pandas as pd
import markdown
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
        stats_cards = self._generate_stats_cards(stats)
        table_html = self._generate_table_html()
        tabs_html = self._generate_tabs_html()
        content_html = self._generate_content_html(stats_cards, table_html)
        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return self._get_html_template().format(
            tabs_html=tabs_html,
            content_html=content_html,
            generated_time=generated_time
        )

    def _calculate_stats(self) -> dict:
        cluster_count = len(self.df)
        cell_type_count = self.df.iloc[:, 1].nunique() if len(self.df.columns) > 1 else 0
        cell_subtype_count = self.df.iloc[:, 2].nunique() if len(self.df.columns) > 2 else 0
        return {
            'cluster_count': cluster_count,
            'cell_type_count': cell_type_count,
            'cell_subtype_count': cell_subtype_count
        }

    def _generate_stats_cards(self, stats: dict) -> str:
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

        return '''
        <div class="table-container">
            <table class="data-table">
                <thead><tr>{}</tr></thead>
                <tbody>{}</tbody>
            </table>
        </div>
        '''.format(thead, tbody_rows)

    def _escape_html(self, text: str) -> str:
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def _generate_tabs_html(self) -> str:
        tabs = ['<button class="tab-btn active" data-tab="overview">📊 Overview</button>']
        for key in self.markdown_dict.keys():
            safe_key = self._sanitize_key(key)
            display_name = self._escape_html(key)
            tabs.append('<button class="tab-btn" data-tab="{}">📄 {}</button>'.format(safe_key, display_name))
        return ''.join(tabs)

    def _generate_content_html(self, stats_cards: str, table_html: str) -> str:
        overview_content = '''
        <div class="tab-content active" id="overview">
            <h2 class="section-title">注释结果总览</h2>
            {}
            <h3 class="subsection-title">详细数据表格</h3>
            {}
        </div>
        '''.format(stats_cards, table_html)

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

    def _get_html_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cell Type Annotation Report</title>
    <style>
        :root {{
            --charcoal-blue: #264653;
            --verdigris: #2a9d8f;
            --tuscan-sun: #e9c46a;
            --sandy-brown: #f4a261;
            --burnt-peach: #e76f51;
            --bg-primary: #F8F9FA;
            --bg-secondary: #FFFFFF;
            --bg-tertiary: #F1F3F5;
            --text-primary: #264653;
            --text-secondary: #3D5A6C;
            --text-muted: #6B7C85;
            --accent-primary: #2a9d8f;
            --accent-secondary: #e9c46a;
            --accent-light: #E8F5F3;
            --border-color: #D4E0E6;
            --shadow-sm: 0 1px 3px 0 rgba(38, 70, 83, 0.08);
            --shadow-md: 0 4px 12px -2px rgba(38, 70, 83, 0.12);
            --shadow-lg: 0 12px 24px -4px rgba(38, 70, 83, 0.15);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .header {{
            background: linear-gradient(135deg, var(--charcoal-blue) 0%, var(--verdigris) 100%);
            color: white;
            padding: 32px 40px;
            box-shadow: var(--shadow-lg);
        }}

        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .main-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 40px;
        }}

        .tabs-nav {{
            display: flex;
            gap: 8px;
            background: var(--bg-secondary);
            padding: 8px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            margin-bottom: 24px;
            overflow-x: auto;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            padding: 12px 24px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-radius: var(--radius-md);
            transition: all 0.2s ease;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            background: var(--accent-primary);
            color: white;
            box-shadow: var(--shadow-sm);
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.3s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .section-title {{
            font-size: 22px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border-color);
        }}

        .subsection-title {{
            font-size: 18px;
            font-weight: 500;
            color: var(--text-primary);
            margin: 32px 0 16px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}

        .stat-card {{
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}

        .stat-icon {{
            font-size: 40px;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--radius-md);
        }}

        .stat-icon-1 {{
            background: rgba(233, 196, 106, 0.2);
        }}

        .stat-icon-2 {{
            background: rgba(244, 162, 97, 0.2);
        }}

        .stat-icon-3 {{
            background: rgba(231, 111, 81, 0.2);
        }}

        .stat-value {{
            font-size: 36px;
            font-weight: 700;
            color: var(--verdigris);
            line-height: 1.2;
        }}

        .stat-label {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .table-container {{
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        .data-table thead {{
            background: var(--charcoal-blue);
        }}

        .data-table th {{
            color: white;
            font-weight: 600;
            text-align: left;
            padding: 16px 20px;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}

        .data-table td {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .data-table tbody tr.even {{
            background: var(--bg-secondary);
        }}

        .data-table tbody tr.odd {{
            background: var(--bg-tertiary);
        }}

        .data-table tbody tr:hover {{
            background: var(--accent-light);
        }}

        .markdown-body {{
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            padding: 32px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
        }}

        .markdown-body h1 {{
            font-size: 26px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border-color);
        }}

        .markdown-body h2 {{
            font-size: 22px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 28px 0 16px;
        }}

        .markdown-body h3 {{
            font-size: 18px;
            font-weight: 500;
            color: var(--text-primary);
            margin: 24px 0 12px;
        }}

        .markdown-body p {{
            margin-bottom: 16px;
            color: var(--text-secondary);
        }}

        .markdown-body ul, .markdown-body ol {{
            margin: 16px 0;
            padding-left: 28px;
        }}

        .markdown-body li {{
            margin-bottom: 8px;
            color: var(--text-secondary);
        }}

        .markdown-body code {{
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 13px;
            color: var(--verdigris);
        }}

        .markdown-body pre {{
            background: #1E293B;
            color: #E2E8F0;
            padding: 20px;
            border-radius: var(--radius-md);
            overflow-x: auto;
            margin: 20px 0;
        }}

        .markdown-body pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}

        .markdown-body blockquote {{
            border-left: 4px solid var(--burnt-peach);
            padding-left: 20px;
            margin: 20px 0;
            color: var(--text-secondary);
            font-style: italic;
        }}

        .markdown-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .markdown-body th, .markdown-body td {{
            border: 1px solid var(--border-color);
            padding: 12px 16px;
            text-align: left;
        }}

        .markdown-body th {{
            background: var(--bg-tertiary);
            font-weight: 600;
        }}

        .footer {{
            text-align: center;
            padding: 24px;
            color: var(--text-muted);
            font-size: 13px;
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }}

        @media (max-width: 768px) {{
            .main-container {{
                padding: 20px;
            }}

            .header {{
                padding: 24px 20px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .tabs-nav {{
                padding: 6px;
            }}

            .tab-btn {{
                padding: 10px 16px;
                font-size: 13px;
            }}

            .markdown-body {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>🧬 Cell Type Annotation Report</h1>
        <p>单细胞 RNA-seq 数据细胞类型注释分析报告</p>
    </header>

    <main class="main-container">
        <nav class="tabs-nav">
            {tabs_html}
        </nav>

        {content_html}
    </main>

    <footer class="footer">
        Generated by ohmycelltype • {generated_time}
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var tabBtns = document.querySelectorAll('.tab-btn');
            var tabContents = document.querySelectorAll('.tab-content');

            tabBtns.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    var tabId = this.getAttribute('data-tab');

                    tabBtns.forEach(function(b) {{
                        b.classList.remove('active');
                    }});
                    tabContents.forEach(function(c) {{
                        c.classList.remove('active');
                    }});

                    this.classList.add('active');
                    document.getElementById(tabId).classList.add('active');
                }});
            }});
        }});
    </script>
</body>
</html>'''
