import os
import re
import time
from flask import Flask, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Configure Chrome options for Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Required for Render
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = os.getenv("CHROME_BIN")  # Set custom Chrome path
driver_path = os.getenv("CHROMEDRIVER_PATH")  # Set custom Chromedriver path


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    redgifs_url = request.form["url"]

    # Extract video ID from the URL
    match = re.search(r"redgifs\.com/watch/(\w+)", redgifs_url)
    if not match:
        return "Invalid RedGifs URL", 400
    video_id = match.group(1)

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    driver.get(redgifs_url)
    time.sleep(5)  # Wait for the page to load

    # Extract the .m4s video URL
    video_url = None
    logs = driver.get_log("performance")
    for entry in logs:
        log = entry["message"]
        match = re.search(r'"https://files\.redgifs\.com/.*?\.m4s"', log)
        if match:
            video_url = match.group(0).strip('"')
            break

    driver.quit()

    if not video_url:
        return "Unable to retrieve video URL", 404

    # Redirect to the video URL for direct download
    return redirect(video_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
