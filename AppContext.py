import os
import ConfigParser
from User import User
from Pagination import Pagination

dir = os.path.dirname('__file__')
configfile = ConfigParser.ConfigParser()
configfile.read(os.path.join(dir, 'config.cfg'))
templates = os.path.join(dir, 'templates')

clientID = configfile.get('Client', 'clientID')
clientSecret = configfile.get('Client', 'clientSecret')

olduser = User()
newuser = User()

pagination = Pagination()