"""
Builds a configured Selenium Chrome WebDriver.

Handles:
  - Applying the US proxy from config.py at the ChromeOptions level
  - Authenticated proxies (Chrome's --proxy-server flag doesn't support
    embedded user:pass@ credentials, so we generate a tiny unpacked
    Chrome extension that supplies them via the proxy auth API)
"""

import os
import string
import zipfile
import tempfile

import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config import ProxyConfig


_PROXY_AUTH_EXTENSION_MANIFEST = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Proxy Auth",
    "permissions": [
        "proxy", "tabs", "unlimitedStorage", "storage",
        "<all_urls>", "webRequest", "webRequestBlocking"
    ],
    "background": {"scripts": ["background.js"]},
    "minimum_chrome_version": "22.0.0"
}
"""

_PROXY_AUTH_EXTENSION_BG = string.Template("""
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "$scheme",
            host: "$host",
            port: parseInt($port)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

chrome.webRequest.onAuthRequired.addListener(
    function(details) {
        return {
            authCredentials: {username: "$username", password: "$password"}
        };
    },
    {urls: ["<all_urls>"]},
    ["blocking"]
);
""")


def _build_proxy_auth_extension():
    """Creates a temp .zip Chrome extension that injects proxy credentials."""
    manifest = _PROXY_AUTH_EXTENSION_MANIFEST
    background = _PROXY_AUTH_EXTENSION_BG.substitute(
        scheme=ProxyConfig.scheme,
        host=ProxyConfig.host,
        port=ProxyConfig.port,
        username=ProxyConfig.username,
        password=ProxyConfig.password,
    )

    fd, path = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as zp:
        zp.writestr("manifest.json", manifest)
        zp.writestr("background.js", background)
    return path


def get_chrome_options(headless: bool = True) -> Options:
    import os
    if os.environ.get("GITHUB_ACTIONS") == "true":
        headless = True
    chrome_options = Options()

    use_auth_proxy = ProxyConfig.enabled and ProxyConfig.is_authenticated()

    # IMPORTANT: Chrome's legacy/old headless mode (--headless or
    # --headless=old) does NOT support extensions at all - they silently
    # fail to load, which silently breaks the proxy-auth extension below
    # with no error (traffic just goes out unproxied). Only the newer
    # --headless=new mode (Chrome 109+) supports extensions, so always use
    # that, regardless of whether an auth proxy is in play.
    if headless:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Enable Chrome's performance/network log so driver.get_log("performance")
    # works - this is required by find_airtable_record() and conftest.py's
    # log-clearing fixture to detect the lead submission API call. This is
    # NOT the timing/PageSpeed feature that was removed - it's how the bot
    # captures the network request itself, not how long it took.
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    if ProxyConfig.enabled:
        ProxyConfig.validate()

        if use_auth_proxy:
            # Authenticated proxy: credentials via extension, not the CLI flag.
            ext_path = _build_proxy_auth_extension()
            chrome_options.add_extension(ext_path)
        else:
            # Unauthenticated proxy: simple CLI flag works fine.
            chrome_options.add_argument(
                f"--proxy-server={ProxyConfig.as_chrome_arg()}"
            )

    return chrome_options


def get_driver(headless: bool = True) -> webdriver.Chrome:
    """Returns a ready-to-use Chrome WebDriver with the proxy applied."""
    options = get_chrome_options(headless=headless)
    if platform.system() == "Windows":
        service = Service(executable_path=r"C:\Users\ic\AppData\Local\Programs\Python\Python312\Scripts\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    return driver
