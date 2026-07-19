# import os
# import time
# import pytest

# from pages.signmakers_net_lead_page import SignmakersNetLeadPage
# from utils.report_writer import init_md_report, append_unified_row
# from utils.network_logs import find_airtable_record
# from utils.Pagespeed import fetch_pagespeed_score


# URL =      "https://signmakers.net/pages/signage"
# ENDPOINT = "https://signsync.marke-ter.online/api/submit/signmakersnet" 
# @pytest.fixture
# def driver():
#     from utils.driver import create_chrome_driver
#     drv = create_chrome_driver(headless=False)
#     drv.execute_cdp_cmd("Network.enable", {})
#     yield drv
#     drv.quit()
# def test_lead_form_submission(driver):

#     page = SignmakersNetLeadPage(driver)
#     page.open(URL)
#     page.fill_name("zainab-test")
#     page.fill_email("zainabbashir.codeblue@gmail.com")
#     page.fill_phone("870879809")
#     page.fill_details("Test")
#     page.select_placements(indoor=True, outdoor=True)
#     page.select_mockup_types("3D Metal Blade Sign")
#     page.select_mockup_types("Lightbox Sign")
#     img_path = os.path.abspath("CodeBlue.png")
#     if os.path.exists(img_path):
#      page.upload_image(img_path)
#     driver.get_log("performance")
#     page.fill_hidden_fields()
#     page.fill_business_name("Test Business")
#     page.submit()
#     duration = page.get_submission_duration()

#     assert page.success_visible(), "Expected 'Thank You' confirmation after submission"
#     time.sleep(5)
#     record, meta = find_airtable_record(driver, endpoint_filter=ENDPOINT, return_meta=True)
#     assert record, "POST request to Signmakers.Net not captured"
#     desktop = fetch_pagespeed_score(URL, strategy="desktop")
#     mobile = fetch_pagespeed_score(URL, strategy="mobile")
#     append_unified_row(
#     record=record,
#     site_name="Signmakers Net ",
#     visit_url=URL,
#     desktop_score=desktop,
#     mobile_score=mobile,

#     form_submit_time=duration   # ← pass it here
# )

#     driver.get_log("performance")
