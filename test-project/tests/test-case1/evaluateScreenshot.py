#!/bin/python3

import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import argparse
import os
import sys

# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)



def preprocess_image(image_path: str) -> np.ndarray:

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image file '{image_path}' not found or cannot be opened.")

    # Increase image resolution
    height, width = image.shape[:2]
    new_size = (width * 2, height * 2)
    image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply binary thresholding to enhance text contrast
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return binary


def extract_text(image_path: str) -> str:

    processed_image = preprocess_image(image_path)
    pil_image = Image.fromarray(processed_image)

    custom_config = r'--oem 3 --psm 6 -l eng'
    text = pytesseract.image_to_string(pil_image, config=custom_config)

    return text


def clean_text(text: str) -> str:
    
    text = text.replace('iaplemented', 'implemented')
    text = text.replace('inplenented', 'implemented')

    # Remove unwanted characters and fix common OCR issues
    text = re.sub(r'[^\w\s:.]', '', text)
    text = re.sub(r'\s+', ' ', text)


    return text.strip()


def check_syscall(syscall_screenshot):

    syscall_screenshot_text = extract_text(syscall_screenshot)
    syscall_screenshot_text = clean_text(syscall_screenshot_text)

    pattern = r"This.*?(?:system\s*call|syscall)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+implemented"
    found = re.search(pattern, syscall_screenshot_text, re.IGNORECASE)
    status = 'Fail'

    if not found:
        print(f'Extracted: {syscall_screenshot_text}', file=sys.stderr)
        print('Syscall screenshot incorrect', file=sys.stderr)
        sys.exit(1)
    else:
        print('TestCase Passed')
        # print(f'Check Student Name -> {found.group(1)}')
        status = 'Pass'

    return status, syscall_screenshot_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("submissionPath")
    args = parser.parse_args()

    filepath = os.path.join(args.submissionPath, 'syscall-screenshot.png')
    check_syscall(filepath)
