from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

driver.get('http://127.0.0.1:5000/')
time.sleep(1)
driver.execute_script("showPage('ai-interviewer')")
time.sleep(1)

print('Console logs:')
for entry in driver.get_log('browser'):
    print(entry)

html = driver.execute_script("return document.getElementById('page-ai-interviewer').outerHTML")
print('HTML length:', len(html))
print('Class of target:', driver.execute_script("return document.getElementById('page-ai-interviewer').className"))
print('Display style:', driver.execute_script("return window.getComputedStyle(document.getElementById('page-ai-interviewer')).display"))

driver.quit()
