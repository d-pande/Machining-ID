# Machining-ID

Sign-in and administration system for the MILL's machining room


## Description

Machining-ID provides a simple sign-in/sign-out system for students using the MILL's machining room. When signing in students can view the machines they are allowed to use and indicate which machines they're using each time they enter. An administrative app is also available for teachers, allowing them to manage students' access to the machines and monitor sign-in logs. Both apps are built primarily using the Kivy library for better support on touchscreen devices (especially for the sign-in keypad). 

## Getting Started

### Dependencies

* Windows: Packaged admin app is  available under 'Releases'
* If using the individual script files, you must download the requires packages listed in requirements.txt
    * Using a virtual environment is recomended
    * You must also manually add the credentials to connect to the database server in `credentials.py`

### Installing

* Windows: Simply download the latest release

* MacOS/Linux: Files can be manually downloaded and executed in terminal

### Executing program

* Windows: Launch the app, `adminApp.exe`
* MacOS/Linux: Run the python files in terminal


## Help

* If the keypad app does not launch, check to see if the MySQL server is running


## Authors

[Dhruv Pande](https://github.com/d-pande)

[Ishaan Ghosh](https://github.com/22ghoshi)

[Kylan Chen](https://github.com/Naylk)
