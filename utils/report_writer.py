from pathlib import Path
from datetime import datetime
from typing import List, Dict

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEAD_MD_PATH = OUTPUT_DIR / "leadpage_status.md"
NETWORK_REPORT_FILE = OUTPUT_DIR / "network_report.md"

UNIFIED_HEADERS = [
    "Site", "Name", "Email", "Record ID", "Date", "Time",
    "Lead Page URL", "Desktop Speed", "Mobile Speed", "Form Submit Time (s)"
]


def init_md_report(sites_tested: List[str] = None, overview: str = None, overwrite: bool = False):
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    summary_lines = []

    if sites_tested:
        summary_lines.append("**Sites Tested:**")
        for site in sites_tested:
            summary_lines.append(f"- {site}")
        summary_lines.append("")

    if overview:
        summary_lines.append("**Overview:**")
        summary_lines.append(overview)
        summary_lines.append("")

    mode = "w" if overwrite else "a"
    with LEAD_MD_PATH.open(mode, encoding="utf-8") as f:
        if overwrite or not LEAD_MD_PATH.exists():
            f.write("# Leadpages Testing Report\n\n")

        f.write(f"\n## Test Run – {timestamp}\n\n")
        if summary_lines:
            f.write("\n".join(summary_lines) + "\n\n")

        f.write("### Lead Records + PageSpeed\n\n")
        f.write("| " + " | ".join(UNIFIED_HEADERS) + " |\n")
        f.write("| " + " | ".join(["---"] * len(UNIFIED_HEADERS)) + " |\n")


def append_unified_row(record: dict, site_name: str, visit_url: str,
                      ):

    airtable_data = record.get("airtable_data", record)
    fields = airtable_data.get("fields", None)

    if fields is not None:
        # ── Standard Airtable (Signage Inc, Signize Us, Signmakers Net, Signs Inc, Signs Store) ──
        name      = fields.get("Name", "") or fields.get("Email", "").split("@")[0]
        email     = fields.get("Email", "")
        record_id = str(airtable_data.get("id", ""))
        created   = airtable_data.get("createdTime", "")

    elif "body" in airtable_data:
        # ── SignMakerz: airtable_data → body → records[0] ────────────────────
        records_list = airtable_data.get("body", {}).get("records", [])
        first_record = records_list[0] if records_list else {}

        record_id = first_record.get("id", "")         
        created   = first_record.get("createdTime", "")  

        form_data = record.get("form_data", {})
        name  = form_data.get("name", "")
        email = form_data.get("email", "")

    else:
        # ── Flat form_data fallback (no airtable_data wrapper) ───────────────
        name      = airtable_data.get("name", "")
        email     = airtable_data.get("email", "")
        record_id = str(airtable_data.get("id", ""))
        created   = airtable_data.get("created_at", "") or airtable_data.get("updated_at", "")

    date_str, time_str = "", ""
    if created:
        try:
            dt = datetime.fromisoformat(str(created).replace("Z", ""))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
        except Exception:
            pass

   

    row = [
        site_name,
        name,
        email,
        record_id,
        date_str,
        time_str,
        visit_url,
        
    ]

    with LEAD_MD_PATH.open("a", encoding="utf-8") as f:
        f.write("| " + " | ".join(str(x) for x in row) + " |\n")


def write_markdown_report(sections: List[Dict[str, any]]) -> None:
    lines = ["# Network report"]
    for section in sections:
        lines.append(f"\n## {section['title']}\n")
        headers = section["headers"]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in section["rows"]:
            lines.append("| " + " | ".join(row) + " |")
    NETWORK_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def finalize_report():
    with LEAD_MD_PATH.open("a", encoding="utf-8") as f:
        f.write("\n## Description Of Table\n\n")
        f.write("- `Record ID`: Indicates whether lead data was received in Airtable.\n")
        f.write("- `Desktop & Mobile Speed`: Page load performance scores:\n")
        f.write("  - 🟢 90–100: Excellent performance\n")
        f.write("  - 🟡 50–89: Needs improvement\n")
        f.write("  - 🔴 0–49: Poor performance\n\n")


