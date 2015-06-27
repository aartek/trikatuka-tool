import AppContext
import web
import os
import base64
import json
import requests
import sys

render = web.template.render(AppContext.templates, base='layout')

class Hello:
    def GET(self):
        return render.index(AppContext.olduser,AppContext.newuser)

class Checkusers:
    def GET(self):
        currentLoggedIn = True if AppContext.newuser.access_token else False
        previousLoggedIn = True if AppContext.olduser.access_token else False
        response = {'users':{'current':currentLoggedIn, 'previous': previousLoggedIn}}
        web.header('Content-Type', 'application/json')
        return json.dumps(response)

class UserAuthorized:
    def GET(self):
        params  = web.input()
        if(params):
            if hasattr(params,'error'):
                return render.loginUnsuccessful()

            auth_code = params.code

            authorization = base64.standard_b64encode(AppContext.clientID + ':' + AppContext.clientSecret)
            payload = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': "http://localhost:7878/user_auth_callback"
            }
            headers = {'Authorization' : 'Basic ' + authorization}
            url = 'https://accounts.spotify.com/api/token'

            response = requests.post(url,data=payload,headers=headers, verify=False)
            response = response.json()

            if(params.state == AppContext.olduser.authorization_id):
                AppContext.olduser.access_token = response["access_token"]
                AppContext.olduser.fetchDetails()
                AppContext.olduser.loadPlaylists()
            elif(params.state == AppContext.newuser.authorization_id):
                AppContext.newuser.access_token = response["access_token"]
                AppContext.newuser.fetchDetails()

            return render.loginSuccessful()
        else:
            return render.loginUnsuccessful()

class LoginPrevious:
    def GET(self):
        AppContext.olduser.login()
        raise web.seeother('/')

class LoginCurrent:
    def GET(self):
        AppContext.newuser.login()
        raise web.seeother('/')

class SignOutPrevious:
    def GET(self):
        AppContext.olduser.logout()
        raise web.seeother('/')

class SignOutCurrent:
    def GET(self):
        AppContext.newuser.logout()
        raise web.seeother('/')

class Playlists:
    def GET(self):
        AppContext.olduser.loadPlaylists()
        raise web.seeother('/')

class Transfer:
    def POST(self):
        params  = web.input(pid = [])
        print params

        if not AppContext.newuser.access_token or not AppContext.olduser.access_token:
            raise web.seeother('/')

        for param in params['pid']:
            if AppContext.olduser.playlists[param] and AppContext.olduser.playlists[param].collaborative \
                    and AppContext.olduser.user_id != AppContext.newuser.user_id:
                self.follow_collaborative(param)
            else:
                self.copy_playlist(param)

        raise web.seeother('/')

    def follow_collaborative(self, playlist_id):
        print 'following...'
        payload = {
            'public': AppContext.olduser.playlists[playlist_id].public
        }
        headers = {
            'Authorization' : 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.olduser.user_id+'/playlists/'+playlist_id+'/followers'
        response = requests.put(url,data=payload,headers=headers, verify=False)
        print response

    def copy_playlist(self,playlist_id):
        headers = {
            'Authorization' : 'Bearer ' + AppContext.olduser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'fields' : 'items(track.uri)'
        }

        try:
            url = 'https://api.spotify.com/v1/users/'+AppContext.olduser.user_id+'/playlists/'+playlist_id+'/tracks'
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
            print "Error during migrating playlist: " + AppContext.olduser.playlists[playlist_id].name



    def create_playlist(self, playlist_id):
        headers = {
            'Authorization': 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'name': AppContext.olduser.playlists[playlist_id].name,
            'public': AppContext.olduser.playlists[playlist_id].public
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.newuser.user_id+'/playlists'
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response = response.json()
        return response["id"]

    def add_tracks_to_playlist(self, tracks, playlist_id):
        headers = {
            'Authorization' : 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'uris': tracks
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.newuser.user_id+'/playlists/'+playlist_id+'/tracks'
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response = response.json()