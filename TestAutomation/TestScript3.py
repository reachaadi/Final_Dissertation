from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from openpyxl import load_workbook

# Excel and driver setup
base_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(base_dir, "TestData", "VerifyRadioButton.xlsx")
report_file = os.path.join(base_dir, "HTML_Reports", "VerifyRadioButtonReport.html")
screenshots_dir = os.path.join(base_dir, "Screenshots")

# Ensure output directories exist
os.makedirs(os.path.dirname(report_file), exist_ok=True)
os.makedirs(screenshots_dir, exist_ok=True)

workbook = load_workbook(filename=file_path)
sheet = workbook.active

from selenium.webdriver.chrome.options import Options

# ...existing code...
# driver = webdriver.Chrome()
options = Options()
# Use modern headless mode; fallback to "--headless" if needed for your Chrome version
options.add_argument("--headless=new")
# Ensure a consistent viewport for screenshots in headless
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

driver.maximize_window()
time.sleep(1)

# Start HTML report
with open(report_file, "w") as report:
    report.write(
        """
    <html>
    <head>
        <title>Radio Button Test Report</title>
        <style>
            body {
                background-color: #f8fafd; /* Soft white */
            }
            h2 {
                text-align: center;
                color: #26547c; /* Deep blue */
                font-size: 2.2em;
                margin-bottom: 30px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }
            table {
                margin-left: auto;
                margin-right: auto;
                border-collapse: collapse;
                border: 3px solid #5a9bd3; /* Thicker blue border */
                 font-size: 1.1em; /* Slightly smaller table font */
                 width: 60%; /* Reduce overall table width */
            }
            th, td {
                padding: 11px 15px;
                text-align: center;
                border: 1.5px solid #5a9bd3; /* Thicker inner borders */
            }
            th {
                background-color: #5a9bd3; /* Table header background */
                color: #fff;
                font-size: 1.2em;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #eaf1fb; /* Alt row color */
            }
        </style>
    </head>
    <body>
    <h2>Radio Button Test Execution Report</h2>
    <table>
        <tr>
            <th>Scenario</th>
            <th>Language</th>
            <th>Button</th>
            <th>Expected Result</th>
            <th>Status</th>
            <th>Screenshot(RadioButton)</th>
        </tr>
    """
    )

try:
    # Step 1: Go to login page, login as student
    driver.get("https://practicetestautomation.com/practice-test-login/")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.clear()
    username_field.send_keys("student")
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.clear()
    password_field.send_keys("Password123")
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
    submit_button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "PRACTICE")))

    # Step 2: Click the PRACTICE menu
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "PRACTICE"))).click()
    time.sleep(1)

    # Step 3: Click "Test Table"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Test Table"))).click()
    time.sleep(2)

    # Step 4: For each relevant row in Excel, validate Java RadioButton selection
    for row in sheet.iter_rows(min_row=2, values_only=True):
        scenario, language, button, expected_result = row
        status = "Fail"
        screenshot_radio = ""
        print(f"Running {scenario}: Language={language}, Button={button}, Expected={expected_result}")

        try:
            # Locate Java radio button
            java_radio = driver.find_element(
                By.XPATH,
                "//input[@type='radio' and (../label[contains(text(),'Java')] or @value='Java')]",
            )
            # Only proceed for rows that require Java RadioButton to be checked
            if language == "Java" and button == "RadioButton" and expected_result == "RadioButton":
                if not java_radio.is_selected():
                    java_radio.click()
                # Scroll into view before screenshot
                driver.execute_script("arguments[0].scrollIntoView();", java_radio)
                time.sleep(1)
                screenshot_radio = os.path.join(
                    screenshots_dir, f"{scenario.replace(' ', '_')}_radio.png"
                )
                driver.save_screenshot(screenshot_radio)
                print("PASS: Java radio button selected and screenshot taken.")
                status = "Pass"
            else:
                # For all other scenarios, click Java radio button and take fail screenshot
                driver.execute_script("arguments[0].scrollIntoView();", java_radio)
                time.sleep(1)
                screenshot_radio = os.path.join(
                    screenshots_dir, f"{scenario.replace(' ', '_')}_radio_FAIL.png"
                )
                driver.save_screenshot(screenshot_radio)
                status = "Fail"
        except Exception as e:
            screenshot_radio = os.path.join(
                screenshots_dir, f"{scenario.replace(' ', '_')}_radio_ERROR.png"
            )
            driver.save_screenshot(screenshot_radio)
            print(f"FAIL: Could not verify/select Java radio button. Exception: {e}")
            status = "Fail"

        # Write result to HTML report
        with open(report_file, "a") as report:
            report.write(
                f"<tr><td>{scenario}</td><td>{language}</td><td>{button}</td><td>{expected_result}</td><td>{status}</td>"
                f"<td><a href='{screenshot_radio}' target='_blank'><img src='{screenshot_radio}' height='50'></a></td></tr>"
            )
        time.sleep(1)

finally:
    driver.quit()
    with open(report_file, "a") as report:
        report.write("</table></body></html>")

print(f"Test report generated: {report_file}")
