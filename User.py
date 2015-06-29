import webbrowser
import requests
from Playlist import Playlist
import AppContext
import uuid

__all__ = ['User']

class User:
    def __init__(self):
        self._set_initial_params()

    def _set_initial_params(self):
        self.access_token = None
        self.user_id = None
        self.name = None
        self.playlists = {}
        self.image_url = None
        self.authorization_id = str(uuid.uuid4())

    def login(self):
        redirect_uri="http://localhost:7878/user_auth_callback"
        scope="playlist-read-private%20playlist-read-collaborative%20playlist-modify-public%20playlist-modify-private%20user-follow-read"
        show_dialog="true"
        url = 'https://accounts.spotify.com/authorize?client_id='+AppContext.clientID+'&response_type=code&redirect_uri='+redirect_uri+'&client_secret='+AppContext.clientSecret+'&show_dialog=true&state='+self.authorization_id+'&scope='+scope
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
        payload = {
            'offset': AppContext.pagination.offset
        }
        response = requests.get('https://api.spotify.com/v1/users/'+str(self.user_id)+'/playlists', params=payload, headers=self.getHeaders(), verify=False)
        response = response.json();
        AppContext.pagination.total = response["total"]
        self.setPlaylists(response["items"])

    def getHeaders(self):
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer '+str(self.access_token),
                   'Content-Type': 'application/json'}
        return headers

    def setPlaylists(self, items):
        self.playlists = {};
        for item in items:
            playlist = Playlist(item)
            self.playlists[playlist.id]=playlist

    def playlistsForHuman(self):
        buf=""
        for p in self.playlists:
            buf += p.name +' Public: '+str(p.public)+' Collaborative: '+str(p.collaborative) +"\n"
        return buf
