import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class QuickSignageLeadPage:

    NAME_INPUT  = (By.CSS_SELECTOR, "input#qf-name")
    PHONE_INPUT = (By.CSS_SELECTOR, "input#qf-phone")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input#qf-email")
    FILE_INPUT  = (By.CSS_SELECTOR, "input#qf-logo")

    SUBMIT_BTN  = (By.CSS_SELECTOR, "button#qfSubmit")
    SUCCESS_DIV = (By.ID, "qfSuccess")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.submission_time_seconds = None

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

    def upload_image(self, path: str):
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
            self.wait.until(lambda d: "on" in d.find_element(
                By.ID, "qfSuccess").get_attribute("class")
            )
        except TimeoutException:
            pass
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float | None:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        try:
            el = self.driver.find_element(By.ID, "qfSuccess")
            return "on" in el.get_attribute("class")
        except Exception:
            return False

    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)