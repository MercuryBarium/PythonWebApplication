import tkinter
import os

mysql   = os.popen('mysql --version')

if mysql.read()