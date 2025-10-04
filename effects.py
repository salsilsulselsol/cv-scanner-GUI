# effects.py
import cv2

def apply_bw_filter(image):
    if image is None: return None
    scan_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scan_bw = cv2.adaptiveThreshold(scan_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 15)
    return scan_bw