import bcrypt


def hashNsalt(plaintext):
    return (bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')


def checkPW(plaintext, hashed):
    if bcrypt.checkpw(plaintext.encode('utf-8'), hashed.encode('utf-8')):
        return True
    else:
        return False
