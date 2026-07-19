import os
import time
import pytest
from pages.quicksignage_lead_page import QuickSignageLeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import init_md_report, append_unified_row
from utils.driver import create_chrome_driver

URL      = "https://quicksignage.com/pages/quicksignage-info"
ENDPOINT = "https://quicksignagev2.codeblue.agency/api/submit/quicksignage"


@pytest.fixture
def driver():
   
    drv = create_chrome_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()


def test_lead_form_submission(driver):
    page = QuickSignageLeadPage(driver)

    # 1. Open page
    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("11122334442")
    # 5. Upload image
    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)

    # 6. Clear log and submit
    driver.get_log("performance")
    page.submit()
    duration = page.get_submission_duration()

    assert page.success_visible(), "Expected 'Thank You' confirmation after submission"

    time.sleep(8)

    # 7. Capture lead record from network
    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True,
        debug=True
    )
    assert record, "Lead record not captured"

   
    # 9. Write report row
    append_unified_row(
        record=record,
        site_name="QuickSignage",
        visit_url=URL,
        
    )

    driver.get_log("performance")