import os
import ConfigParser
from User import User

dir = os.path.dirname('__file__')
configfile = ConfigParser.ConfigParser()
configfile.read(os.path.join(dir, 'config.cfg'))
templates = os.path.join(dir, 'templates')

clientID = configfile.get('Client', 'clientID')
clientSecret = configfile.get('Client', 'clientSecret')

olduser = User()
newuser = User()

class Pagination():
    def __init__(self):
        self.total = 0
        self.offset = 0
        self.max = 20

pagination = Pagination()