"""
HTML report generator
"""
from typing import Dict, List
from jinja2 import Template
from datetime import datetime

class ReportGenerator:
    """Generate HTML reports from review results"""
    
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .meta {
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }
        .summary-card h3 {
            font-size: 12px;
            text-transform: uppercase;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        .score {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .score-value {
            font-size: 72px;
            font-weight: bold;
            margin: 10px 0;
        }
        .score-label {
            font-size: 18px;
            opacity: 0.9;
        }
        .issues-section {
            margin-top: 40px;
        }
        .issue {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
            transition: box-shadow 0.2s;
        }
        .issue:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .issue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .issue-type {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .type-bug { background: #e74c3c; color: white; }
        .type-security { background: #c0392b; color: white; }
        .type-style { background: #f39c12; color: white; }
        .type-documentation { background: #3498db; color: white; }
        .severity {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .severity-critical { background: #c0392b; color: white; }
        .severity-high { background: #e74c3c; color: white; }
        .severity-medium { background: #f39c12; color: white; }
        .severity-low { background: #95a5a6; color: white; }
        .issue-location {
            color: #7f8c8d;
            font-size: 14px;
            margin: 10px 0;
        }
        .issue-description {
            margin: 15px 0;
            line-height: 1.8;
        }
        .suggestion {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .suggestion h4 {
            color: #2e7d32;
            margin-bottom: 8px;
        }
        .explanation {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .explanation h4 {
            color: #1565c0;
            margin-bottom: 8px;
        }
        .recommendations {
            margin-top: 40px;
            padding: 20px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 6px;
        }
        .recommendations h2 {
            color: #856404;
            margin-bottom: 15px;
        }
        .recommendations ul {
            list-style-position: inside;
        }
        .recommendations li {
            margin: 8px 0;
            color: #856404;
        }
        .no-issues {
            text-align: center;
            padding: 60px 20px;
            color: #27ae60;
        }
        .no-issues-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Review Report</h1>
        <div class="meta">
            Generated: {{ timestamp }}<br>
            {% if file_path %}File: {{ file_path }}<br>{% endif %}
            {% if language %}Language: {{ language }}<br>{% endif %}
            Model: {{ model_used }}
        </div>
        
        <div class="score">
            <div class="score-label">Overall Score</div>
            <div class="score-value">{{ overall_score }}/100</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Issues</h3>
                <div class="value">{{ summary.total_issues }}</div>
            </div>
            <div class="summary-card">
                <h3>Bugs</h3>
                <div class="value">{{ summary.by_type.bug or 0 }}</div>
            </div>
            <div class="summary-card">
                <h3>Security</h3>
                <div class="value">{{ summary.by_type.security or 0 }}</div>
            </div>
            <div class="summary-card">
                <h3>Style</h3>
                <div class="value">{{ summary.by_type.style or 0 }}</div>
            </div>
            <div class="summary-card">
                <h3>Documentation</h3>
                <div class="value">{{ summary.by_type.documentation or 0 }}</div>
            </div>
        </div>
        
        {% if issues %}
        <div class="issues-section">
            <h2>Issues Found</h2>
            {% for issue in issues %}
            <div class="issue">
                <div class="issue-header">
                    <span class="issue-type type-{{ issue.type }}">{{ issue.type }}</span>
                    <span class="severity severity-{{ issue.severity }}">{{ issue.severity }}</span>
                </div>
                <div class="issue-location">
                    Line {{ issue.line }}{% if issue.column %}, Column {{ issue.column }}{% endif %}
                </div>
                <div class="issue-description">
                    {{ issue.description }}
                </div>
                {% if issue.suggestion %}
                <div class="suggestion">
                    <h4>💡 Suggestion</h4>
                    <p>{{ issue.suggestion }}</p>
                </div>
                {% endif %}
                {% if issue.explanation %}
                <div class="explanation">
                    <h4>📚 Learning</h4>
                    <p>{{ issue.explanation }}</p>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-issues">
            <div class="no-issues-icon">✅</div>
            <h2>No Issues Found!</h2>
            <p>Great job! Your code looks clean and well-written.</p>
        </div>
        {% endif %}
        
        {% if recommendations %}
        <div class="recommendations">
            <h2>General Recommendations</h2>
            <ul>
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""
    
    def generate_html(self, review_result: Dict, file_path: str = None, language: str = None) -> str:
        """Generate HTML report from review results"""
        template = Template(self.HTML_TEMPLATE)
        
        return template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=file_path,
            language=language,
            model_used=review_result.get("model_used", "unknown"),
            overall_score=review_result.get("overall_score", 100),
            summary=review_result.get("summary", {}),
            issues=review_result.get("issues", []),
            recommendations=review_result.get("recommendations", [])
        )

report_generator = ReportGenerator()

