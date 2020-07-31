from typing import Tuple, List
from pyglet.image import ColorBufferImage
import numpy as np
import cv2
from PIL import Image


def get_closest_asteroid_from_image(image: ColorBufferImage) -> Tuple[List[int], int]:
    return [1, 2], 3


def detect_window_in_image(templates: List[str], cv_img) -> Image:
    """
    Use multiple templates to detect a section in cv_img where the window of the game is and return that image.

    :param templates: The template image filenames to detect the section of the image with.
    :param cv_img: The
    :return: An
    """
    lefts = []
    tops = []
    bottoms = []
    rights = []

    for index, template in enumerate(templates):
        template_image = cv2.imread(template, cv2.IMREAD_GRAYSCALE)
        w, h = template_image.shape[::-1]
        res = cv2.matchTemplate(cv_img, template_image, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        lefts.append(max_loc[0])
        tops.append(max_loc[1])
        bottoms.append(max_loc[0] + h)
        rights.append(max_loc[1] + w)

    median_left = np.median(lefts)
    median_top = np.median(tops)
    median_bottom = np.median(bottoms)
    median_right = np.median(rights)

    im = Image.fromarray(cv_img)
    im_cropped = im.crop((median_left, median_top, median_right, median_bottom))
    return im_cropped
