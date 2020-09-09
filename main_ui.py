
"""
GoCalc/main_ui.py
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

####################################################################################################

def main():

    GoCalcApp().run()

    exit()

####################################################################################################

class GoCalcApp(App):
    def build(self):
        return MainWindow()

class MainWindow(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'

####################################################################################################

main()
