
import os
import time
import pytest
from pages.signmakerz_lead_page import SignMakerzLeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import init_md_report, append_unified_row
from utils.driver import create_chrome_driver

URL = "https://www.signmakerz.com/pages/signmakerz-info"
ENDPOINT ="https://leads.codeblue.agency/api/no-approval"

@pytest.fixture
def driver():
  
    drv =create_chrome_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()

def test_lead_form_submission(driver):
    page = SignMakerzLeadPage(driver)
    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("2223334444")
    page.fill_details("TEST")
    page.select_placements(indoor=True, outdoor=False)
    page.select_mockup_types("2D Letter Sign")
    page.select_mockup_types("Blade Sign")

    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)

    driver.get_log("performance")
    page.submit()
    duration = page.get_submission_duration()
    assert page.success_visible(), "Expected 'Thank You' confirmation after submission"

    time.sleep(8) 

    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True,
        debug=True
    )
    assert record, "Lead record not captured"

    
    append_unified_row(
    record=record,
    site_name="SignMakerz",
    visit_url=URL,
 
)
        
    time.sleep(8)

