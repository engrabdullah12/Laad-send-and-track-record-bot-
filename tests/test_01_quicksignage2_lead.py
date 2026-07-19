import os
import time
import pytest
from pages.quicksignage2_lead_page import QuickSignage2LeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import append_unified_row
from utils.driver import create_chrome_driver

URL      = "https://quicksignage.com/pages/mockup"
ENDPOINT = "https://quicksignagev2.codeblue.agency/api/webhook/lead/update"


@pytest.fixture
def driver():

    drv = create_chrome_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()


def test_lead_form_submission(driver):
    page = QuickSignage2LeadPage(driver)

    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("2015550123")
    page.fill_website("test.com")

    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)
    else:
        print(f"⚠️  Image not found at {img_path} — skipping upload")

    page.click_continue()


    page.select_sign_usage(indoor=True)
    page.select_lighting("backlit")

    page.select_material("notsure")


    driver.get_log("performance")
    page.submit()
    duration = page.get_submission_duration()

    assert page.success_visible(), "Expected success screen after submission"

    time.sleep(8)

    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True,
        debug=True,
    )
    assert record, "Lead record not captured"

 
    append_unified_row(
        record=record,
        site_name="QuickSignage 2",
        visit_url=URL,
      
    )

    driver.get_log("performance")