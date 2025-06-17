from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def setup_selenium_driver():
  CHROMEDRIVER_PATH = "C:/chromedriver-win64/chromedriver.exe"
  
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")
  options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
  options.add_argument("--window-size=1280,800")
  options.add_argument("--enable-unsafe-swiftshader")
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('useAutomationExtension', False)
  options.binary_location = r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
  
  service = Service(CHROMEDRIVER_PATH)
  driver = webdriver.Chrome(service=service, options=options)
  driver.set_page_load_timeout(60)
  return driver