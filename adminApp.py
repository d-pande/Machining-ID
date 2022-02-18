from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

import credentials as creds #file with db credentials
import pymysql.cursors

import threading

connection = pymysql.connect(host=creds.dbhost,
                             user=creds.dbuser,
                             password=creds.dbpass,
                             database=creds.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)

class AdminScreen(Screen):
    red = [1, 0, 0, 1]
    green = [0, 1, 0, 1]
    status = [red, green]

    machines = ['CNC Machine', 'Laser Cutter', 'Bandsaw', 'Sanding Belt', 'Drill Press', 'Heat Gun', 
                'Dremels / Rotary', 'Soldering']

    def on_enter(self, *args):
        return super().on_enter(*args)

    def validateInput(self):
        validated = True
        if not(len(self.ids.id_input.text) == 5 and self.ids.id_input.text.isnumeric()):
            self.ids.instructions1.text = "Invalid ID"
            t1 = (threading.Timer(1.5, lambda: AdminScreen.resetInstructions1))
            t1.start()
            validated = False
        if not all(c.isalpha() or c.isspace() for c in self.ids.name_input.text):
            self.ids.instructions2.text = "Invalid Name"
            t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
            t2.start()
            validated = False
        return validated
        


    def addStudent(self):
        if not self.validateInput():
            return
        curr_id = int(self.ids.id_input.text)
        curr_name = self.ids.name_input.text.lower()
        currMachines = []
        for id in self.ids:
            if id.isnumeric():
                currMachines.append(self.ids[id].background_color == AdminScreen.status[1])
        connection.ping(True)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("select name from students where student_id = " + str(curr_id))
                if len(cursor.fetchall()) == 1:
                    self.ids.instructions1.text = "Student Already Exists"
                    self.ids.instructions2.text = "Student Already Exists"
                    t1 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions1(self))
                    t1.start()
                    t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
                    t2.start()
                    return
                cursor.callproc("add_new_student", [curr_id, curr_name, currMachines[0], currMachines[1], 
                                currMachines[2], currMachines[3], currMachines[4], currMachines[5], 
                                currMachines[6], currMachines[7]])
                connection.commit()
                self.ids.instructions1.text = "Student Added"
                self.ids.instructions2.text = "Student Added"
                t1 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions1(self))
                t1.start()
                t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
                t2.start()

    def updateStudent(self):
        if not self.validateInput():
            return
        curr_id = int(self.ids.id_input.text)
        curr_name = self.ids.name_input.text.lower()
        currMachines = []
        for id in self.ids:
            if id.isnumeric():
                currMachines.append(self.ids[id].background_color == AdminScreen.status[1])
        connection.ping(True)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT * FROM students WHERE student_id = "+str(curr_id)+" and name = \""+str(curr_name)+"\")")
                if cursor.fetchall()[0][0] == 0:
                    self.ids.instructions1.text = "Student Doesn't Exist"
                    self.ids.instructions2.text = "Student Doesn't Exist"
                    t1 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions1(self))
                    t1.start()
                    t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
                    t2.start()
                    return
                cursor.callproc("update_student", [curr_id, currMachines[0], currMachines[1], 
                                currMachines[2], currMachines[3], currMachines[4], currMachines[5], 
                                currMachines[6], currMachines[7]])
                connection.commit()
                self.ids.instructions1.text = "Student Updated"
                self.ids.instructions2.text = "Student Updated"
                t1 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions1(self))
                t1.start()
                t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
                t2.start()
                

    def toggleColor(self, id, currColor):
        self.ids[str(id)].background_color = AdminScreen.status[1 - AdminScreen.status.index(currColor)]
    
    def resetInstructions1(self):
        self.ids.instructions1.text = "Please Enter\nStudent ID Below"
    
    def resetInstructions2(self):
        self.ids.instructions2.text = "Please Enter\nStudent Name Below"

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
