from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

class IDScreen(Screen):
    id_label = ObjectProperty() #make id text accessible here
    def on_enter(self, *args):
        self.id_label.text = 'ID: ' #reset id when coming back to this screen
        return super().on_enter(*args)

    def updateID(self, key):
        if (key.isnumeric() and len(self.id_label.text) < 9): #add only 5 numbers
            self.id_label.text += key
        elif (key == 'delete' and len(self.id_label.text) > 4):
            self.id_label.text = self.id_label.text[:-1] #don't delete 'ID: '

    def sendID(self):
        if (len(self.id_label.text) == 9):
            #SEND ID TO SQL SERVER
            self.manager.current = 'machine' #switch screen


class MachineScreen(Screen):
    pass

class KeypadApp(App):
    def build(self):
        # Builder.load_file('keypad.kv')
        sm = ScreenManager()
        sm.add_widget(IDScreen(name='ID'))
        sm.add_widget(MachineScreen(name='machine'))
        return sm

if __name__ == "__main__":
    KeypadApp().run()