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
from kivy.graphics.texture import Texture
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.clock import Clock

import cv2 as cv
import numpy as np


def gaussian_blur(image, radius):
    '''
    Return the image with gaussian blur filter applied.

    This version correctly handle the alpha channel is it exists.

    :param image: The image array returned by :method:``cv2.imread``
    :param float radius: The blur radius
    :return: The image with Gaussian Blur applied
    :rtype: ``np.array`` with ``dtype`` of ``cv.CV_64F``
    '''
    b0 = cv.GaussianBlur(np.float64(image), (0, 0), radius)
    if b0.shape[-1] == 4: # alpha channel exists
        with np.errstate(invalid='ignore'):
            b1 = cv.merge([b0[..., :3] / b0[..., -1:] * 255.0, b0[..., -1:]])
            b1[np.isnan(b1)] = 0
    else:
        b1 = b0

    return b1


#  Builder.load_file('./textinputs.kv')


class ImageButton(ButtonBehavior, Image):

    disabled = BooleanProperty(False)


class GaussianBlurWindow(ScreenManager):

    image = DictProperty({
            'path': '',
            'has_alpha': False,
            'texture': None
        }, rebind=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_radius_change = Clock.create_trigger(self._radius_change, .15)

    def on_choose_file(self, imfile):
        self.prepare_texture(imfile)
        self.image.texture = self.texture
        self.image.has_alpha = self.texture.colorfmt == 'bgra'
        self.current = 'blur'

    def _radius_change(self, radius):
        print('Changing radius slider to', radius)

    def prepare_texture(self, imfile):
        im = np.float32(cv.imread(imfile, -1)) / 255
        size = im.shape[1], im.shape[0]
        colorfmt = 'bgr' if im.shape[-1] == 3 else 'bgra'
        texture = Texture.create(size=size,colorfmt=colorfmt,
                                 bufferfmt='float')
        buf = cv.flip(im, 0).reshape(-1)

        self.im = im
        self.imbuf = buf
        self.texture = texture
        texture.add_reload_observer(self.populate_texture)
        self.populate_texture()

    def populate_texture(self):
        self.texture.blit_buffer(self.imbuf, bufferfmt=self.texture.bufferfmt,
                                 colorfmt=self.texture.colorfmt)

    def gaussian_blur(self, radius):
        b0 = cv.GaussianBlur(self.im, (0, 0), radius)
        if self.texture.colorfmt == 'bgra':
            b = cv.merge([b0[..., :3] / b0[..., -1:], b0[..., -1:]])
        else:
            b = b0
        self.imbuf = cv.flip(b, 0).reshape(-1)
        self.populate_texture()


class TextureImage(Image):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with self.canvas.before:
            Color(1, 1, 1)
            Rectangle(size=(480, 640))

        imfile = './images/polygon.png'
        #  imfile = './images/sunset.jpg'
        im = np.float32(cv.imread(imfile, -1)) / 255
        size = im.shape[1], im.shape[0]
        colorfmt = 'bgr' if im.shape[-1] == 3 else 'bgra'
        texture = Texture.create(size=size,colorfmt=colorfmt,
                                 bufferfmt='float')
        buf = cv.flip(im, 0).reshape(-1)

        self.im = im
        self.imbuf = buf
        self.texture = texture
        texture.add_reload_observer(self.populate_texture)
        self.populate_texture()

        self.gaussian_blur(10)

    def populate_texture(self):
        self.texture.blit_buffer(self.imbuf, bufferfmt=self.texture.bufferfmt,
                                 colorfmt=self.texture.colorfmt)

    def gaussian_blur(self, radius):
        b0 = cv.GaussianBlur(self.im, (0, 0), radius)
        if self.texture.colorfmt == 'bgra':
            b = cv.merge([b0[..., :3] / b0[..., -1:], b0[..., -1:]])
        else:
            b = b0
        self.imbuf = cv.flip(b, 0).reshape(-1)
        self.populate_texture()


class GaussianBlurApp(App):

    def build(self):
        #  return GaussianBlurWindow()
        return TextureImage()


if __name__ == '__main__':
    GaussianBlurApp().run()
