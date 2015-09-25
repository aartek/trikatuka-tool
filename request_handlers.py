import AppContext
import web
import os
import base64
import json
import requests
import sys
from UserTracks import UserTracks

__all__= ['Hello','Checkusers','UserAuthorized','LoginPrevious','LoginCurrent','SignOutPrevious','SignOutCurrent',
          'Playlists','Transfer']

render = web.template.render(AppContext.templates, base='layout')


class Hello:
    def GET(self):
        return render.index(AppContext.olduser, AppContext.newuser, AppContext.pagination)


class Checkusers:
    def GET(self):
        currentLoggedIn = True if AppContext.newuser.access_token else False
        previousLoggedIn = True if AppContext.olduser.access_token else False
        response = {'users':{'current':currentLoggedIn, 'previous': previousLoggedIn}}
        web.header('Content-Type', 'application/json')
        return json.dumps(response)


class UserAuthorized:
    def GET(self):
        params = web.input()
        if params:
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
        params = web.input()
        if params and params.offset:
            AppContext.pagination.offset = int(params.offset)
        AppContext.olduser.loadPlaylists()
        raise web.seeother('/')


class Transfer:
    def POST(self):
        params = web.input(pid=[], copy_tracks=False)
        print params

        if not AppContext.newuser.access_token or not AppContext.olduser.access_token:
            raise web.seeother('/')

        for param in params['pid']:
            playlist = AppContext.olduser.playlists[param]
            if AppContext.olduser.user_id != AppContext.newuser.user_id:
                if playlist and playlist.collaborative:
                    playlist.follow_collaborative()
                else:
                    playlist.copy_playlist()

        if params['copy_tracks'] == 'true':
            user_tracks = UserTracks()
            user_tracks.copy_tracks(AppContext.olduser, AppContext.newuser)

        raise web.seeother('/')






