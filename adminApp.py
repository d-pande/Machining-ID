from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

import credentials as creds #file with db credentials
import pymysql.cursors

connection = pymysql.connect(host=creds.dbhost,
                             user=creds.dbuser,
                             password=creds.dbpass,
                             database=creds.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)

class AdminScreen(Screen):
    def on_enter(self, *args):
        return super().on_enter(*args)

    def addStudent(self):
        curr_id = self.ids.id.text
        pass

    def toggleStatus(self, id, currColor):
        pass

class LogScreen(Screen):
    def on_enter(self, *args):
        return super().on_enter(*args)

class AdminApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AdminScreen(name = 'admin'))
        sm.add_widget(LogScreen(name = 'log'))
        return sm
       
if __name__ == "__main__":
    AdminApp().run()
