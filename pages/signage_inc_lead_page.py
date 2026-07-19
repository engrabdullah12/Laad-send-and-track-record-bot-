
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SignageIncLeadPage:

    # ── Step 1: Contact ──────────────────────────────────────────────────
    NAME_INPUT  = (By.CSS_SELECTOR, "input#f-name")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input#f-email")
    PHONE_INPUT = (By.CSS_SELECTOR, "input#f-phone")
    FILE_INPUT  = (By.CSS_SELECTOR, "input#file-input")

    CONTINUE_BTN = (By.XPATH, "//button[.//span[@id='btn-next-label']]")

    # ── Step 2: Sign Details ─────────────────────────────────────────────
    INDOOR_BTN  = (By.CSS_SELECTOR, "button#su-indoor")
    OUTDOOR_BTN = (By.CSS_SELECTOR, "button#su-outdoor")

    # Lighting — selected by data-val attribute
    FRONTLIT_BTN   = (By.CSS_SELECTOR, "button[data-field='lighting'][data-val='front-lit']")
    BACKLIT_BTN    = (By.CSS_SELECTOR, "button[data-field='lighting'][data-val='back-lit']")
    FRONTBACK_BTN  = (By.CSS_SELECTOR, "button[data-field='lighting'][data-val='front-back-lit']")
    NOLIGHT_BTN    = (By.CSS_SELECTOR, "button[data-field='lighting'][data-val='no-lighting']")

    # Material — selected by data-val attribute
    ACRYLIC_BTN  = (By.CSS_SELECTOR, "button[data-field='material'][data-val='acrylic']")
    METAL_BTN    = (By.CSS_SELECTOR, "button[data-field='material'][data-val='metal']")
    NOTSURE_BTN  = (By.CSS_SELECTOR, "button[data-field='material'][data-val='not-sure']")

    SUBMIT_BTN = (By.CSS_SELECTOR, "button#btn-submit")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.submission_time_seconds = None

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)

    # ── Step 1 ────────────────────────────────────────────────────────────

    def fill_name(self, value: str):
        self._type(self.NAME_INPUT, value)

    def fill_email(self, value: str):
        self._type(self.EMAIL_INPUT, value)

    def fill_phone(self, value: str):
        self._type(self.PHONE_INPUT, value)

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
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        time.sleep(0.5)

    # ── Step 2 ────────────────────────────────────────────────────────────

    def select_sign_usage(self, indoor=True):
        locator = self.INDOOR_BTN if indoor else self.OUTDOOR_BTN
        self._click_option(locator)

    def select_lighting(self, option: str = "back-lit"):
        """Options: 'front-lit' | 'back-lit' | 'front-back-lit' | 'no-lighting'"""
        locators = {
            "front-lit":      self.FRONTLIT_BTN,
            "back-lit":       self.BACKLIT_BTN,
            "front-back-lit": self.FRONTBACK_BTN,
            "no-lighting":    self.NOLIGHT_BTN,
        }
        if option not in locators:
            raise ValueError(f"Invalid lighting option '{option}'. Choose from: {list(locators)}")
        self._click_option(locators[option])

    def select_material(self, option: str = "not-sure"):
        """Options: 'acrylic' | 'metal' | 'not-sure'"""
        locators = {
            "acrylic":  self.ACRYLIC_BTN,
            "metal":    self.METAL_BTN,
            "not-sure": self.NOTSURE_BTN,
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
            self.wait.until(EC.visibility_of_element_located((By.ID, "q-success")))
        except TimeoutException:
            pass
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        try:
            el = self.driver.find_element(By.ID, "q-success")
            return self.driver.execute_script("""
                var el = arguments[0];
                var s = window.getComputedStyle(el);
                return s.display !== 'none'
                    && s.visibility !== 'hidden'
                    && s.opacity !== '0'
                    && el.offsetHeight > 0;
            """, el)
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