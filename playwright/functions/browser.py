import subprocess
import time
import base64
import os
import hashlib
import random

pip_install_strings = ['playwright']

def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def take_screenshot(url: str):
    from playwright.sync_api import sync_playwright
    
    # Record the start time before installation
    start_time = time.time()
    
    # Install Playwright browser binaries using subprocess
    # Suppress the output of installing dependencies
    subprocess.run(["playwright", "install-deps"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Suppress the output of installing Chromium
    subprocess.run(["playwright", "install", "chromium"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Record the end time after installation
    end_time = time.time()
    installation_time = end_time - start_time

    stdout = f"Installation time: {installation_time:.2f} seconds\n"
    stderr = ""
    screenshot_base64 = ""

    try:
        with sync_playwright() as p:
            try:
                # Generate a random hash for the filename
                random_hash = hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()
                filename = f"{random_hash}.jpg"

                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                # Save as JPG
                page.screenshot(path=filename, type='jpeg', quality=80)
                browser.close()
                
                # Read the screenshot file and encode it to base64
                with open(filename, "rb") as image_file:
                    screenshot_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                
                stdout += f"Screenshot taken successfully and saved as {filename}"
                
                # Remove the local file after encoding
                os.remove(filename)
            except Exception as e:
                stderr = f"Failed to launch browser or take screenshot: {str(e)}"
    except Exception as e:
        stderr = f"Error running Playwright: {str(e)}"

    return {
        "stdout": stdout,
        "stderr": stderr,
        "screenshot_base64": screenshot_base64,
        "filename": filename  # Return the generated filename
    }