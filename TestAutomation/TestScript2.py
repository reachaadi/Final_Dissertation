from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from openpyxl import load_workbook

# Excel and driver setup
base_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(base_dir, "TestData", "LinkTest.xlsx")
report_file = os.path.join(base_dir, "HTML_Reports", "LinkTest.html")
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
        <title>Link Test Report</title>
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
    <h2>Link Test Execution Report</h2>
    <table>
        <tr>
            <th>Scenario</th>
            <th>Screen</th>
            <th>Expected Result</th>
            <th>Status</th>
            <th>Screenshot1</th>
            <th>Screenshot2</th>
            <th>Screenshot3</th>
        </tr>
    """
    )

try:
    for row in sheet.iter_rows(min_row=2, values_only=True):
        print(f"Value of row is: {row}")
        scenario, screen, expected_result = row
        print(f"Running {scenario}: Screen={screen}, Expected={expected_result}")

        # Step 1: Go to website
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

        # Screenshot 1: After clicking Submit (login)
        screenshot_submit = os.path.join(screenshots_dir, f"{scenario.replace(' ', '_')}_submit.png")
        driver.save_screenshot(screenshot_submit)

        # Step 2: Click the PRACTICE menu
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "PRACTICE"))
        ).click()
        time.sleep(1)

        # Screenshot 2: Scroll until the link from "Screen" column is visible
        try:
            link_elem = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, screen))
            )
            driver.execute_script("arguments[0].scrollIntoView();", link_elem)
            screenshot_link = os.path.join(screenshots_dir, f"{scenario.replace(' ', '_')}_link.png")
            driver.save_screenshot(screenshot_link)
        except Exception as e:
            screenshot_link = os.path.join(
                screenshots_dir, f"{scenario.replace(' ', '_')}_link_ERROR.png"
            )
            driver.save_screenshot(screenshot_link)
            print(f"FAIL: Could not scroll to '{screen}'. Exception: {e}")

        time.sleep(1)
        # Step 3: Click the expected link
        try:
            link_elem.click()
            print(f"PASS: Clicked the link '{screen}'")
        except Exception as e:
            print(f"FAIL: Could not click the link '{screen}'. Exception: {e}")

        # Screenshot 3: After clicking link, scroll to expected <h1>
        status = "Fail"
        screenshot_header = os.path.join(screenshots_dir, f"{scenario.replace(' ', '_')}_header.png")
        try:
            expected_label = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//h1[contains(text(), '{expected_result}')]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView();", expected_label)
            driver.save_screenshot(screenshot_header)
            status = "Pass"
        except Exception as e:
            driver.save_screenshot(screenshot_header)
            print(f"Check failed: {e}")

        # Write result to HTML report
        with open(report_file, "a") as report:
            report.write(
                f"<tr><td>{scenario}</td><td>{screen}</td><td>{expected_result}</td><td>{status}</td>"
                f"<td><a href='{screenshot_submit}' target='_blank'><img src='{screenshot_submit}' height='50'></a></td>"
                f"<td><a href='{screenshot_link}' target='_blank'><img src='{screenshot_link}' height='50'></a></td>"
                f"<td><a href='{screenshot_header}' target='_blank'><img src='{screenshot_header}' height='50'></a></td></tr>"
            )
        time.sleep(2)

finally:
    driver.quit()
    with open(report_file, "a") as report:
        report.write("</table></body></html>")

print(f"Test report generated: {report_file}")
