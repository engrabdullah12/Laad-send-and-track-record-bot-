import os
import time
import pytest

from driver_factory import get_driver
from pages.signage_inc_lead_page import SignageIncLeadPage
from utils.network_logs import find_airtable_record
from utils.report_writer import init_md_report, append_unified_row


URL      = "https://signage.inc/pages/signage-quote"
ENDPOINT = "https://signsincv2.codeblue.agency/api/submit/signage/step-two"


@pytest.fixture
def driver():
    drv = get_driver(headless=False)
    drv.execute_cdp_cmd("Network.enable", {})
    yield drv
    drv.quit()


def test_lead_form_submission(driver):
    page = SignageIncLeadPage(driver)

    page.open(URL)
    page.fill_name("-Automated test-")
    page.fill_email("zainabbashir.codeblue@gmail.com")
    page.fill_phone("2223334444")

    img_path = os.path.abspath("CodeBlue.png")
    if os.path.exists(img_path):
        page.upload_image(img_path)

    page.click_continue()

    page.select_sign_usage(indoor=True)
    page.select_lighting("back-lit")
    page.select_material("not-sure")
    driver.get_log("performance")
    page.submit()
    duration = page.get_submission_duration()

    assert page.success_visible(), "Expected 'Thank You' confirmation"

    time.sleep(8)
    record, meta = find_airtable_record(
        driver,
        endpoint_filter=ENDPOINT,
        return_meta=True,
        debug=True

    )
    assert record, "Airtable record not captured"

    append_unified_row(
        record=record,
        site_name="Signage Inc",
        visit_url=URL,
   
    )

    driver.get_log("performance")