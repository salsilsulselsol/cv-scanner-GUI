# scanner_logic.py

import cv2
import numpy as np

def remove_shadows(image):
    rgb_planes = cv2.split(image)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(norm_img)
    shadowless_image = cv2.merge(result_planes)
    return shadowless_image

def get_intersection(line1, line2):
    rho1, theta1 = line1; rho2, theta2 = line2
    A = np.array([[np.cos(theta1), np.sin(theta1)], [np.cos(theta2), np.sin(theta2)]])
    b = np.array([[rho1], [rho2]])
    try:
        x0, y0 = np.linalg.solve(A, b)
        return [int(np.round(x0)), int(np.round(y0))]
    except np.linalg.LinAlgError: return None

def scan_with_hough(image_path, canny1, canny2, hough_thresh):
    try:
        gambar_original_color = cv2.imread(image_path)
        if gambar_original_color is None: return None
        
        gambar_tanpa_bayangan = remove_shadows(gambar_original_color)
        gambar_gray = cv2.cvtColor(gambar_tanpa_bayangan, cv2.COLOR_BGR2GRAY)
        gambar_blur = cv2.GaussianBlur(gambar_gray, (5, 5), 0)
        gambar_canny = cv2.Canny(gambar_blur, canny1, canny2)
        kernel = np.ones((5,5), np.uint8)
        gambar_dilated = cv2.dilate(gambar_canny, kernel, iterations=1)
        lines = cv2.HoughLines(gambar_dilated, 1, np.pi / 180, hough_thresh)
        if lines is None: return None

        horizontal_lines = []; vertical_lines = []
        for line in lines:
            rho, theta = line[0]
            if (np.pi / 180 * 80 < theta < np.pi / 180 * 100): horizontal_lines.append((rho, theta))
            elif (theta < np.pi / 180 * 10 or theta > np.pi / 180 * 170): vertical_lines.append((rho, theta))
        if not horizontal_lines or not vertical_lines: return None
        
        top_edge = min(horizontal_lines, key=lambda x: x[0]); bottom_edge = max(horizontal_lines, key=lambda x: x[0])
        left_edge = min(vertical_lines, key=lambda x: x[0]); right_edge = max(vertical_lines, key=lambda x: x[0])

        p1=get_intersection(top_edge, left_edge); p2=get_intersection(top_edge, right_edge)
        p3=get_intersection(bottom_edge, left_edge); p4=get_intersection(bottom_edge, right_edge)
        if not all([p1, p2, p3, p4]): return None
    
        unorganized_corners = np.array([p1, p2, p3, p4], dtype="float32")
        corners = np.zeros((4, 2), dtype="float32")
        s = unorganized_corners.sum(axis=1)
        corners[0] = unorganized_corners[np.argmin(s)]; corners[2] = unorganized_corners[np.argmax(s)]
        diff = np.diff(unorganized_corners, axis=1)
        corners[1] = unorganized_corners[np.argmin(diff)]; corners[3] = unorganized_corners[np.argmax(diff)]
        
        return {'corners': corners}
    except Exception as e:
        print(f"Terjadi error di scanner_logic: {e}")
        return None