import threading
import requests
import base64
import web
import sys
import webbrowser
import uuid
import os
import json
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
import ConfigParser

sys.argv[1:] = ['7878']
print sys.argv

global clientID
global clientSecret

dir = os.path.dirname('__file__')
config = ConfigParser.ConfigParser()
config.read(os.path.join(dir, 'config.cfg'))
clientID = config.get('Client','clientID')
clientSecret = config.get('Client','clientSecret')

urls = (
    '/', 'hello',
    '/login_previous', 'login_previous',
    '/login_current', 'login_current',
    '/sign_out_previous', 'sign_out_previous',
    '/sign_out_current', 'sign_out_current',
    '/user_auth_callback', 'user_authorized',
    '/playlists', 'playlists',
    '/transfer', 'transfer'
)

filename = os.path.join(dir, 'templates')
render = web.template.render(filename, base='layout')

app = web.application(urls, globals())

class SocketServer(WebSocket):

    def handleMessage(self):
        # echo message back to client
        self.sendMessage(self.data)

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


class SocketService():
    def __init__(self):
        self.started = False
        self.server = None


    def start(self):
        print "starting socket server"
        if not self.started:
            self.server = SimpleWebSocketServer('', 7879, SocketServer)
            self.server.serveforever()
            self.started = True


    def sendMessage(self):
        # self.server.sendMessage()
        pass

global socket_service
socket_service = SocketService()

class auth:
    def __init__(self):
        self.auth_code = None

authdata = auth();

class Playlist:
    def __init__(self, item):
        self.id = item["id"]
        self.name = item["name"]
        self.public = item["public"]
        self.collaborative = item["collaborative"]


class User:
    def __init__(self):
        self._set_initial_params()

    def _set_initial_params(self):
        self.access_token = None
        self.user_id = None
        self.name = None
        self.playlists = {}
        self.image_url = None

    def login(self, state):
        redirect_uri="http://localhost:7878/user_auth_callback"
        scope="playlist-read-private%20playlist-read-collaborative%20playlist-modify-public%20playlist-modify-private%20user-follow-read"
        show_dialog="true"
        url = 'https://accounts.spotify.com/authorize?client_id='+clientID+'&response_type=code&redirect_uri='+redirect_uri+'&client_secret='+clientSecret+'&show_dialog=true&state='+state+'&scope='+scope
        webbrowser.open(url)

    def logout(self):
        self._set_initial_params()

    def fetchDetails(self):
        response = requests.get('https://api.spotify.com/v1/me', headers=self.getHeaders(), verify=False)
        response = response.json()
        self.user_id = response["id"]
        self.name = response["display_name"] if response["display_name"] else '-'
        if(len(response["images"])>0):
            self.image_url = response["images"][0]["url"]

    def loadPlaylists(self):
        response = requests.get('https://api.spotify.com/v1/users/'+str(self.user_id)+'/playlists', headers=self.getHeaders(), verify=False)
        response = response.json();
        self.setPlaylists(response["items"])

    def getHeaders(self):
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer '+str(self.access_token),
                   'Content-Type': 'application/json'}
        return headers

    def setPlaylists(self, items):
        for item in items:
            playlist = Playlist(item)
            self.playlists[playlist.id]=playlist

    def playlistsForHuman(self):
        buf=""
        for p in self.playlists:
            buf += p.name +' Public: '+str(p.public)+' Collaborative: '+str(p.collaborative) +"\n"
        return buf

olduser = User()
newuser = User()

olduser_authorization_id = str(uuid.uuid4())
newuser_authorization_id = str(uuid.uuid4())

class hello:
    def GET(self):
        return render.index(authdata,olduser,newuser)

class user_authorized:
    def GET(self):
        params  = web.input()
        if(params):
            if hasattr(params,'error'):
                return render.loginUnsuccessful()

            authdata.auth_code = params.code

            authorization = base64.standard_b64encode(clientID + ':' + clientSecret)
            payload = {
                'grant_type': 'authorization_code',
                'code': authdata.auth_code,
                'redirect_uri': "http://localhost:7878/user_auth_callback"
            }
            headers = {'Authorization' : 'Basic ' + authorization}
            url = 'https://accounts.spotify.com/api/token'

            response = requests.post(url,data=payload,headers=headers, verify=False)
            response = response.json()

            if(params.state == olduser_authorization_id):
                olduser.access_token = response["access_token"]
                olduser.fetchDetails()
                olduser.loadPlaylists()
            elif(params.state == newuser_authorization_id):
                newuser.access_token = response["access_token"]
                newuser.fetchDetails()

            socket_service.sendMessage()
            return render.loginSuccessful()
        else:
            return render.loginUnsuccessful()

class login_previous:
    def GET(self):
        olduser.login(olduser_authorization_id)
        raise web.seeother('/')

class login_current:
    def GET(self):
        newuser.login(newuser_authorization_id)
        raise web.seeother('/')

class sign_out_previous:
    def GET(self):
        olduser.logout()
        raise web.seeother('/')

class sign_out_current:
    def GET(self):
        newuser.logout()
        raise web.seeother('/')

class playlists:
    def GET(self):
        olduser.loadPlaylists()
        raise web.seeother('/')

class transfer:
    def POST(self):
        params  = web.input(pid = [])
        print params

        if not newuser.access_token or not olduser.access_token:
            raise web.seeother('/')

        for param in params['pid']:
            if olduser.playlists[param] and olduser.playlists[param].collaborative \
                    and olduser.user_id != newuser.user_id:
                self.follow_collaborative(param)
            else:
                self.copy_playlist(param)

        raise web.seeother('/')

    def follow_collaborative(self, playlist_id):
        print 'following...'
        payload = {
            'public': olduser.playlists[playlist_id].public
        }
        headers = {
            'Authorization' : 'Bearer ' + newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = 'https://api.spotify.com/v1/users/'+olduser.user_id+'/playlists/'+playlist_id+'/followers'
        response = requests.put(url,data=payload,headers=headers, verify=False)
        print response

    def copy_playlist(self,playlist_id):
        headers = {
            'Authorization' : 'Bearer ' + olduser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'fields' : 'items(track.uri)'
        }

        try:
            url = 'https://api.spotify.com/v1/users/'+olduser.user_id+'/playlists/'+playlist_id+'/tracks'
            response = requests.get(url, params=payload, headers=headers, verify=False)
            response = response.json()

            tracks = response["items"]
            uris = []
            for item in tracks:
                uris.append(item["track"]["uri"])

            new_playlist_id = self.create_playlist(playlist_id)
            self.add_tracks_to_playlist(uris, new_playlist_id)

        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "Error during migrating playlist: " + olduser.playlists[playlist_id].name



    def create_playlist(self, playlist_id):
        headers = {
            'Authorization': 'Bearer ' + newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'name': olduser.playlists[playlist_id].name,
            'public': olduser.playlists[playlist_id].public
        }
        url = 'https://api.spotify.com/v1/users/'+newuser.user_id+'/playlists'
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response = response.json()
        return response["id"]

    def add_tracks_to_playlist(self, tracks, playlist_id):
        headers = {
            'Authorization' : 'Bearer ' + newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'uris': tracks
        }
        url = 'https://api.spotify.com/v1/users/'+newuser.user_id+'/playlists/'+playlist_id+'/tracks'
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response = response.json()

if __name__ == "__main__":
    # t1 = threading.Thread(target=socket_service.start)
    # t1.start()
    app.run()
