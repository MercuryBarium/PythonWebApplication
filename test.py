import pymysql, pymysql.cursors
import time


now = time.time()
connection = pymysql.connect(
    'localhost',
    'pythonhttp',
    'qwerty123',
    'matlista',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True)

thisCursor = connection.cursor()

connection2 = pymysql.connect(
    'localhost',
    'pythonhttp',
    'qwerty123',
    'matlista',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True)

thisCursor2 = connection.cursor()

print(connection.)

thisCursor.close()
connection.close()

thisCursor2.close()
connection2.close()
later = time.time()

print('operation took : %f seconds' % (later-now))