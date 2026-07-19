from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BestBusinessSignsLeadPage:
    # Inputs
    NAME_INPUT = (By.ID, "name")
    EMAIL_INPUT = (By.ID, "email")
    COMPANY_INPUT = (By.ID, "company")
    LEAD_ADDED_BY_INPUT = (By.ID, "leadBy")

    # Hidden Airtable-bound fields
    BUSINESS_NAME_INPUT = (By.ID, "businessName")
    IMAGE_URL_INPUT = (By.ID, "imageUrl")

    # Custom Type (radio buttons)
    CUSTOM_TYPE_NEW = (By.ID, "paid")
    CUSTOM_TYPE_PARTIAL = (By.ID, "partial")

    # Placements
    PLACEMENT_INDOOR = (By.ID, "Indoor")
    PLACEMENT_OUTDOOR = (By.ID, "Outdoor")

    # Preferences
    PREFERENCE_FRONTLIT = (By.ID, "Frontlit")
    PREFERENCE_BACKLIT = (By.ID, "Backlit")
    PREFERENCE_NOLIGHT = (By.ID, "NoLight")

    # Size
    SIZE_RECOMMENDED = (By.ID, "Recommended")
    SIZE_CUSTOM = (By.ID, "Custom")

    # Services
    SERVICE_INSTALLATION = (By.ID, "Installation")
    SERVICE_PERMITS = (By.ID, "SignPermits")

    # Mockups
    MOCKUP_3D_BLADE = (By.CSS_SELECTOR, "label[for='D_Blade']")
    MOCKUP_METAL_BACKLIT = (By.CSS_SELECTOR, "label[for='Metal_Backlit']")
    MOCKUP_BLADE_SIGN = (By.CSS_SELECTOR, "label[for='Blade_Sign']")

    # File upload
    FILE_INPUT = (By.ID, "image")

    # Details
    DETAILS_TEXTAREA = (By.ID, "detail")

    # Submit
    SUBMIT_BTN = (By.ID, "submitbtnn")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.NAME_INPUT))

    # Fillers
    def fill_name(self, value: str): self._type(self.NAME_INPUT, value)
    def fill_email(self, value: str): self._type(self.EMAIL_INPUT, value)
    def fill_company(self, value: str): self._type(self.COMPANY_INPUT, value)
    def fill_lead_added_by(self, value: str): self._type(self.LEAD_ADDED_BY_INPUT, value)
    def fill_details(self, value: str): self._type(self.DETAILS_TEXTAREA, value)

    def fill_business_name(self, value: str):
        self._type(self.BUSINESS_NAME_INPUT, value)

    def fill_hidden_fields(self):
        self._type(self.IMAGE_URL_INPUT, "CodeBlue.png")

    # Selectors
    def select_custom_type(self, partial=False):
        self._check(self.CUSTOM_TYPE_PARTIAL if partial else self.CUSTOM_TYPE_NEW)

    def select_placements(self):
        self._check(self.PLACEMENT_INDOOR)
        self._check(self.PLACEMENT_OUTDOOR)

    def select_preferences(self):
        self._check(self.PREFERENCE_FRONTLIT)

    def select_size(self, custom=False):
        self._check(self.SIZE_CUSTOM if custom else self.SIZE_RECOMMENDED)

    def select_services(self):
        self._check(self.SERVICE_INSTALLATION)
        self._check(self.SERVICE_PERMITS)

    def select_mockups(self):
        self._check(self.MOCKUP_3D_BLADE)
        self._check(self.MOCKUP_METAL_BACKLIT)
        self._check(self.MOCKUP_BLADE_SIGN)

    def upload_image(self, path: str):
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].removeAttribute('hidden'); arguments[0].style.display = 'block';", el)
        el.send_keys(path)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el)

    def submit(self):
        btn = self.wait.until(EC.presence_of_element_located(self.SUBMIT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)

    def success_visible(self) -> bool:
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "ThankYou")))
            return True
        except:
            return False

    # Helpers
    def _type(self, locator, value: str):
        el = self.wait.until(EC.presence_of_element_located(locator))
        try:
            el.clear()
            el.send_keys(value)
        except:
            self.driver.execute_script("arguments[0].value = arguments[1];", el, value)
        self.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, el, value)

    def _check(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", el)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el)
