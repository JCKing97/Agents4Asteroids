from typing import Type
import os
import numpy as np
from time import time
import cv2
from PIL import ImageGrab

from game.agent import Agent, Action
from game.perception import Perception, ImagePerception, VectorPerception

from agents.decide import attack_nearest_asteroid
from agents.perceive import get_closest_asteroid_from_image, detect_window_in_image
from agents.reactive_agent import ReactiveAgent


class ObjectDetectionAgent(Agent):

    def __init__(self, ship):
        super().__init__(ship)
        self.closest_asteroid = [0, 0]
        self.asteroid_radius = 0

    def perceive(self, perception: ImagePerception):
        """
        Receive a perception of the state of the game as an image

        :param perception: The perception received
        :return: None
        """
        self.closest_asteroid, self.asteroid_radius = get_closest_asteroid_from_image(perception.get_perception_data())

    def decide(self) -> Action:
        return attack_nearest_asteroid(self.ship, self.closest_asteroid, self.asteroid_radius)

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return ImagePerception


class ObjectDetectionTrainingAgent(ReactiveAgent):
    # TODO https://pythonprogramming.net/haar-cascade-object-detection-python-opencv-tutorial/

    def __init__(self, ship):
        super().__init__(ship)
        self.last_recorded_image_time = time()
        template_dir = "training_images/templates"
        self.templates = [os.path.join(template_dir, template) for template in os.listdir(template_dir)]

    def perceive(self, perception: VectorPerception):
        super().perceive(perception)
        current_time = time()
        if current_time - self.last_recorded_image_time > 2:
            image = ImageGrab.grab().convert("RGB")
            cv_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
            detect_window_in_image(self.templates, cv_image)
            # next_image_num = len(os.listdir("training_images"))
            # image.save("training_images/image_{}.png".format(next_image_num))
            self.last_recorded_image_time = current_time
