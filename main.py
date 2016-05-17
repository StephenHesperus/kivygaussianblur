from kivy.config import Config

Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 640)
Config.set('kivy', 'keyboard_mode', 'system')


from kivy.app import App
#  from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout


#  Builder.load_file('./textinputs.kv')


class ImageButton(ButtonBehavior, Image):

    pass


class ImageFileChooser(Popup):

    pass


class Dialog(BoxLayout):

    pass


class InitScreen(Screen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.popup = ImageFileChooser()

    def on_folder_open_click(self, *args):
        self.popup.open()
        self.manager.current = 'blur'


class GaussianBlurWindow(ScreenManager):

    pass


class GaussianBlurApp(App):

    def build(self):
        return GaussianBlurWindow()


if __name__ == '__main__':
    GaussianBlurApp().run()
