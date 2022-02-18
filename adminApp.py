from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty


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

    def showLog(self):
        self.manager.current = 'log'
    
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

class Row(RecycleKVIDsDataViewBehavior, BoxLayout):
    def showMachines(self):
        print("workkk")

class LogScreen(Screen):
    def on_enter(self, *args):
        return super().on_enter(*args)
    
    def populate(self):
        connection.ping(True)
        table = []
        dic = {}
        with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM log;")
                    r = cursor.fetchall()
                    rows = r[0][0] #num of rows in the table
                    cursor.execute("select * from log;")
                    result = cursor.fetchall()
                    cursor.execute("select * from students;")
                    students = cursor.fetchall()
                    for x in students:
                        dic.update({x[0]:x[1]}) #int:string
                    for x in result:
                        table.append([dic.get(x[0]),str(x[1]),str(x[2])])
        
        self.rv.data = [
            {'name.text': table[x][0],
            'time_in.text': table[x][1],
            'time_out.text': table[x][2],
            'machs.text': 'Click for machines' #make button for machines
            }
            for x in range(rows)]
        self.rv.data = sorted(self.rv.data, key=lambda x: x['time_in.text'], reverse=True)
    

    def sort(self):
        self.rv.data = sorted(self.rv.data, key=lambda x: x['time_in.text'])

    def clear(self):
        self.rv.data = []

    def insert(self, value):
        self.rv.data.insert(0, {
            'name.text': value or 'default value', 'value': 'unknown'})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['name.text'] = value or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)

class AdminApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AdminScreen(name = 'admin'))
        sm.add_widget(LogScreen(name = 'log'))
        return sm
       
if __name__ == "__main__":
    AdminApp().run()
