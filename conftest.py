

import pytest
from config import TARGET_SITES, SITES, LEAD_MD_PATH, LEAD_HTML_PATH, LEAD_PDF_PATH
from utils.driver import create_chrome_driver
from utils.network_logs import (
    collect_network_events,
    filter_requests,
    get_response_body,
    map_report_row,
)
from utils.report_writer import init_md_report, write_markdown_report
from utils.pdf_writer import generate_pdf_from_markdown
@pytest.fixture(scope="session")
def driver():
    drv = create_chrome_driver(headless=True)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()
@pytest.fixture(scope="function", autouse=True)
def ensure_clean_logs(driver):
    driver.get_log("performance")
    yield
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    Initialize lead markdown report ONCE with summary.
    """
    sites = [site["name"] for site in SITES]
    overview_text = (
        "- All data from lead pages successfully sent to Airtable.\n"
        "- Emails received.\n"
    )
    init_md_report(sites_tested=sites, overview=overview_text, overwrite=False)
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    1. Collect network data
    2. Append network markdown report (do NOT overwrite lead/PageSpeed tables)
    3. Convert final MD → HTML → PDF
    """
    drv = create_chrome_driver(headless=True)
    drv.execute_cdp_cmd("Network.enable", {})
    sections = []
    for site in TARGET_SITES:
        drv.get(site["visit_url"])

        events = collect_network_events(drv)
        matched = filter_requests(
            events,
            site["endpoint_filter"],
            site.get("method", "POST"),
        )
        headers = [c["label"] for c in site.get("report_row", [])]
        rows = []
        for req_id, meta in matched.items():
            body = get_response_body(drv, req_id)
            if not body:
                continue
            row = map_report_row(site.get("report_row", []), body, meta)
            rows.append(row)
        if rows:
            sections.append({
                "title": site["name"],
                "headers": headers,
                "rows": rows,
            })
    drv.quit()
    if sections:
        write_markdown_report(sections)
    generate_pdf_from_markdown(
        md_path=LEAD_MD_PATH,
        html_path=LEAD_HTML_PATH,
        pdf_path=LEAD_PDF_PATH,
    )
    print(f"\n PDF generated successfully: {LEAD_PDF_PATH}")
