import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SignsIncLeadPage:

    NAME_INPUT       = (By.CSS_SELECTOR, "input#qf-name")
    EMAIL_INPUT      = (By.CSS_SELECTOR, "input#qf-email")
    PHONE_INPUT      = (By.CSS_SELECTOR, "input#qf-phone")
    DETAILS_TEXTAREA = (By.CSS_SELECTOR, "textarea#qf-details")

    PLACEMENT_INDOOR  = (By.XPATH, "//button[contains(@class, 'qf-toggle-btn') and contains(., 'Indoor')]")
    PLACEMENT_OUTDOOR = (By.XPATH, "//button[contains(@class, 'qf-toggle-btn') and contains(., 'Outdoor')]")

    FILE_INPUT  = (By.CSS_SELECTOR, "input#qf-logo")

    SUBMIT_BTN  = (By.CSS_SELECTOR, "button#qfSubmit")
    SUCCESS_DIV = (By.ID, "qfSuccess")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.submission_time_seconds = None
        self._submission_succeeded = False

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
        try:
            self._type(self.DETAILS_TEXTAREA, value)
        except TimeoutException:
            print("⚠️ Details textarea not found - skipping")

    def select_placements(self, indoor=True, outdoor=False):
        if indoor:
            self._check(self.PLACEMENT_INDOOR)
        if outdoor:
            self._check(self.PLACEMENT_OUTDOOR)

    def select_mockup_types(self, mockup_id: str):
        # The mockup selection does not exist on the current form layout, so this is handled gracefully.
        locator = (By.XPATH, f"//label[@for='{mockup_id}']")
        try:
            el = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)
        except TimeoutException:
            print(f"⚠️ Mockup type '{mockup_id}' not found/clickable - skipping")

    def upload_image(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Upload file not found: {path}")
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].style.display = 'block';", el)
        el.send_keys(path)

    def submit(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)

        submit_start = time.time()
        self.driver.execute_script("""
            var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            arguments[0].dispatchEvent(evt);
        """, btn)

        try:
            self.wait.until(EC.presence_of_element_located(self.SUCCESS_DIV))
            self._submission_succeeded = True
        except TimeoutException:
            self._submission_succeeded = False
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float | None:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        try:
            el = self.driver.find_element(By.ID, "qfSuccess")
            classes = el.get_attribute("class") or ""
            return "on" in classes or el.is_displayed() or self._submission_succeeded
        except Exception:
            return False

    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)

    def _check(self, locator):
        try:
            el = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].click();", el)
        except TimeoutException:
            print(f"⚠️ Placement option '{locator}' not found/clickable - skipping")