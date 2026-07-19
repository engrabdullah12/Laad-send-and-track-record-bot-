import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("PAGESPEED_API_KEY") 
import requests

def fetch_pagespeed_score(url: str, strategy: str = "desktop", timeout: int = 150) -> int:
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {"url": url, "key": API_KEY, "strategy": strategy}
    resp = requests.get(endpoint, params=params, timeout=timeout)
    if resp.status_code == 429:
        print(f"⚠️ Rate limit hit for {url} ({strategy}). Skipping.")
        return -1
    resp.raise_for_status()
    data = resp.json()
    score = data["lighthouseResult"]["categories"]["performance"]["score"]
    return int(score * 100)

def get_pagespeed_safe(url: str, retries: int = 2, delay: float = 5.0) -> tuple[str, str]:
    desktop, mobile = "Timeout", "Timeout"  # ✅ default instead of ""
    
    for i in range(retries + 1):
        try:
            result = fetch_pagespeed_score(url, strategy="desktop", timeout=45)
            if result == -1:
                desktop = "Rate Limited"  # ✅ clearer than -1
            else:
                desktop = str(result)
            break
        except Exception as e:
            print(f"[Retry {i+1}/{retries+1}] Desktop failed: {e}")
            if i < retries:
                time.sleep(delay)

    for i in range(retries + 1):
        try:
            result = fetch_pagespeed_score(url, strategy="mobile", timeout=45)
            if result == -1:
                mobile = "Rate Limited"  # ✅ clearer than -1
            else:
                mobile = str(result)
            break
        except Exception as e:
            print(f"[Retry {i+1}/{retries+1}] Mobile failed: {e}")
            if i < retries:
                time.sleep(delay)

    return desktop, mobile