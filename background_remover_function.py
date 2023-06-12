import cv2
import numpy as np

def generate_mask(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    binary = cv2.medianBlur(binary, 3)
    mask = cv2.resize(binary, (img.shape[1], img.shape[0]))
    mask = np.expand_dims(mask, axis=2)
    mask = np.repeat(mask, 3, axis=2)
    return mask

def extract_foreground(image, mask):
    foreground = np.zeros_like(image)
    foreground[mask > 0] = image[mask > 0]
    return foreground

def remove_background(image, mask):
    background = np.zeros_like(image)
    background[mask == 0] = image[mask == 0]
    return background

def postprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    smoothed = cv2.bilateralFilter(gray, 9, 75, 75)
    _, binary = cv2.threshold(smoothed, 10, 255, cv2.THRESH_BINARY)
    binary = cv2.medianBlur(binary, 3)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.erode(binary, kernel, iterations=1)
    binary = cv2.dilate(binary, kernel, iterations=1)
    result = cv2.bitwise_and(image, image, mask=binary)
    return result
