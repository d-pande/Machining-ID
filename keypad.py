from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

import credentials as creds #file with db credentials
import pymysql.cursors

#Connecting to the Database
connection = pymysql.connect(host=creds.dbhost,
                             user=creds.dbuser,
                             password=creds.dbpass,
                             database=creds.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)


def allowed_machines(id): #returns list of machine IDs that a student can use
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            machs = []
            cursor.execute("select mid from students_machines where sid="+id+" and can_use=1") 
            result = cursor.fetchall()
            if not result:
                print("Invalid ID")
                return -1
            for l in result:
                machs.append(l[0]) #being stored as ints
            return machs

class IDScreen(Screen):
    id_label = ObjectProperty() #make id text accessible here
    def on_enter(self, *args): 
        return super().on_enter(*args)

    def updateID(self, key):
        if (key.isnumeric() and len(self.id_label.text) < 9): #add only 5 numbers
            self.id_label.text += key
        elif (key == 'delete' and len(self.id_label.text) > 4):
            self.id_label.text = self.id_label.text[:-1] #don't delete 'ID: '

    def sendID(self):
        if (len(self.id_label.text) == 9):
            id = self.id_label.text[4:]
            # print(id)
            allowed = allowed_machines(id) #SEND ID TO SQL SERVER and get list of machine ID's that student can use
            if allowed != -1:
                self.manager.current = 'machine' #switch screen
            self.id_label.text = 'ID: '
            
            




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