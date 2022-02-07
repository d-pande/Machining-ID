import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import mysql.connector

millDatabase = mysql.connector.connect(host="192.168.86.211", user = "remote", passwd = "MILLpassword123", database = "id_project") 
dbcursor = millDatabase.cursor()

class MyScreen(App):
    def build(self):
        screen = FloatLayout()
        self.txtInput = TextInput(
            text = '',
            size_hint = (0.3,0.05),
            background_color = (1,0,1,0.5),
            pos_hint= {'x':0.05, 'y':0.70},
            font_size = '15sp')
        self.lblTxt = Label(
            text = 'Please Enter ID Numeber Below',
            size_hint = (0.3,0.05),
            pos_hint= {'x':0.05, 'y':0.75},
            font_size = '15sp')
        self.updateBtn = Button(
            text ='Update', size_hint =(.15, .20),
            background_color =(1,0,0,1),
            pos_hint ={'x':0.80, 'y':0.65},
            font_size='30sp')
        self.addStudentBtn = Button(
            text ='Add', size_hint =(.15, .20),
            max_lines=2,
            background_color =(1,0,0,1),
            pos_hint ={'x':0.6, 'y':0.65 },
            font_size='30sp',
            on_press = self.addStudent)
        self.machine1 = Button(
            text ='1', size_hint =(.25, .25),
            background_color =(1,0,0,1),
            pos_hint ={'x':0, 'y':0 },
            font_size='30sp',
            on_press = self.press1)
        self.machine2 = Button(
            text ='2', size_hint =(.25, .25),
            background_color =(1,0,0,1),
            pos_hint ={'x':.25, 'y':0 },
            font_size='30sp')
        self.machine3 = Button(
            text ='3', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':.5, 'y':0 },
            font_size='30sp')
        machine4 = Button(
            text ='4', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':.75, 'y':0 },
            font_size='30sp')

        machine5 = Button(
            text ='5', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':0, 'y':.25 },
            font_size='30sp')
        machine6 = Button(
            text ='6', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':0.25, 'y':.25 },
            font_size='30sp')
        machine7 = Button(
            text ='7', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':0.5, 'y':.25 },
            font_size='30sp')
        machine8 = Button(
            text ='8', size_hint =(.25, .25),
            background_color =(1,0,0),
            pos_hint ={'x':0.75, 'y':.25 },
            font_size='30sp')

        screen.add_widget(self.machine1)
        screen.add_widget(self.machine2)
        screen.add_widget(self.machine3)
        screen.add_widget(machine4)
        screen.add_widget(machine5)
        screen.add_widget(machine6)
        screen.add_widget(machine7)
        screen.add_widget(machine8)
        screen.add_widget(self.updateBtn)
        screen.add_widget(self.addStudentBtn)
        screen.add_widget(self.txtInput)
        screen.add_widget(self.lblTxt)
        return screen
    def press1(self,obj):
        if (self.machine1.background_color == [1,0,0,1]):
            self.machine1.background_color = (0,2,0)
        else:
            self.machine1.background_color = (1,0,0,1)
    def addStudent(self,obj):
        if (self.machine1.background_color == [1,0,0,1]):
            bool1 = False
        else:
            bool1 = True        
if __name__ == "__main__":
    MyScreen().run()