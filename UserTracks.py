import logging
import AppContext
import requests
import sys
import json
import math
__all__ = ['UserTracks']


class UserTracks:
    def __init__(self):
        pass

    def copy_tracks(self, old_user, new_user):
        tracks = self.get_tracks(old_user)
        self._save_tracks_for_user(tracks, new_user)

    def get_tracks(self, user):
        items = []
        items = self._fetch_tracks(user.user_id, items, 0)
        return items

    def _fetch_tracks(self, user_id, items, offset):
        headers = {
            'Authorization': 'Bearer ' + AppContext.olduser.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'fields': 'total,items(track.uri)',
            'offset': offset,
            'limit': 50
        }
        url = 'https://api.spotify.com/v1/me/tracks'
        response = requests.get(url, params=payload, headers=headers, verify=False)
        response = response.json()

        for item in response['items']:
            items.append(item['track']['id'])

        total = response['total']
        if len(items) < total:
            self._fetch_tracks(user_id, items, offset + 50)

        return items

    def _save_tracks_for_user(self, tracks, user):
        url = 'https://api.spotify.com/v1/me/tracks'

        headers = {
            'Authorization': 'Bearer ' + user.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        pages = int(math.ceil(float(len(tracks)) / 50))
        for i in range(0, pages):
            payload = tracks[i*50:(i*50)+50]
            requests.put(url, data=json.dumps(payload), headers=headers, verify=False)