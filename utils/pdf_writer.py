import subprocess
import markdown 
from pathlib import Path
from config import WKHTMLTOPDF_PATH, LEAD_MD_PATH, LEAD_HTML_PATH, LEAD_PDF_PATH
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.6;
        }}
        h1 {{
            font-size: 20px;
            margin-bottom: 10px;
        }}
        h2 {{
            font-size: 16px;
            margin-top: 20px;
        }}
        p {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 6px;
            text-align: left;
            word-break: break-word;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        ul {{
            margin-top: 8px;
            margin-bottom: 8px;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 4px;
        }}
        .description-block {{
            margin-top: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-left: 4px solid #ccc;
            font-size: 12px;
        }}
        .page-break {{
            page-break-before: always;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>
"""
def generate_pdf_from_markdown(md_path: Path = LEAD_MD_PATH, html_path: Path = LEAD_HTML_PATH, pdf_path: Path = LEAD_PDF_PATH): 
    with open(md_path, "r", encoding="utf-8") as f: html_body = markdown.markdown(f.read(), extensions=["tables"])
    full_html = HTML_TEMPLATE.format(content=html_body)
    with open(html_path, "w", encoding="utf-8") as f: f.write(full_html)
    cmd = [
    WKHTMLTOPDF_PATH,
    "--enable-local-file-access",
    "--page-width", "250mm",       
    "--page-height", "297mm",      
    "--margin-top", "10mm",
    "--margin-bottom", "10mm",
    "--margin-left", "5mm",
    "--margin-right", "5mm",
    str(html_path),
    str(pdf_path),
]
    subprocess.run(cmd, check=True)


