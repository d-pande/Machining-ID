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

import time
from datetime import datetime

# Connecting to the Database
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

def log(id, machs): #logs a student entering the room given an id and list of machines
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("insert into log (sid, time_in) values ("+str(id)+", '"+timestamp+"')")
            connection.commit()
            # print(machs)
            for m in machs:
                cursor.execute("insert into log_machines (time_in, machine_id) values ('"+timestamp+"', "+str(m)+")")
                connection.commit()
            

class IDScreen(Screen):
    id_label = ObjectProperty() #make id text accessible here
    curr_id = ''
    def on_enter(self, *args):
        self.id_label.text = 'ID: '
        return super().on_enter(*args)

    def updateID(self, key):
        if (key.isnumeric() and len(self.id_label.text) < 9): #add only 5 numbers
            self.id_label.text += key
        elif (key == 'delete' and len(self.id_label.text) > 4): #don't delete 'ID: '
            self.id_label.text = self.id_label.text[:-1]

    def sendID(self):
        if (len(self.id_label.text) == 9):
            id = self.id_label.text[4:]
            allowed = allowed_machines(id)
            if allowed != -1:
                self.manager.current = 'machine' #switch screen
            self.id_label.text = 'ID: '
            IDScreen.curr_id = id




class MachineScreen(Screen):
    red = [1, 0, 0, 1]
    green = [0, 1, 0, 1]
    black = [0, 0, 0, 0]
    white = [1, 1, 1, 1]
    status = [red, green]

    machines = ['Tormach', 'Bosslaser', 'Prusa MINI', 'Prusa i3', 'Afinia H+1', 'Bandsaw', 
                'Sanding Belt', 'Drill Press', 'Heat Gun', 'Dremel', 'Soldering']

    def on_enter(self, *args):
        allowedMachs = allowed_machines(IDScreen.curr_id)
        # print(allowedMachs)
        for id in self.ids:
            if int(id) not in allowedMachs:
                self.ids[id].background_color = MachineScreen.black
                self.ids[id].color = MachineScreen.black
            else:
                self.ids[id].background_color = MachineScreen.status[0]
        return super().on_enter(*args)
    
    def toggleColor(self, id, currColor):
        if currColor in MachineScreen.status:
            self.ids[str(id)].background_color = MachineScreen.status[1 - MachineScreen.status.index(currColor)]

    def sendMachines(self):
        selectedMachines = []
        for id in self.ids:
            if self.ids[id].background_color == MachineScreen.status[1]:
                selectedMachines.append(int(id))
        # print(selectedMachines)
        # print(IDScreen.curr_id)
        log(IDScreen.curr_id, selectedMachines)
        self.manager.current = 'ID'

class KeypadApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(IDScreen(name='ID'))
        sm.add_widget(MachineScreen(name='machine'))
        return sm

if __name__ == "__main__":
    KeypadApp().run()