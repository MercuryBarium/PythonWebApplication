class foodorder:
    def __init__(self, food, recipient, units):
        self.food = food
        self.recipient = recipient
        self.units = units

    def getNameOfFood(self):
        return self.food

    def getRecipient(self):
        return self.recipient

    def getUnits(self):
        return self.units

    