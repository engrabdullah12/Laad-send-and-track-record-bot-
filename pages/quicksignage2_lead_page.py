import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class QuickSignage2LeadPage:
    NAME_INPUT    = (By.CSS_SELECTOR, "input#f-name")
    EMAIL_INPUT   = (By.CSS_SELECTOR, "input#f-email")
    PHONE_INPUT   = (By.CSS_SELECTOR, "input#f-phone")
    WEBSITE_INPUT = (By.CSS_SELECTOR, "input#f-web")
    FILE_INPUT    = (By.CSS_SELECTOR, "input#file-input")
    CONTINUE_BTN  = (By.XPATH, "//button[contains(., 'CONTINUE') or contains(., 'Continue')]")
    INDOOR_BTN    = (By.ID, "pl-indoor")
    OUTDOOR_BTN   = (By.ID, "pl-outdoor")

    FRONTLIT_BTN  = (By.ID, "lt-frontlit")
    BACKLIT_BTN   = (By.ID, "lt-backlit")
    FRONTBACK_BTN = (By.ID, "lt-frontback")
    NOLIGHT_BTN   = (By.ID, "lt-nolight")

    ACRYLIC_BTN   = (By.ID, "mat-acrylic")
    METAL_BTN     = (By.ID, "mat-metal")
    NOTSURE_BTN   = (By.ID, "mat-notsure")

    SUBMIT_BTN    = (By.ID, "btn-submit")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.submission_time_seconds = None
        self._submission_succeeded = False
    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)

    def fill_name(self, value: str):
        self._type(self.NAME_INPUT, value)

    def fill_email(self, value: str):
        self._type(self.EMAIL_INPUT, value)

    def fill_phone(self, value: str):
        self._type(self.PHONE_INPUT, value)

    def fill_website(self, value: str):
        try:
            self._type(self.WEBSITE_INPUT, value)
        except TimeoutException:
            print("⚠️ Website URL input not found or not visible - skipping")

    def upload_image(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Upload file not found: {path}")
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].style.display = 'block';", el)
        el.send_keys(path)

    def click_continue(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.presence_of_element_located(self.SUBMIT_BTN))
        time.sleep(0.5)

    def select_sign_usage(self, indoor=True):
        locator = self.INDOOR_BTN if indoor else self.OUTDOOR_BTN
        self._click_option(locator)

    def select_lighting(self, option: str = "backlit"):
        """Options: 'frontlit', 'backlit', 'frontback', 'nolight'"""
        locators = {
            "frontlit":  self.FRONTLIT_BTN,
            "backlit":   self.BACKLIT_BTN,
            "frontback": self.FRONTBACK_BTN,
            "nolight":   self.NOLIGHT_BTN,
        }
        if option not in locators:
            raise ValueError(f"Invalid lighting option '{option}'. Choose from: {list(locators)}")
        self._click_option(locators[option])

    def select_material(self, option: str = "notsure"):
        """Options: 'acrylic', 'metal', 'notsure'"""
        locators = {
            "acrylic": self.ACRYLIC_BTN,
            "metal":   self.METAL_BTN,
            "notsure": self.NOTSURE_BTN,
        }
        if option not in locators:
            raise ValueError(f"Invalid material option '{option}'. Choose from: {list(locators)}")
        self._click_option(locators[option])

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
            WebDriverWait(self.driver, 15).until(
                lambda d: d.find_elements(By.ID, "q-success") or "thanks-for-response" in d.current_url
            )
            self._submission_succeeded = True
        except TimeoutException:
            self._submission_succeeded = False
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        if "thanks-for-response" in self.driver.current_url:
            return True
        try:
            el = self.driver.find_element(By.ID, "q-success")
            return el.is_displayed() or self._submission_succeeded
        except Exception:
            return False
    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)

    def _click_option(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)