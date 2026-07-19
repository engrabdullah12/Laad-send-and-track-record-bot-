import os
import time
import pytest

from utils.driver import create_chrome_driver
from pages.signs_inc_lead_page import SignsIncLeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import init_md_report, append_unified_row



URL = "https://signs.inc/pages/signage"
ENDPOINT = "https://signsincv3.codeblue.agency/api/prospects"

@pytest.fixture
def driver():
    drv = create_chrome_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()

def test_lead_form_submission(driver):
    page = SignsIncLeadPage(driver)
    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("2015550123")
    page.fill_details("TEST")
    page.select_placements(indoor=True, outdoor=False)
    page.select_mockup_types("flat_cut_2d_letter")
    page.select_mockup_types("halo_lit_3d_metal_backlit")

    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)

    driver.get_log("performance")
    page.submit()
    duration = page.get_submission_duration()
    assert page.success_visible(), "Expected 'Thank You' confirmation"

    time.sleep(8)

    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True
    )
    assert record, "Airtable record not captured"

  

    append_unified_row(
    record=record,
    site_name="Signs Inc Landing Page 1 ",
    visit_url=URL,
 
)
    driver.get_log("performance")
