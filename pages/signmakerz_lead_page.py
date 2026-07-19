import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SignMakerzLeadPage:

    NAME_INPUT        = (By.XPATH, "//label[contains(., 'Name')]/following::input[1]")
    EMAIL_INPUT       = (By.XPATH, "//label[contains(., 'Email')]/following::input[1]")
    PHONE_INPUT       = (By.XPATH, "//label[contains(., 'Phone')]/following::input[1]")
    DETAILS_TEXTAREA  = (By.XPATH, "//label[contains(., 'Details')]/following::textarea[1]")

    PLACEMENT_INDOOR  = (By.XPATH, "//label[contains(., 'Indoor')]")
    PLACEMENT_OUTDOOR = (By.XPATH, "//label[contains(., 'Outdoor')]")

    FILE_INPUT  = (By.CSS_SELECTOR, "input[type='file']")

    # ✅ FIXED: use class-based selector, more reliable than text matching
    SUBMIT_BTN  = (By.XPATH, "//button[contains(@class, 'submitButton')]")

    # ✅ FIXED: correct ID is "submitSuccess" not "submitSuccess_at_lead"
    SUCCESS_DIV = (By.ID, "submitSuccess")

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

    def select_placements(self, indoor=True, outdoor=False):
        if indoor:
            self._check(self.PLACEMENT_INDOOR)
        if outdoor:
            self._check(self.PLACEMENT_OUTDOOR)

    def select_mockup_types(self, label_text: str):
        # ✅ FIXED: try exact match first, fall back to contains()
        try:
            locator = (By.XPATH, f"//label[normalize-space()='{label_text}']")
            el = self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            try:
                locator = (By.XPATH, f"//label[contains(normalize-space(), '{label_text}')]")
                el = self.wait.until(EC.element_to_be_clickable(locator))
            except TimeoutException as e:
                print(f"Could not select mockup '{label_text}': {e}")
                return
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def upload_image(self, path: str):
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        el.send_keys(path)

    def submit(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)  # ✅ let scroll settle

        submit_start = time.time()
        self.driver.execute_script("""
            var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            arguments[0].dispatchEvent(evt);
        """, btn)

        try:
            # ✅ FIXED: watch for d-none removal, not visibility
            self.wait.until(lambda d: "d-none" not in d.find_element(
                By.ID, "submitSuccess").get_attribute("class")
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
            el = self.driver.find_element(By.ID, "submitSuccess")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    # ── helpers ────────────────────────────────────────────────────────────────

    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)

    def _check(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", el)