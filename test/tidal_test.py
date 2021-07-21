import tidalapi
from tidalapi import Config


session = tidalapi.Session()
session.login('ariel.boukris@outlook.com', 'zYSA7Q5nyKQQAMs')
tracks = session.get_album_tracks(album_id=16909093)
for track in tracks:
    print(track.name)