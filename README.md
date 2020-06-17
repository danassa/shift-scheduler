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

5. Edit the spec file as seen below

6. Run:
pyinstaller --clean sahar.spec

This will create a 'dist' folder containing an EXE file with a config file you can distribute to the end user.



####SPEC file should contain:

block_cipher = None
from PyInstaller.utils.hooks import copy_metadata
datas=[*copy_metadata('google-api-python-client')]
a = Analysis(['main.py'],
             datas=datas,
.......
.......
import shutil
shutil.copyfile('right.gif', '{0}/right.gif'.format(DISTPATH))
shutil.copyfile('left.gif', '{0}/left.gif'.format(DISTPATH))
shutil.copyfile('auth_service_account.json', '{0}/auth_service_account.json'.format(DISTPATH))
shutil.copyfile('oauth_2_client_id.json', '{0}/oauth_2_client_id.json'.format(DISTPATH))




