from model.matlista import basicusermanager

config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)

print(backend.checkuserexists('vebbe90@gmail.com'))