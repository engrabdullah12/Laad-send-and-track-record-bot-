import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os



class SignmakersNetLeadPage:
    SUCCESS_CONTAINER = (By.ID, "submitSuccess")

    NAME_INPUT = (By.ID, "name")
    EMAIL_INPUT = (By.ID, "email")
    PHONE_INPUT = (By.ID, "phone_number")
    DETAILS_TEXTAREA = (By.ID, "details")
    BUSINESS_NAME_INPUT = (By.ID, "businessName")
    IMAGE_URL_INPUT = (By.ID, "imageUrl")

    PLACEMENT_INDOOR = (By.ID, "Indoor")
    PLACEMENT_OUTDOOR = (By.ID, "Outdoor")

    FILE_INPUT = (By.ID, "fileInput")

    SUBMIT_BTN = (By.XPATH, "//button[contains(@class,'submitButton')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.submission_time_seconds = None  # ← add this

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

    def fill_business_name(self, value: str):
        self._js_fill("businessName", value)

    def fill_hidden_fields(self):
        self._js_fill("imageUrl", "CodeBlue.png")

    def select_placements(self, indoor=True, outdoor=False):
        if indoor:
            self._check(self.PLACEMENT_INDOOR)
        if outdoor:
            self._check(self.PLACEMENT_OUTDOOR)

    def select_mockup_types(self, label_text: str):
        locator = (By.XPATH, f"//label[.//span[contains(text(), '{label_text}')]]")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", el)

    def upload_image(self, path: str):
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].removeAttribute('hidden');", el)
        el.send_keys(path)
        self.wait.until(lambda d: el.get_attribute("value") != "")


    def submit(self):
      btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
      self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)

      submit_start = time.time()

      self.driver.execute_script("""
        var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
        arguments[0].dispatchEvent(evt);
    """, btn)

      try:
         self.wait.until(EC.visibility_of_element_located(self.SUCCESS_CONTAINER))
      except TimeoutException:
        pass
      finally:
        self.submission_time_seconds = round(time.time() - submit_start, 2)  # ← stops timer

    def get_submission_duration(self) -> float | None:  # <<-- added new
     return self.submission_time_seconds 

    def success_visible(self) -> bool:
        try:
            self.wait.until(EC.visibility_of_element_located(self.SUCCESS_CONTAINER))
            return True
        except TimeoutException:
            return False

    # 🔧 Helpers
    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        try:
            el.clear()
            el.send_keys(value)
        except:
            self.driver.execute_script("arguments[0].value = arguments[1];", el, value)
        self.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, el)

    def _check(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", el)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el)

    def _js_fill(self, element_id: str, value: str):
        self.driver.execute_script(f"""
            var el = document.getElementById('{element_id}');
            if (el) {{
                el.value = arguments[0];
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        """, value)
