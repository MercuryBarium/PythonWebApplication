from base64 import b64encode, b64decode

event_data_template = [
    {
        "name": "Emails",
        "type": "string-list",
        "data": None
    },
    {
        "name": "Office Name",
        "type": "string",
        "data": None
    },
    {
        "name": "SomeInt",
        "type": "int",
        "min": 3,
        "max": 4,
        "data": None
    },
    {
        "name": "SomeFloat",
        "type": "float",
        "min": 3.0,
        "max": 6.0,
        "data": None
    }
]

test_data = [
    {
        "name": "Emails",
        "type": "string-list",
        "data": [
            "marcus.brulls@gmail.com",
            "vebbe90@gmail.com"
        ]
    },
    {
        "name": "Office Name",
        "type": "string",
        "data": "Lestrade INC"
    },
    {
        "name": "SomeInt",
        "type": "int",
        "min": 3,
        "max": 4,
        "data": 3
    },
    {
        "name": "SomeFloat",
        "type": "float",
        "min": 3.0,
        "max": 6.0,
        "data": 6.1
    }
]


def type_check(template, test, layer=0):
    if ("type" and "name" and "data" in template) and ("type" and "name" and "data" in test):
        if template["name"] == test["name"] and template["type"] == test["type"]:
            if template["type"] == "int":
                if type(test["data"]) == int:
                    if "min" in template and "min" in test:
                        if not (template["min"] == test["min"]):
                            return None, False
                        if not(test["data"] >= template["min"]):
                            return None, False

                    if "max" in template and "max" in test:
                        if not (template["max"] == test["max"]):
                            return None, False
                        if not(test["data"] <= template["max"]):
                            return None, False

                    pass
                else:
                    return None, False
            
            elif template["type"] == "string":
                if type(test["data"]) == str:
                    test["data"] = b64encode(test["data"].encode("utf-8")).decode("utf-8")
                else:
                    return None, False
            
            elif template["type"] == "float":
                if type(test["data"]) == float:
                    if "min" in template and "min" in test:
                        if not (template["min"] == test["min"]):
                            return None, False
                        if not(test["data"] >= template["min"]):
                            return None, False

                    if "max" in template and "max" in test:
                        if not (template["max"] == test["max"]):
                            return None, False
                        if not(test["data"] <= template["max"]):
                            return None, False
                    pass
                else:
                    return None, False
            
            elif template["type"] == "int-list":
                if type(test["data"]) == list:
                    for item in test["data"]:
                        if type(item) == int:
                            if "min" in template and "min" in test:
                                if not (template["min"] == test["min"]):
                                    return None, False
                                if not(item >= template["min"]):
                                    return None, False

                            if "max" in template and "max" in test:
                                if not (template["max"] == test["max"]):
                                    return None, False
                                if not(item <= template["max"]):
                                    return None, False
                            pass
                        else:
                            return None, False
            
            elif template["type"] == "float-list":
                if type(test["data"]) == list:
                    for item in test["data"]:
                        if type(item) == float:
                            if "min" in template and "min" in test:
                                if not (template["min"] == test["min"]):
                                    return None, False
                                if not(item >= template["min"]):
                                    return None, False

                            if "max" in template and "max" in test:
                                if not (template["max"] == test["max"]):
                                    return None, False
                                if not(item <= template["max"]):
                                    return None, False
                            pass
                        else:
                            return None, False
            
            elif template["type"] == "string-list":
                if type(test["data"]) == list:
                    for i in range(len(test["data"])):
                        if type(test["data"][i]) == str:
                            test["data"][i] = b64encode(test["data"][i].encode("utf-8")).decode("utf-8")
                            pass
                        else:
                            return None, False
            
            return test, True
        
    else:
        layer += 1
        if len(template) == len(test):
            for i in range(len(template)):
                test[i], check = type_check(template[i], test[i], layer)
                if check:
                    pass
                else:
                    return None, False
            
            return test, True
        else:
            return None, False



test, check = type_check(event_data_template, test_data)
print(test)
