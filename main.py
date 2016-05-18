from kivy.config import Config

Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 640)
Config.set('kivy', 'keyboard_mode', 'system')


from kivy.app import App
#  from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import BooleanProperty
from kivy.properties import DictProperty

import cv2 as cv
import numpy as np


#  Builder.load_file('./textinputs.kv')


class ImageButton(ButtonBehavior, Image):

    disabled = BooleanProperty(False)


class GaussianBlurWindow(ScreenManager):

    image = DictProperty({
            'path': '',
            'has_alpha': False,
        }, rebind=True)

    def on_choose_file(self, imfile):
        self.image.path = imfile
        im = np.float64(cv.imread(imfile, -1))
        self.image.has_alpha = im.shape[-1] == 4
        self.current = 'blur'


class GaussianBlurApp(App):

    def build(self):
        return GaussianBlurWindow()


if __name__ == '__main__':
    GaussianBlurApp().run()
