#  import glob

from functools import partial
from threading import Thread
from os import path

from kivy.config import Config

Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 640)
Config.set('kivy', 'keyboard_mode', 'system')


from kivy.app import App
#  from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.properties import DictProperty
from kivy.properties import ListProperty
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.animation import Animation

import cv2 as cv
import numpy as np

from utils import rgba


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
            'texture': None,
            'has_alpha': False,
            'initial_radius': 0,
            'initial_matrix': Matrix(),
        }, rebind=True)
    blurring = BooleanProperty(False)
    use_alpha = BooleanProperty(True)
    saving = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_cb = None
        self._blur_thread = None

    def on_image_choose(self, imfile):
        self.imfile = imfile
        self.prepare_texture(imfile)
        self.image.texture = self.texture
        self.image.has_alpha = self.texture.colorfmt == 'bgra'
        self.current = 'blur'

    def on_radius_change(self, radius):
        self.radius = radius
        Clock.unschedule(self._last_cb)
        self._last_cb = partial(self._threaded_gaussian_blur, radius=radius)
        Clock.schedule_once(self._last_cb, .1)

    def _threaded_gaussian_blur(self, dt, radius):
        self._blur_thread = Thread(target=self.gaussian_blur, args=(radius, ))
        Clock.schedule_once(lambda dt: self._blur_thread.start(), .1)

    def prepare_texture(self, imfile):
        im = np.float32(cv.imread(imfile, -1)) / 255
        size = im.shape[1], im.shape[0]
        colorfmt = 'bgr' if im.shape[-1] == 3 else 'bgra'
        texture = Texture.create(size=size,colorfmt=colorfmt,
                                 bufferfmt='float')
        buf = cv.flip(im, 0).reshape(-1)

        self.radius = 0
        self.blur = im
        self.im = im
        self.imbuf = buf
        self.texture = texture
        texture.add_reload_observer(self.populate_texture)
        self.populate_texture()

    @mainthread
    def _set_blurring(self, blurring):
        self.blurring = blurring

    @mainthread
    def populate_texture(self):
        self.texture.blit_buffer(self.imbuf, bufferfmt=self.texture.bufferfmt,
                                 colorfmt=self.texture.colorfmt)
        self.canvas.ask_update()

    def gaussian_blur(self, radius, *args):
        '''
        This method here is used as callback for Clock.schedule_once, hence the
        ``*args`` parameter.
        '''
        self._set_blurring(True)
        if radius == 0:
            b = self.im
        else:
            b = cv.GaussianBlur(self.im, (0, 0), radius)
            if self.texture.colorfmt == 'bgra' and self.use_alpha:
                with np.errstate(divide='ignore', invalid='ignore'):
                    b = cv.merge([b[..., :3] / b[..., -1:], b[..., -1:]])
        self.blur = b
        self.imbuf = cv.flip(b, 0).reshape(-1)
        self.populate_texture()
        self._set_blurring(False)

    def save(self):
        self.saving = True
        f, e = path.splitext(self.imfile)
        alpha = ('.alpha_%s' % ('on' if self.use_alpha else 'off')
                 if self.image.has_alpha else '')
        fn = f + '.gaussian_blur.raidus_%.1f' % self.radius + alpha + e
        cv.imwrite(fn, self.blur*255,
                   (cv.IMWRITE_JPEG_QUALITY, 100,
                    cv.IMWRITE_PNG_COMPRESSION, 9))
        self.saving = False


from kivy.graphics import Color
from kivy.graphics import Rectangle

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


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
import time

class SliderCalculation(BoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = TextInput(readonly=True)
        slider = Slider(range=(0, 10000), step=1, size_hint=(1, None),
                        height='64dp')
        self.orientation = 'vertical'
        self.add_widget(text)
        self.add_widget(slider)
        slider.bind(value=self.on_slider_value)
        self._last_cb = None

    def on_slider_value(self, slider, radius):
        Clock.unschedule(self._last_cb)
        self._last_cb = partial(self._calculate, radius)
        Clock.schedule_once(self._last_cb, .1)

    def _calculate(self, radius, *args):
        time.sleep(1)
        print(radius)


from kivy.graphics import Line
from kivy.graphics import Ellipse
from kivy.graphics.stencil_instructions import StencilPush
from kivy.graphics.stencil_instructions import StencilPop
from kivy.graphics.stencil_instructions import StencilUse
from kivy.graphics.stencil_instructions import StencilUnUse
from kivy.animation import AnimationTransition

class Indicator1(Widget):

    color = ListProperty(rgba('9e9e9e'))
    reset = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tick = 0
        self._progress = 0
        self.bind(reset=self.on_reset)
        Clock.schedule_interval(self.draw_indicator, .01)

    def on_reset(self, indicator, reset):
        if reset:
            self._tick = 0
            self._progress = 0

    def draw_indicator(self, dt):
        with self.canvas:
            self.canvas.clear()

            Color(*self.color)
            Ellipse(pos=(self.center_x-32, self.center_y-32), size=(64, 64),
                    source='./images/indicator.png',
                    angle_start=self._progress,
                    angle_end=360-self._progress)

        self._tick = (self._tick + 1/15) % 1
        self._progress = AnimationTransition.in_out_cubic(self._tick) * 30 % 31


from kivy.properties import NumericProperty

class Indicator(Image):

    angle = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        anim = Animation(angle=-360, d=1, t='in_out_cubic')
        anim += Animation(angle=0, d=0)
        anim.repeat = True
        anim.start(self)


class GaussianBlurApp(App):

    def build(self):
        return GaussianBlurWindow()
        #  return TextureImage()
        #  return SliderCalculation()


if __name__ == '__main__':
    GaussianBlurApp().run()
