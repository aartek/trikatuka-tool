import logging
import AppContext
import requests
import sys
import json
import math
__all__ = ['Playlist']


class Playlist:
    def __init__(self, item):
        self.id = item["id"]
        self.name = item["name"]
        self.public = item["public"]
        self.collaborative = item["collaborative"]

    def follow_collaborative(self):
        print 'following...'
        payload = {
            'public': AppContext.olduser.playlists[self.id].public
        }
        headers = {
            'Authorization': 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.olduser.user_id+'/playlists/'+self.id+'/followers'
        response = requests.put(url, data=payload, headers=headers, verify=False)
        print response

    def copy_playlist(self):
        try:
            tracks = self._load_tracks()
            uris = []
            for item in tracks:
                uris.append(item["track"]["uri"])
            new_playlist_id = self._create_playlist()
            self._add_tracks_to_playlist(uris, new_playlist_id)

        except requests.exceptions.HTTPError:
            msg = "Could not copy playlist \"%s\" id: %s" % (self.name, self.id)
            logging.error(msg)

    def _load_tracks(self):
        tracks_json = self._fetch_tracks(0)
        tracks = tracks_json["items"]
        total = tracks_json["total"]

        if total > 100:
            pages = int(math.ceil(float(total)/100))
            for i in range(1, pages + 1):
                tracks_json = self._fetch_tracks(i * 100)
                tracks += tracks_json["items"]
        return tracks

    def _fetch_tracks(self, offset):
        headers = {
            'Authorization': 'Bearer ' + AppContext.olduser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'fields': 'total,items(track.uri)',
            'offset': offset
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.olduser.user_id+'/playlists/'+self.id+'/tracks'
        response = requests.get(url, params=payload, headers=headers, verify=False)
        response.raise_for_status()
        response = response.json()
        return response

    def _create_playlist(self):
        headers = {
            'Authorization': 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'name': self.name,
            'public': self.public
        }
        url = 'https://api.spotify.com/v1/users/'+AppContext.newuser.user_id+'/playlists'
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response = response.json()
        return response["id"]

    def _add_tracks_to_playlist(self, tracks, playlist_id):
        headers = {
            'Authorization': 'Bearer ' + AppContext.newuser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        pages = int(math.ceil(float(len(tracks)) / 100))
        for i in range(0, pages):
            payload = {
                'uris': tracks[i*100:(i*100)+100]
            }
            print str(len(payload['uris']))
            url = 'https://api.spotify.com/v1/users/'+AppContext.newuser.user_id+'/playlists/'+playlist_id+'/tracks'
            response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
            response = response.json()