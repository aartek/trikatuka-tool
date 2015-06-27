**Trikatuka** is a tool helping transfer Spotify playlists from one account to another.

- *Collaborative* playlists are followed.
- *Public* and *private* playlists are copied.

**Requirements**

- `Python 2.7`
- `Web.py` (http://webpy.org/)
- You need to create an app on https://developer.spotify.com/ and get `clientId` and `clientSecret`

**Instructions**

1. Rename `config.cfg.template` to `config.cfg`
2. Fill `clientID` and `clientSecret` fields and save.
3. Run the app (`python app.py`)
4. Go to `http://localhost:7878`
5. Login to previous user
6. Login to new user
7. Select playlists you want to transfer
8. Press transfer and wait.
9. Done!

**Known bugs**

No paging support yet, so app already can display only 100 playlists, and can copy only first 100 tracks of each playlist.

