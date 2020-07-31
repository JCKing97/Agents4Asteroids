from typing import Tuple, List
from pyglet.image import ColorBufferImage
import numpy as np
import cv2
from PIL import Image


def get_closest_asteroid_from_image(image: ColorBufferImage) -> Tuple[List[int], int]:
    return [1, 2], 3


def detect_window_in_image(templates: List[str], cv_img) -> np.ndarray:
    """
    Use multiple templates to detect a section in cv_img where the window of the game is and return that image.

    :param templates: The template image filenames to detect the section of the image with.
    :param cv_img: The image to detect the window in.
    :return: A numpy array representing the cropped image.
    """
    lefts = []
    tops = []
    widths = []
    heights = []

    for index, template in enumerate(templates):
        template_image = cv2.imread(template, cv2.IMREAD_GRAYSCALE)
        w, h = template_image.shape[::-1]
        res = cv2.matchTemplate(cv_img, template_image, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        lefts.append(max_loc[0])
        tops.append(max_loc[1])
        heights.append(h)
        widths.append(w)

    median_left = int(np.median(lefts))
    median_top = int(np.median(tops))
    median_width = int(np.median(widths))
    median_height = int(np.median(heights))

    im_cropped = cv_img[median_top:median_top+median_height, median_left:median_left+median_width]
    return im_cropped
