# Image Differentiator

This Python script allows you to compare images obtained from website screenshots with baseline images to identify any differences. It uses Playwright for capturing screenshots and Pixelmatch for image comparison.

## Prerequisites

Before running the script, ensure you have the following installed on your Mac machine:

- Python 3.x
- Pip (Python package installer)
- Playwright
- Pixelmatch
- Pillow

1. Navigate to the project directory:
```
cd Image_Differentiator
```

2. Create and activate a virtual environment (recommended):

```
# Using virtualenv
virtualenv venv

# Using venv (Python 3.x)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate 
```

3. You can install Python dependencies using pip:

```
pip install -r requirements.txt
```

## Installation

Make sure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/).

## Usage
1. Ensure that the baseline image you want to compare with is saved in the `Baseline` folder within the project directory. Otherwise, if the baseline image does not exist, a screenshot of the URL will be taken and stored in the `Baseline` folder.
2. Run the script with the following command:
```
python script.py <URL> <image_name>
```
Replace <URL> with the URL of the website you want to capture, and <image_name> with the name you want to give to the captured image.

Example:
```
python script.py https://example.com example_image
```

3. If differences are found between the baseline image and the screenshot, the highlighted differences will be saved in the `Output` folder within the project directory. The file name will be prefixed with the image name and suffixed with `_differences.png`. Additionally, the screenshot of the webpage will be saved in the `Output` folder with the name prefixed with the image name and suffixed with `_screenshot.png`.
