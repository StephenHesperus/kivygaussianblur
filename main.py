from kivy.config import Config

Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 640)
Config.set('kivy', 'keyboard_mode', 'system')


from kivy.app import App
#  from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty


#  Builder.load_file('./textinputs.kv')


class ImageButton(ButtonBehavior, Image):

    disabled = BooleanProperty(False)


class GaussianBlurWindow(ScreenManager):

    image = ObjectProperty()

    def on_choose_file(self, imfile):
        self.image = imfile
        self.current = 'blur'


class GaussianBlurApp(App):

    def build(self):
        return GaussianBlurWindow()


if __name__ == '__main__':
    GaussianBlurApp().run()
