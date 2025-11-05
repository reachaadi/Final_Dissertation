from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from openpyxl import load_workbook
import os

# Excel and driver setup
base_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(base_dir, "TestData", "Credentials.xlsx")
report_file = os.path.join(base_dir, "HTML_Reports", "CredentialsTest.html")
screenshots_dir = os.path.join(base_dir, "Screenshots")

# Ensure output directories exist
os.makedirs(os.path.dirname(report_file), exist_ok=True)
os.makedirs(screenshots_dir, exist_ok=True)

workbook = load_workbook(filename=file_path)
sheet = workbook.active

import tempfile
from selenium.webdriver.chrome.options import Options

temp_dir = tempfile.mkdtemp()
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={temp_dir}")
driver = webdriver.Chrome(options=chrome_options)

driver.maximize_window()
time.sleep(1)

# Start HTML report
with open(report_file, "w") as report:
    report.write(
        """
    <html>
    <head>
        <title>Credentials Test Report</title>
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
    <h2>Credentials Test Execution Report</h2>
    <table>
        <tr>
            <th>Scenario</th>
            <th>Status</th>
            <th>Expected Result</th>
            <th>Actual Result</th>
            <th>Screenshot</th>
        </tr>
    """
    )

try:
    for row in sheet.iter_rows(min_row=2, values_only=True):
        scenario, username, password, expected_result = row
        print(f"Running test for {scenario}: username={username} password={password}")

        driver.get("https://practicetestautomation.com/practice-test-login/")

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(password)
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
        submit_button.click()

        # Wait for either success header or error message
        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "error")),
                EC.presence_of_element_located((By.XPATH, "//h1")),
            )
        )

        test_status = "Fail"
        actual_result = "No relevant message"

        # Dynamically check expected result from the D column
        found_message = ""
        try:
            error_element = driver.find_element(By.ID, "error")
            found_message = error_element.text
        except Exception:
            try:
                success_element = driver.find_element(By.XPATH, "//h1")
                found_message = success_element.text
            except Exception:
                found_message = "No relevant message"

        # Assert dynamically based on expected_result from Excel
        if expected_result.lower() in found_message.lower():
            test_status = "Pass"
            actual_result = found_message
        else:
            actual_result = found_message

        screenshot_file = os.path.join(screenshots_dir, f"{scenario.replace(' ', '_')}.png")
        driver.save_screenshot(screenshot_file)

        with open(report_file, "a") as report:
            report.write(
                f"<tr><td>{scenario}</td><td>{test_status}</td><td>{expected_result}</td><td>{actual_result}</td>"
                f"<td><a href='{screenshot_file}' target='_blank'>"
                f"<img src='{screenshot_file}' height='50'></a></td></tr>"
            )

        time.sleep(1)

finally:
    driver.quit()
    with open(report_file, "a") as report:
        report.write("</table></body></html>")

print(f"Test report generated: {report_file}")
