

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SignizeLeadPage:

    NAME_INPUT        = (By.ID, "name_at_lead")
    EMAIL_INPUT       = (By.ID, "email_at_lead")
    PHONE_INPUT       = (By.ID, "phone_number_at_lead")
    DETAILS_TEXTAREA  = (By.ID, "details_at_lead")

    PLACEMENT_INDOOR  = (By.XPATH, "//label[@for='Indoor_at_lead']")
    PLACEMENT_OUTDOOR = (By.XPATH, "//label[@for='Outdoor_at_lead']")

    MOCKUP_CONTAINER  = (By.ID, "checkboxContainer_at_lead")
    FILE_INPUT        = (By.ID, "fileInput_at_lead")
    SUBMIT_BTN        = (By.XPATH, "//button[contains(@class,'submitButton')]")
    SUCCESS_DIV       = (By.ID, "submitSuccess_at_lead")  # ✅ renamed for clarity

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)  # ✅ increased from 12 → 20
        self.submission_time_seconds = None

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.SUBMIT_BTN))

    def fill_name(self, value: str):
        self._type(self.NAME_INPUT, value)

    def fill_email(self, value: str):
        self._type(self.EMAIL_INPUT, value)

    def fill_phone(self, value: str):
        self._type(self.PHONE_INPUT, value)

    def fill_details(self, value: str):
        self._type(self.DETAILS_TEXTAREA, value)

    def select_placements(self, indoor=False, outdoor=False):
        if indoor:
            el = self.wait.until(EC.element_to_be_clickable(self.PLACEMENT_INDOOR))
            self.driver.execute_script("arguments[0].click();", el)
        if outdoor:
            el = self.wait.until(EC.element_to_be_clickable(self.PLACEMENT_OUTDOOR))
            self.driver.execute_script("arguments[0].click();", el)

    def select_mockup_types(self, mockup_id: str):
        locator = (By.XPATH, f"//label[@for='{mockup_id}']")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def upload_image(self, path: str):
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].classList.remove('d-none');", el)
        el.send_keys(path)
        self.wait.until(lambda d: el.get_attribute("value") != "")

    def submit(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)  # ✅ let scroll settle before clicking

        submit_start = time.time()
        self.driver.execute_script("""
            var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            arguments[0].dispatchEvent(evt);
        """, btn)

        try:
            # ✅ FIXED: watch for d-none being removed, not visibility
            # EC.visibility_of_element_located fails because div is hidden via d-none (display:none)
            self.wait.until(lambda d: "d-none" not in d.find_element(
                By.ID, "submitSuccess_at_lead").get_attribute("class")
            )
        except TimeoutException:
            pass
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float | None:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        # ✅ FIXED: check class attribute instead of Selenium visibility
        try:
            el = self.driver.find_element(By.ID, "submitSuccess_at_lead")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    # ── helpers ────────────────────────────────────────────────────────────────

    def _type(self, locator, value: str):
        el = self.wait.until(EC.presence_of_element_located(locator))
        try:
            el.clear()
            el.send_keys(value)
        except Exception:
            self.driver.execute_script("arguments[0].value = arguments[1];", el, value)
        # ✅ fire all framework events so JS validation picks up the value
        self.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('focus',   { bubbles: true }));
            arguments[0].dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));
            arguments[0].dispatchEvent(new KeyboardEvent('keyup',   { bubbles: true }));
            arguments[0].dispatchEvent(new Event('input',   { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change',  { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur',    { bubbles: true }));
        """, el)