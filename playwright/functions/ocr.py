import subprocess
import time
import base64
import os
import random
import string
from io import BytesIO
from PIL import Image

pip_install_strings = ['easyocr', 'Pillow']

def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def process_image_with_easyocr(screenshot_base64: str):
    # Record the start time before installation
    start_time = time.time()

    # Install EasyOCR and Pillow
    for package in pip_install_strings:
        subprocess.run(["pip", "install", package], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Record the end time after installation
    end_time = time.time()
    installation_time = end_time - start_time

    stdout = f"Installation time: {installation_time:.2f} seconds\n"
    stderr = ""

    import easyocr
    from PIL import Image
    try:
        # Decode the base64 string to image bytes
        image_bytes = base64.b64decode(screenshot_base64)

        # Generate a random filename
        random_filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + ".png"

        # Convert bytes to an image and save it
        image = Image.open(BytesIO(image_bytes))
        image.save(random_filename)

        # Initialize EasyOCR reader (CPU-only)
        reader = easyocr.Reader(['en'], gpu=False)

        # Perform OCR on the saved image
        result = reader.readtext(random_filename)

        # Process the results
        recognized_text = [item[1] for item in result]
        stdout += f"OCR completed successfully. Recognized text:\n{recognized_text}"

    except Exception as e:
        stderr = f"Error processing image with EasyOCR: {str(e)}"

    return stdout, stderr
