from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class KeypadApp(App):
    def build(self):
        layout = BoxLayout(orientation='horizontal')
        button_grid = GridLayout(cols=3, size_hint_x=1.25) #size_hint gives a little more room for the buttons just in case

        output_label = Label(text='ID: ', font_size='25sp')
        button_symbols = ('1', '2', '3',
                          '4', '5', '6',
                          '7', '8', '9',
                          'delete', '0', 'enter')
        for symbol in button_symbols:
            button_grid.add_widget(Button(text=symbol, font_size='20sp'))

        def print_button_text(instance):
            #print("running print_button_text for "+instance.text)
            if(button_grid.children.index(instance)==2 and len(output_label.text)>4): #delete if they click button 2 (delete button) but make sure they don't delete the "ID: " part
                output_label.text = output_label.text[:-1]
            elif (instance.text.isnumeric() and len(output_label.text)<9): #making sure we only add 0-9 to the label and capping ID to 5 numbers
                output_label.text += instance.text

        for button in button_grid.children: #in the button_grid.children list the index of enter is 0, 0 is 1, del is 2, and so on
                button.bind(on_release=print_button_text) 
            
        def send_id(instance):
            if(len(output_label.text)==9):
                #SEND ID TO SQL SERVER?
                output_label.text = 'ID: '
            else:
                print('ID is less than 5 characters!')
        button_grid.children[0].bind(on_release=send_id)
        


        layout.add_widget(output_label)
        layout.add_widget(button_grid)

        return layout

if __name__ == '__main__':
    KeypadApp().run()
