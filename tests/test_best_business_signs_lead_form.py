# import os
# import time
# import pytest

# from pages.best_business_signs_lead_page import BestBusinessSignsLeadPage
# from utils.report_writer import init_md_report, append_row, append_pagespeed_table
# from utils.network_logs import find_airtable_record
# from utils.Pagespeed import fetch_pagespeed_score

# URL = "https://bestbusinesssigns.com/pages/private"
# ENDPOINT = "https://apibase.marke-ter.online/api/submit/bestbusinesssign"  

# @pytest.fixture
# def driver():
#     from utils.driver import create_chrome_driver
#     drv = create_chrome_driver(headless=False)
#     drv.execute_cdp_cmd("Network.enable", {})
#     yield drv
#     drv.quit()

# def test_lead_form_submission(driver):
   
#     page = BestBusinessSignsLeadPage(driver)
#     page.open(URL)

#     page.fill_name("-SQA Test-")
#     page.fill_email("zainabbashir.codeblue@gmail.com")
#     page.fill_company("CodeBlue")
#     page.fill_lead_added_by("CodeBlue")

#     page.select_custom_type(partial=False)
#     page.select_placements()
#     page.select_preferences()
#     page.select_size(custom=False)
#     page.select_services()
#     page.select_mockups()

#     img_path = os.path.abspath("CodeBlue.png")
#     if os.path.exists(img_path):
#         page.upload_image(img_path)

#     driver.get_log("performance")

#     page.fill_details("Test")

#     page.submit()

#     assert page.success_visible(), "Expected 'Thank You' confirmation after submission"


#     time.sleep(8)


#     record, meta = find_airtable_record(driver, endpoint_filter=ENDPOINT, return_meta=True)
#     assert record, "POST request to BestBusinessSigns not captured"


#     append_row(record, meta, site_name="BestBusinessSigns", visit_url=URL)

#     driver.get_log("performance")

#     desktop = fetch_pagespeed_score(URL, strategy="desktop")
#     mobile = fetch_pagespeed_score(URL, strategy="mobile")
#     append_pagespeed_table(URL, desktop, mobile)
