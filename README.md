# shift-scheduler
Scheduling app for Sahar 



### How to create an app for Windows end user

1. Copy this project to a Windows OS

2. Install Python3 (if missing) and pip install the libraries:
    - PySimpleGUI	4.18.0
    - pyinstaller
    - pywin32
    
3. Open terminal and cd into /shift-scheduler directory

4. Run:
pyi-makespec --onefile -wF --name sahar main.py

5. Run:
pyinstaller --clean sahar.spec


This will create a 'dist' folder containing an EXE file with a config file you can distribute to the end user.