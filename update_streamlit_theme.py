import re
from pathlib import Path

app_path = Path("superr_selector_app.py")
content = app_path.read_text(encoding="utf-8")

# Replace light backgrounds and text colors
replacements = [
    ('background: #F8FAFC;', 'background: #09061A;'),
    ('color: #0F172A;', 'color: #FFFFFF;'),
    ('background-color: #FFFFFF;', 'background-color: #0C0824;'),
    ('background: #FFFFFF;', 'background: rgba(19, 15, 48, 0.88);'),
    ('color="#0F172A"', 'color="#FFFFFF"'),
    ('color: #0F172A', 'color: #FFFFFF'),
    ('color: #334155', 'color: #CBD5E1'),
    ('color="#334155"', 'color="#CBD5E1"'),
    ('color: #475569', 'color: #94A3B8'),
    ('color="#475569"', 'color="#94A3B8"'),
    ('border: 1px solid #E2E8F0;', 'border: 1px solid rgba(139, 92, 246, 0.25);'),
    ('border: 1px solid rgba(15, 23, 42, 0.08);', 'border: 1px solid rgba(139, 92, 246, 0.22);'),
    ('border: 1px solid rgba(15, 23, 42, 0.09);', 'border: 1px solid rgba(139, 92, 246, 0.22);'),
    ('border: 1px solid rgba(15, 23, 42, 0.06);', 'border: 1px solid rgba(255, 255, 255, 0.08);'),
    ('border-right: 1px solid rgba(15, 23, 42, 0.08);', 'border-right: 1px solid rgba(255, 255, 255, 0.08);'),
    ('background: #F1F5F9;', 'background: rgba(255, 255, 255, 0.04);'),
    ('border: 1px solid #CBD5E1;', 'border: 1px solid rgba(255, 255, 255, 0.1);'),
    ('components.html(html_code, height=1380, scrolling=True)', 'components.html(html_code, height=1400, scrolling=True)')
]

for src, target in replacements:
    content = content.replace(src, target)

app_path.write_text(content, encoding="utf-8")
print("Updated superr_selector_app.py successfully!")
