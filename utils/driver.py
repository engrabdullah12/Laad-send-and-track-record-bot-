import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def create_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--enable-logging")
    opts.add_argument("--auto-open-devtools-for-tabs")  
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    if platform.system() == "Windows":
        service = Service(executable_path=r"C:\Users\ic\AppData\Local\Programs\Python\Python312\Scripts\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=opts)
    else:
        driver = webdriver.Chrome(options=opts)
        
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Page.enable", {})
    return driver
