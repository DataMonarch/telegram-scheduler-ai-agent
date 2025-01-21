import cv2
import numpy as np
import pytesseract
import logging


def process_screenshot_text(screenshot, name):
    d = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    merged = []
    prev_y = -999
    prev_right = 0
    current_text = ""

    for i, txt in enumerate(d["text"]):

        txt = txt.strip()
        if not txt:
            continue
        x, y, w, h = d["left"][i], d["top"][i], d["width"][i], d["height"][i]

        if abs(y - prev_y) < h and x - prev_right < 30:
            current_text += " " + txt
            prev_right = x + w
        else:
            if current_text:
                merged.append((current_text, prev_x, prev_y))
            current_text = txt
            prev_x, prev_y, prev_right = x, y, x + w

    if current_text:
        merged.append((current_text, prev_x, prev_y))

    for text, x, y in merged:
        if name in text:
            return x, y

    return None


def find_best_match(large_image_path, small_image_path, threshold=0.7):

    large_img = cv2.imread(large_image_path)
    small_img = cv2.imread(small_image_path)

    result = cv2.matchTemplate(large_img, small_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = small_img.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2

        return (center_x, center_y)
    return None
