import os
import re
import time
import requests
from flask import Flask, request, render_template, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = os.getenv("CHROME_BIN")  # Set custom Chrome path
driver = webdriver.Chrome(
    executable_path=os.getenv("CHROMEDRIVER_PATH"), options=chrome_options
)


# Route to render the home page with an input form
@app.route("/")
def home():
    return render_template("index.html")


# Route to process the URL and fetch the video
@app.route("/download", methods=["POST"])
def download():
    redgifs_url = request.form["url"]

    # Extract video ID from the URL
    match = re.search(r"redgifs\.com/watch/(\w+)", redgifs_url)
    if not match:
        return "Invalid RedGifs URL", 400
    video_id = match.group(1)

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)
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

    # Download the video
    response = requests.get(video_url, stream=True)
    video_filename = f"{video_id}.mp4"
    with open(video_filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    # Serve the downloaded file as a downloadable link
    return send_file(video_filename, as_attachment=True)


# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
