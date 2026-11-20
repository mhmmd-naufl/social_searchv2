"""Inisialisasi Selenium WebDriver.

Bisa dipakai di Windows (Brave + chromedriver lokal) maupun di container
Linux (Chromium dari apt). Semua path bisa ditimpa lewat environment variable.
"""

import os
import platform

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

IS_WINDOWS = platform.system() == "Windows"

DEFAULT_DRIVER = (
    "C:/chromedriver-win64/chromedriver.exe"
    if IS_WINDOWS
    else "/usr/bin/chromedriver"
)
DEFAULT_BROWSER = (
    r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    if IS_WINDOWS
    else "/usr/bin/chromium"
)


def setup_selenium_driver():
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or DEFAULT_DRIVER
    browser_binary = os.getenv("BROWSER_BINARY") or DEFAULT_BROWSER

    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    options.add_argument("--window-size=1280,800")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.path.isfile(browser_binary):
        options.binary_location = browser_binary

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver
