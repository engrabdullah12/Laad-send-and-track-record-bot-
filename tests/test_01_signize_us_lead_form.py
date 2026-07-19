import os
import time
import pytest
from pages.signize_us_lead_page import SignizeLeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import init_md_report, append_unified_row

URL = "https://signize.us/pages/custom-business-sign"
ENDPOINT = "https://apibase.marke-ter.online/api/submit/signize"

@pytest.fixture
def driver():
    from driver_factory import get_driver
    drv = get_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()
def test_lead_form_submission(driver):

    page = SignizeLeadPage(driver)
    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("2223334444")
    page.fill_details("TEST")
    page.select_placements(indoor=False, outdoor=True)
    page.select_mockup_types("face_lit_3d_frontlit_at_lead")
    page.select_mockup_types("push_through_letters_at_lead")
   

    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)
    driver.get_log("performance")

    driver.execute_cdp_cmd("Network.enable", {})
    driver.get_log("performance")
    page.submit()
    time.sleep(60)
    duration = page.get_submission_duration()
    assert page.success_visible(), "Expected 'Thank You' confirmation"
    time.sleep(8)
    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True,
        debug=True
    )


    append_unified_row(
    record=record,
    site_name="Signize Us ",
    visit_url=URL,
 
)

    driver.get_log("performance")
 

