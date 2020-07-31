from typing import Tuple, List
from pyglet.image import ColorBufferImage
import numpy as np
import cv2
from matplotlib import pyplot as plt
from time import time
from PIL import Image


def get_closest_asteroid_from_image(image: ColorBufferImage) -> Tuple[List[int], int]:
    return [1, 2], 3


def detect_window_in_image(templates: List[str], cv_img):
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

    print(median_left)
    print(median_top)
    print(median_right)
    print(median_bottom)

    im = Image.fromarray(cv_img)
    im_cropped = im.crop((median_left, median_top, median_right, median_bottom))
    im_cropped.save("training_images/detected_{}.jpg".format(time()))
