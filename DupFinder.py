import os
from click import prompt
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# PLAYLIST_ID = '3iU6jJrwrAdGCT3W7JWPOY'

PLAYLIST_ID = prompt('Enter Playlist ID')

pl = sp.playlist(PLAYLIST_ID)

print('Retrieved playlist', pl['name'])

pl_tracks = sp.playlist_tracks(PLAYLIST_ID)
print('Found', pl_tracks['total'], 'tracks')

pl_tracks_items = pl_tracks['items']


offset = 0
while(pl_tracks['next'] != None):
    offset += 100
    pl_tracks = sp.playlist_tracks(PLAYLIST_ID, offset=offset)
    pl_tracks_items += pl_tracks['items']

seen = dict()
dups = set()

for i, tk in enumerate(pl_tracks_items):
    if tk['track']['name'] in seen:
        dups.add(tk['track']['name'])
        seen[tk['track']['name']].append((i, tk))
    else:
        seen[tk['track']['name']] = [(i, tk)]

to_remove = []

print(dups)

print('Found duplicates:')
for dup in dups:
    print(dup)

    tracks = seen[dup]
    for i, track in tracks:
        print(i+1, ':', track['track']['external_urls'])

    keep = prompt('keep')
    
    if keep == 'a' or keep == 'A' or keep == 'all':
        continue
    else:
        keep = int(keep)

        if keep >= len(tracks):
            keep = int(prompt('Enter a valid index'))

        for i, (j, track) in enumerate(tracks):
            if i != keep:
                print('Removing', j+1, track['track']['uri'])
                to_remove.append({"uri":track['track']['uri'],"positions":[j]})

sp.playlist_remove_specific_occurrences_of_items(PLAYLIST_ID, to_remove)