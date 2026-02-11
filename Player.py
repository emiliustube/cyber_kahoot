class Player:
    def __init__(self, name, points, admin, client_socket, addr):
        self.name = name
        self.points = points
        self.admin = admin
        self.client_socket = client_socket
        self.addr = addr

    def GetPoints(self):
        return self.points

    def SetPoints(self, num):
        self.points = num

    def AddPoint(self):
        self.points += 1
    
    def RemPoint(self):
        self.points -= 1
    
    def GetName(self):
        return self.name
    
    def SetName(self, name):
        self.name = name
    
    def IsAdmin(self):
        return self.admin
