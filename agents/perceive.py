from typing import Tuple, List
from pyglet.image import ColorBufferImage
import numpy as np
import cv2
from matplotlib import pyplot as plt


def get_closest_asteroid_from_image(image: ColorBufferImage) -> Tuple[List[int], int]:
    return [1, 2], 3


def detect_window_in_image(templates: List[str], img: str):
    img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    cv_img2 = img.copy()
    cv_img = cv_img2.copy()
    for template in templates:
        template_image = cv2.imread(template, cv2.IMREAD_GRAYSCALE)
        w, h = template_image.shape[::-1]
        res = cv2.matchTemplate(cv_img, template_image, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(cv_img, top_left, bottom_right, 255, 2)

        plt.subplot(121), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(cv_img, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(cv2.TM_CCOEFF)
        plt.show()
        print("called show")
