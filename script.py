# Installed libraries using pip: Pillow, requests, playwright, pixelmatch
# .\.venv\Scripts\activate
# Set-ExecutionPolicy unrestricted -Scope Process

import sys
import os
import requests
import subprocess
import shutil
import pixelmatch
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
from io import BytesIO
from urllib.parse import urlparse

baseline_folder = "Baseline"

def validate_url(url):
    """
    Validate the structure of a URL.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    parsed_url = urlparse(url) # Parse the URL using urlparse
    if not all([parsed_url.scheme, parsed_url.netloc]): # Check if both scheme and netloc are present in the parsed URL
        return False
    return True # If both scheme and netloc are present, the URL is considered valid

def make_get_request(url):
    """
    Make a GET request to the provided URL.

    Args:
        url (str): The URL to make the GET request to.

    Raises:
        requests.HTTPError: If the HTTP request fails due to a non-2xx status code.
        Exception: If any other exception occurs during the request.
    """
    try:
        response = requests.get(url)  # Make the GET request
        response.raise_for_status()  # Check if the request was successful
    except requests.HTTPError as e:
        # If an HTTP error occurs, print a message with the URL, status code, and exception
        print(f"GET request to '{url}' failed with status code {e.response.status_code}: {e}")
        raise
    except Exception as e:
        # If any other exception occurs, print a generic error message
        print(f"An error occurred during the GET request: {e}")
        raise  # Raise the exception again to propagate it to the caller

def ensure_folder_exists_otherwise_create(folder):
    """
    Ensure that the folder exists in the current directory.
    If it doesn't exist, create it.
    """
    if not os.path.exists(folder):
        os.makedirs(baseline_folder)

def image_exists_in_baseline(image_name):
    """
    Check if an image with the given name exists in the 'Baseline' folder.

    Args:
        image_name (str): The name of the image to check.

    Returns:
        bool: True if the image exists, False otherwise.
    """
    image_path = os.path.join(baseline_folder, image_name)
    return os.path.exists(image_path)

def load_baseline_image(image_name):
    """
    Load the baseline image with the given name from the 'Baseline' folder.

    Args:
        image_name (str): The name of the image to load.

    Returns:
        Image object: The loaded baseline image.

    Raises:
        IOError: If there is an error loading the image file.
        ValueError: If the image file format is not supported.
        RuntimeError: If the image file is corrupted or contains invalid data.
    """

    image_path = os.path.join(baseline_folder, image_name)

    try:
        baseline_image = Image.open(image_path) # Attempt to open and load the image

        # Additional checks on the loaded image
        if not baseline_image.format:
            raise ValueError("Image format is not supported.")
        # Add more checks if necessary

        return baseline_image
    except IOError as e:
        raise IOError(f"Error loading image '{image_name}': {e}")
    except ValueError as e:
        raise ValueError(f"Invalid image format for '{image_name}': {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing image '{image_name}': {e}")


def take_screenshot(url, viewport_size=None):
    """
    Take a screenshot of the specified URL.

    Args:
        url (str): The URL to take the screenshot of.
        viewport_size (dict): Optional. The size of the viewport in pixels.
            Example: {'width': 800, 'height': 600}

    Returns:
        bytes: The screenshot data.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Set viewport size if provided
        if viewport_size:
            page.set_viewport_size(viewport_size)

        # Navigate to the URL
        page.goto(url)

        # Take screenshot
        screenshot_buffer = page.screenshot()

        browser.close()

        return screenshot_buffer

def save_screenshot_to_baseline(image_buffer, image_name):
    """
    Save the screenshot to the 'Baseline' folder with the given name.

    Args:
        image_buffer (bytes): The screenshot data.
        image_name (str): The name to save the screenshot with.
    """
    image_path = os.path.join(baseline_folder, image_name)
    with open(image_path, "wb") as f:
        f.write(image_buffer)

    print(f"Screenshot saved in 'Baseline' folder as {image_name}")

def process_screenshot_buffer(screenshot_buffer):
    """
    Process a screenshot buffer and return the corresponding PIL.Image object.

    Args:
        screenshot_buffer (bytes): The screenshot buffer to process.

    Returns:
        PIL.Image or None: The processed screenshot image if successful, else None.
    """
    try:
        # Open the image using BytesIO
        screenshot_image = Image.open(BytesIO(screenshot_buffer))
        return screenshot_image
    except IOError as e:
        # Handle IOError, which occurs when the image buffer is invalid
        print(f"IOError occurred while opening the image: {e}")
        return None
    except Image.DecompressionBombError as e:
        # Handle DecompressionBombError, which occurs if the image exceeds the decompression limit
        print(f"Image.DecompressionBombError occurred: {e}")
        return None

def run_pixelmatch(baseline_image, screenshot_image):
    """
    Compare two images using pixelmatch and create an RGBA image highlighting the differences.

    Args:
        baseline_image (PIL.Image): The first image.
        screenshot_image (PIL.Image): The second image.

    Returns:
        PIL.Image or str: An RGBA image highlighting the differences if differences are found,
                          or a string indicating no differences found.
    """
    try:
        # Convert images to RGBA if not already
        if baseline_image.mode != "RGBA":
            baseline_image = baseline_image.convert("RGBA")
        if screenshot_image.mode != "RGBA":
            screenshot_image = screenshot_image.convert("RGBA")

        # Ensure images have the same size
        if baseline_image.size != screenshot_image.size:
            raise ValueError("Images must have the same dimensions for comparison.")

        # Create a new RGBA image for highlighting differences
        diff_image = Image.new("RGBA", baseline_image.size)

        # Use pixelmatch to compare images and highlight differences
        num_diff_pixels = pixelmatch(baseline_image, screenshot_image, diff_image, threshold=0.1, includeAA=True)

        if num_diff_pixels == 0:
            return "No differences found in the UI"  # Return a message if no differences found
        else:
            return diff_image  # Return the diff image if differences found

    except Exception as e:
        print(f"Error during image comparison: {str(e)}")
        return None

def main():
    # Check if exactly two command-line arguments are provided
    if len(sys.argv) != 3:
        print("Two parameters are required: an endpoint and an image name! Please run the script again with those requirements.")
        # Print usage instructions if arguments are missing
        print("Usage: python script.py <URL> <image_name>")
        return

    # Extract URL and image name from command-line arguments
    url = sys.argv[1]
    image_name = sys.argv[2]

    if not validate_url(url):
        return

    try:
        make_get_request(url)
    except Exception:
        return

    ensure_folder_exists_otherwise_create(baseline_folder)  # Call the function to ensure the 'Baseline' folder exists

    # Check if image exists in Baseline folder
    if not image_exists_in_baseline(image_name):
        # Take screenshot of the URL
        screenshot_buffer = take_screenshot(url)
        save_screenshot_to_baseline(screenshot_buffer, image_name)
        return

    # Load baseline image
    baseline_image = load_baseline_image(image_name)

    # Take screenshot of the website
    screenshot_buffer = take_screenshot(url, {"width": baseline_image.width, "height": baseline_image.height})

    screenshot_image = process_screenshot_buffer(screenshot_buffer)
    if screenshot_image is None:
        # If an error occurred while processing the screenshot, print an error message
        print("Error occurred while processing the screenshot.")
        return

    # Print the dimensions of the screenshot
    print(f"Screenshot dimensions: {screenshot_image.size}")

    # Print the dimensions of the baseline image
    print(f"Baseline image dimensions: {baseline_image.size}")

    # Compare images
    result = run_pixelmatch(baseline_image, screenshot_image)

    if result is None:
        return
    if isinstance(result, str):
        print(result)  # If no differences found or error occurred, print the message
    else:
        output_folder = "Output"
        ensure_folder_exists_otherwise_create(output_folder)  # Call the function to ensure the 'Output' folder exists

        # Get only the base name (without extension)
        image_base_name, extension = os.path.splitext(image_name)

        diff_image_path = os.path.join(output_folder, f"{image_base_name}_differences.png")
        screenshot_image_path = os.path.join(
            output_folder, f"{image_base_name}_screenshot.png"
        )

        result.save(diff_image_path)
        screenshot_image.save(screenshot_image_path)

        print(f"Differences saved in {diff_image_path}")
        print(f"Screenshot saved in {screenshot_image_path}")

if __name__ == "__main__":
    main()
