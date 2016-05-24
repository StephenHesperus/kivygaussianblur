from functools import partial
from threading import Thread
from os import path

from kivy.config import Config

Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 640)
Config.set('kivy', 'keyboard_mode', 'system')


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import BooleanProperty
from kivy.properties import DictProperty
from kivy.properties import NumericProperty
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.animation import Animation

import cv2 as cv
import numpy as np


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
        if self._blur_thread.is_alive():
            self._blur_thread.join()
        else:
            self._blur_thread.start()

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


if __name__ == '__main__':
    GaussianBlurApp().run()
