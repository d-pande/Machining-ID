from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window

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
            cursor.execute("select mach_id from students_machines where sid="+id+" and can_use=1") 
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

def signOut(id): #signs out a student given their ID, only updates last entry in log
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT time_in FROM log l1 WHERE sid = "+str(id)+" and time_in = (SELECT MAX(time_in) FROM log l2 WHERE l1.sid = l2.sid) ORDER BY sid, time_in;")
            result = cursor.fetchall()
            r = result[0][0]
            cursor.execute("update log set time_out = '"+timestamp+"' where sid = "+str(id)+" and time_in = '"+str(r)+"';")
            connection.commit()
                       

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
        elif (key == 'Delete' and len(self.id_label.text) > 4): #don't delete 'ID: '
            self.id_label.text = self.id_label.text[:-1]
        elif (key == 'Clear'):
            self.id_label.text = 'ID: '

    def signIn(self):
        id = self.id_label.text[4:]
        if (len(id) == 5) and checkID(id) and allowed_machines(id) != -1:
                IDScreen.curr_id = id
                self.manager.current = 'machine' #switch screen
        else:
            self.ids.instructions.text = 'Invalid ID' 
            t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
            t.start()
        self.id_label.text = 'ID: '

    def signOut(self):
        id = self.id_label.text[4:]
        if (len(id) == 5 and checkID(id)):
            signOut(id)
            self.ids.instructions.text = 'Signed Out!'
            t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
            t.start()
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

    machines = ['CNC Machine', 'Laser Cutter', 'Bandsaw', 'Sanding Belt', 'Drill Press', 'Heat Gun', 
                'Dremels / Rotary', 'Soldering']

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
    def on_enter(self, *args):
         self.t = threading.Timer(3.0, lambda: ConfirmationScreen.goToID(self))
         self.t.start()
         return super().on_enter(*args)
    
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
    Window.fullscreen = True
    KeypadApp().run()
