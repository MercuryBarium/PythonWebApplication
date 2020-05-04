

def checkTypes(listOfVars):
    for i in listOfVars:
        var, t = i
        if type(var) != t:
            return False
    return True
        
        
l = [
    (12, int),
    ("12", int)
]

print(checkTypes(l))