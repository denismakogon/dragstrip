'''
Created on Dec 19, 2014

@author: ozamiatin
'''

class ClientInfo():

    def __init__(self,
                 client_name,
                 reg_time,
                 is_online):
        self.client_name = client_name
        self.reg_time = reg_time
        self.is_online = is_online


    def set_status(self, is_online):
        self.is_online = is_online