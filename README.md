
**DEPRECATED** 

Here is the newer, nodejs version https://github.com/aartek/trikatuka2


# Trikatuka - Spotify playlists migration tool

**Trikatuka** is a tool helping transfer Spotify playlists from one account to another.

- *Collaborative* playlists are followed.
- *Public* and *private* playlists are copied.

## For humans

**Windows users**:

You may download latest release zip with app.exe and run.

**Linux users**:

Already you need to follow the instructions from "For developers" section...

**How to**

1. Go to `http://localhost:7878`
2. Login to previous user
3. Login to new user
4. Select playlists you want to transfer
5. Press transfer and wait.
6. Done!


## For developers

**Requirements**
- `Python 2.7`
- `Web.py` (http://webpy.org/)
- You need to create an app on https://developer.spotify.com/ and get `clientId` and `clientSecret`. You must also add `http://localhost:7878/client_auth_callback` and `http://localhost:7878/user_auth_callback` to urls whitelist.

**How to**

1. Rename `config.cfg.template` to `config.cfg`
2. Fill `clientID` and `clientSecret` fields and save.
3. Run the app (`python app.py`)
