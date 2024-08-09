# app.py
import subprocess
import time
import httpx
import easyocr
from playwright.sync_api import sync_playwright
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

pip_install_strings = ['easyocr', 'httpx']

def process_image_with_easyocr(image_url: str):
    # Record the start time before installation
    start_time = time.time()

    # Install EasyOCR and its dependencies
    for package in pip_install_strings:
        subprocess.run(["pip", "install", package], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Record the end time after installation
    end_time = time.time()
    installation_time = end_time - start_time

    stdout = f"Installation time: {installation_time:.2f} seconds\n"
    stderr = ""

    try:
        # Download the image
        with httpx.Client() as client:
            response = client.get(image_url)
            response.raise_for_status()
            image_bytes = response.content

        # Initialize EasyOCR reader (CPU-only)
        reader = easyocr.Reader(['en'], gpu=False)

        # Perform OCR
        result = reader.readtext(image_bytes)

        # Process the results
        recognized_text = [item[1] for item in result]
        stdout += f"OCR completed successfully. Recognized text:\n{recognized_text}"

    except httpx.HTTPStatusError as e:
        stderr = f"HTTP error occurred while downloading the image: {str(e)}"
    except Exception as e:
        stderr = f"Error processing image with EasyOCR: {str(e)}"
    finally:
        # Clean up
        if 'reader' in locals():
            del reader

    return stdout, stderr

def test_playwright(url: str):
    try:
        with sync_playwright() as p:
            browser = p.webkit.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return f"Playwright ran successfully using WebKit. First 1000 characters of content:\n{content[:1000]}"
    except Exception as e:
        return f"Error running Playwright: {str(e)}"

class ImageHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test_image':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('123.PNG', 'rb') as file:
                self.wfile.write(file.read())
        else:
            super().do_GET()

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ImageHandler)
    print(f"Serving image at http://localhost:{port}/test_image")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start the local server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait a moment for the server to start
    time.sleep(1)

    # Test call to OCR function
    local_image_url = "http://localhost:8000/test_image"
    stdout, stderr = process_image_with_easyocr(local_image_url)
    
    print("OCR Output:")
    print(stdout)
    
    if stderr:
        print("Errors:")
        print(stderr)

    # Commented out Playwright test
    # url = "https://google.com"
    # result = test_playwright(url)
    # print(result)