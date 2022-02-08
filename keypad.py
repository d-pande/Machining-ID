from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

import credentials as creds #file with db credentials
import pymysql.cursors

import time
from datetime import datetime
import threading

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
            for m in machs:
                cursor.execute("insert into log_machines (time_in, machine_id) values ('"+timestamp+"', "+str(m)+")")
                connection.commit()

def checkID(id): #need to pass in id as a string
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("select exists(select * from students_machines where sid="+id+")")
            r = cursor.fetchall()
            return bool(r[0][0]) #returns true if student is in students_machines
                       

class IDScreen(Screen):
    id_label = ObjectProperty() #make id text accessible here
    curr_id = ''
    def on_enter(self, *args):
        self.id_label.text = 'ID: '
        self.instructionsText = 'Enter your Student ID'
        return super().on_enter(*args)

    def updateID(self, key):
        if (key.isnumeric() and len(self.id_label.text) < 9): #add only 5 numbers
            self.id_label.text += key
        elif (key == 'delete' and len(self.id_label.text) > 4): #don't delete 'ID: '
            self.id_label.text = self.id_label.text[:-1]

    def sendID(self):
        if (len(self.id_label.text) == 9):
            id = self.id_label.text[4:]
            isStudent = checkID(id)
            if (isStudent):
                allowed = allowed_machines(id)
                IDScreen.curr_id = id
                if allowed != -1:
                    self.manager.current = 'machine' #switch screen
            else:
                self.ids.instructions.text = 'Invalid ID' 
                t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
                t.start()
            self.id_label.text = 'ID: '
    
    def resetInstructions(self):
        self.ids.instructions.text = 'Enter your Student ID'




class MachineScreen(Screen):
    red = [1, 0, 0, 1]
    green = [0, 1, 0, 1]
    black = [0, 0, 0, 0]
    white = [1, 1, 1, 1]
    status = [red, green]

    machines = ['Tormach', 'Bosslaser', 'Prusa MINI', 'Prusa i3', 'Afinia H+1', 'Bandsaw', 
                'Sanding Belt', 'Drill Press', 'Heat Gun', 'Dremel', 'Soldering']

    def on_pre_enter(self, *args):
        allowedMachs = allowed_machines(IDScreen.curr_id)
        for id in self.ids:
            if int(id) in allowedMachs:
                self.ids[id].background_color = MachineScreen.status[0]
                self.ids[id].color = MachineScreen.white
        return super().on_pre_enter(*args)
    
    def toggleColor(self, id, currColor):
        if currColor in MachineScreen.status:
            self.ids[str(id)].background_color = MachineScreen.status[1 - MachineScreen.status.index(currColor)]

    def sendMachines(self):
        selectedMachines = []
        for id in self.ids:
            if self.ids[id].background_color == MachineScreen.status[1]:
                selectedMachines.append(int(id))
        log(IDScreen.curr_id, selectedMachines)
        self.manager.current = 'confirmation'

    def on_leave(self, *args):
        for id in self.ids:
            self.ids[id].background_color = MachineScreen.black
            self.ids[id].color = MachineScreen.black
        return super().on_leave(*args)

class ConfirmationScreen(Screen):
    # t = threading.Timer(5.0, lambda: gotoID(self))
    def on_enter(self, *args):
         self.t = threading.Timer(3.0, lambda: ConfirmationScreen.goToID(self))
         self.t.start()
    
    def goToID(self):
        self.manager.current = 'ID'

    def on_leave(self, *args):
        self.t.cancel()
        return super().on_leave(*args)

class KeypadApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(IDScreen(name = 'ID'))
        sm.add_widget(MachineScreen(name = 'machine'))
        sm.add_widget(ConfirmationScreen(name = 'confirmation'))
        return sm

if __name__ == "__main__":
    KeypadApp().run()
