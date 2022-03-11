from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview.views import RecycleKVIDsDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty, OptionProperty, ListProperty
from kivy.uix.popup import Popup
import pymysql.cursors
import threading
import datetime

import credentials as creds #file with db credentials


connection = pymysql.connect(host=creds.dbhost,
                             user=creds.dbuser,
                             password=creds.dbpass,
                             database=creds.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)


def machsUsed(time_in): #returns displayable string of machines used by time_in
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("select machine_id from log_machines where time_in = \""+str(time_in)+"\"")
            machines = cursor.fetchall()
            ids = []
            ret = ""
            counter = 0
            for m in machines:
                ids.append(m[0])
            for i in ids:
                counter = counter+1
                ret = ret+str(counter)+". "+AdminScreen.machines[i]+"\n"
            if not ret:
                return "No Machines Logged"
            return ret


def allowed_machines(id): #returns list of machine IDs that a student can use
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            machs = []
            cursor.execute("select mach_id from students_machines where sid="+str(id)+" and can_use=1") 
            result = cursor.fetchall()
            if not result:
                # print("Invalid ID")
                return -1
            for l in result:
                machs.append(l[0]) #being stored as ints
            return machs


class AdminScreen(Screen):
    red = [1, 0, 0, 1]
    green = [0, 1, 0, 1]
    white = [1, 1, 1, 1]
    status = [red, green]

    machines = ['CNC Machine', 'Laser Cutter', 'Bandsaw', 'Sanding Belt', 'Drill Press', 'Heat Gun', 
                'Dremels / Rotary', 'Soldering'] #master list of machine names

    def on_enter(self, *args):
        self.ids.id_input.text = ''
        self.ids.name_input.text = ''
        return super().on_enter(*args)
    
    def validateInput(self):
        validated = True
        if not(len(self.ids.id_input.text) == 5 and self.ids.id_input.text.isnumeric()):
            self.ids.instructions1.text = "Invalid ID"
            t1 = (threading.Timer(1.5, lambda: AdminScreen.resetInstructions1(self)))
            t1.start()
            validated = False
        if len(self.ids.name_input.text) == 0 or not all(c.isalpha() or c.isspace() for c in self.ids.name_input.text):
            self.ids.instructions2.text = "Invalid Name"
            t2 = threading.Timer(1.5, lambda: AdminScreen.resetInstructions2(self))
            t2.start()
            validated = False
        return validated
        
    def viewAccess(self):
        if not self.validateInput():
            return
        curr_id = int(self.ids.id_input.text)
        curr_name = self.ids.name_input.text.lower()
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
        allowedMachs = allowed_machines(str(curr_id))
        for id in self.ids:
            if id.isnumeric() and int(id) in allowedMachs:
                self.ids[id].background_color = AdminScreen.status[1]
                self.ids[id].color = AdminScreen.white

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
    limitState = OptionProperty("latest100", options=["latest100", "lastWeek", "lastDay"])
    masterData = []

    def on_enter(self, *args):
        self.populate()
        return super().on_enter(*args)
    
    def populate(self):
        connection.ping(True)
        table = []
        dic = {}
        with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM log;")
                    r = cursor.fetchall()
                    numRows = r[0][0]
                    cursor.execute("select * from log;")
                    result = cursor.fetchall()
                    cursor.execute("select * from students;")
                    students = cursor.fetchall()
                    for x in students:
                        dic.update({x[0]:x[1]}) #int:string
                    for x in result:
                        table.append([dic.get(x[0]),('('+str(x[0])+')'),str(x[1]),str(x[2])])
                        
        self.rv.data = [ #rv.data stores a list of dictionaries, each item is a row from the database
            {'name.text': table[x][0],
            'sid.text': table[x][1],
            'time_in.text': table[x][2],
            'time_out.text': table[x][3],
            'machs.text': 'Click for machines'
            }
            for x in range(numRows)]
        self.rv.data = sorted(self.rv.data, key=lambda x: x['time_in.text'], reverse=True) #sortTIDown
        self.masterData = self.rv.data[:]
        self.rv.data = self.masterData[0:100] #default is latest 100 rows shown

    def switchLimit(self):
        newList = []
        currentDate = datetime.datetime.today()

        if self.limitState == 'latest100':
            self.limitState = 'lastWeek'
            self.ids.limits.text = 'Showing: Last Week'
            for row in self.masterData:
                date = datetime.datetime.strptime(row['time_in.text'], '%Y-%m-%d %H:%M:%S')
                daysDiff = (date-currentDate).days
                if daysDiff>=-7:
                    newList.append(row)
        elif self.limitState == 'lastWeek':
            self.limitState = 'lastDay'
            self.ids.limits.text = 'Showing: Last Day'
            for row in self.masterData:
                date = datetime.datetime.strptime(row['time_in.text'], '%Y-%m-%d %H:%M:%S')
                daysDiff = (date-currentDate).days
                if daysDiff>=-1:
                    newList.append(row)
        elif self.limitState == 'lastDay':
            self.limitState = 'latest100'
            self.ids.limits.text = 'Showing: Latest 100 Sign-Ins'
            newList = self.masterData[0:100]

        self.rv.data = newList[:]

        #resetting column labels
        self.ids.student.text = 'Students '
        self.ids.student.sortState = 'none'
        self.ids.TI.text = 'Time In \u25BC'
        self.ids.TI.sortState = 'down'
        self.ids.TO.text = 'Time Out '
        self.ids.TO.sortState = 'none'

      
class MachinesUsed(Popup):
    time = StringProperty()
    def __init__(self, timeIn, **kwargs):
        super(MachinesUsed, self).__init__(**kwargs)
        self.time = timeIn
    
    def update_text(self): #popup text becomes whatever string is returned
        return machsUsed(str(self.time))


class Row(RecycleKVIDsDataViewBehavior, BoxLayout):
    def showMachines(self):
        timeIn = self.ids.time_in.text
        p = MachinesUsed(timeIn)
        p.open()


class ColumnButton(Button):
    sortState = OptionProperty("none", options=["up", "down", "none"])

    def buttonPress(self, otherButtons, thisButton, r):
        for b in otherButtons:
            if b.sortState != "none":
                b.text = b.text[:-1]
                b.sortState = "none"
        
        if self.sortState == 'none':
            self.sortState = 'up'
            self.text = self.text + "\u25B2"
        elif self.sortState == 'up':
            self.sortState = 'down'
            self.text = self.text[:-1]
            self.text = self.text + "\u25BC"
        elif self.sortState == 'down':
            self.sortState = 'none'
            self.text = self.text[:-1]
           
        if self.sortState == 'up':
            r.rv.data = sorted(r.rv.data, key=lambda x: x[thisButton+'.text'])
        elif self.sortState == 'down':
            if thisButton == 'time_out':
                times = []
                nones = []
                for x in r.rv.data: 
                    if x["time_out.text"][0].isdigit():  
                        times.append(x)
                    else:
                        nones.append(x)
                r.rv.data = sorted(times, key=lambda x: x['time_out.text'], reverse=True) + sorted(nones, key=lambda x: x['time_out.text'], reverse=True)            
            else:
                r.rv.data = sorted(r.rv.data, key=lambda x: x[thisButton+'.text'], reverse=True)


class MachinesAccess(Screen):
    masterData = []

    def on_enter(self, *args):
        self.populate()
        return super().on_enter(*args)
    
    def populate(self):
        connection.ping(True)
        table = []
        with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM students;")
                    r = cursor.fetchall()
                    numRows = r[0][0]
                    cursor.execute("select * from students;")
                    students = cursor.fetchall()
                    for x in students:
                        table.append([str(x[1]),str(x[0])])
        self.rv.data = []
        self.rv.data = [ #rv.data stores a list of dictionaries, each item is a row from the database
            {'name.text': table[x][0],
            'sid.text': table[x][1],
            'machs.text': 'Click for machines'
            }
            for x in range(numRows)]
        self.rv.data = sorted(self.rv.data, key=lambda x: x['name.text'])
        self.masterData = self.rv.data[:]


class MachinesAllowed(Popup):
    sid = NumericProperty()
    def __init__(self, studentID, **kwargs):
        super(MachinesAllowed, self).__init__(**kwargs)
        self.sid = studentID
    
    def update_text(self): #popup text becomes whatever string is returned
        allowedMachines = allowed_machines(self.sid)
        if allowedMachines != -1:
            ret = ""
            counter = 0
            for m in allowedMachines:
                counter = counter+1
                ret = ret+str(counter)+". "+AdminScreen.machines[m]+"\n"
            if not ret:
                return "No Machines Allowed"
            return ret
        else:
            return "No Machines Allowed"


class AccessRow(RecycleKVIDsDataViewBehavior, BoxLayout):
    def showMachines(self):
        studentID = self.ids.sid.text
        p = MachinesAllowed(studentID)
        p.open()


class SearchBar(TextInput):
    word_list = ListProperty()
    mData = ListProperty()

    def __init__(self, **kwargs):
        super(SearchBar, self).__init__(**kwargs)

    def on_text(self, instance, value):
        display_data = []
        for row in self.parent.parent.parent.masterData:
            if self.text.lower() in row['name.text'].lower() or self.text.lower() in row['sid.text']:
                display_data.append(row)
        if len(self.text) == 0:
            display_data = self.parent.parent.parent.masterData
        self.parent.parent.parent.ids.rv.data = display_data
      

class AdminApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AdminScreen(name = 'admin'))
        sm.add_widget(LogScreen(name = 'log'))
        sm.add_widget(MachinesAccess(name = 'access'))
        return sm
       
if __name__ == "__main__":
    AdminApp().run()
