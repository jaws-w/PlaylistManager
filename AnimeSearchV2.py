from platform import release
import re
from jikanpy import Jikan
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SHOW_SEARCH_RESULTS = 10
jikan = Jikan()

load_dotenv()

MARKET_CODE = 'us'
scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user_id = sp.current_user()['id']


def main():

    anime_name = input("Anime Title: ")
    # anime_name = 'sword art online'
    search_result = search_anime(anime_name, 1)

    anime = jikan.anime(search_result['mal_id'])

    # print(anime)

    tracks = get_tracks(anime)

    # print(tracks)

    playlist = get_playlist(anime_name)

    sp.playlist_add_items(playlist_id=playlist['id'], items=[track['id'] for track in tracks])

def parse_sp_serach(response):
    string_res = ""
    
    track_name = response['name']
    if track_name != None:
        string_res += track_name

    album_name = response['album']['name']
    if track_name != None:
        string_res += ' ' + album_name

    artist_names = []
    for artist in response['artists']:
        artist_names.append(artist['name'])

    if artist_names:
        string_res += ' by '

        for artist in artist_names:
            string_res += artist + ' '

    release_date = response['album']['release_date']
    if release_date != None:
        string_res += 'released on ' + release_date
    
    link = response['preview_url']
    if link != None:
        string_res += '\npreview at ' + link
    return string_res + '\n'

def parse_track(track):
    info = re.split('"|by', track)
    title = info[1]
    artist = info[3].split('\xa0')[0][1:]
    return (title, artist)

def get_playlist(anime_name):
    new_pl = input('Create new playlist? (y/n/playlist_id) ')

    if new_pl == 'y':
        playlist_title = input('Playlist Title: ')
        playlist = sp.user_playlist_create(user=user_id, name=playlist_title, public=False, description='Auto generated playlist for {}'.format(anime_name))
    elif new_pl == 'n':
        playlists = sp.current_user_playlists()
        for i, pl in enumerate(playlists['items']):
            print(i+1, pl['name'])
        pl_sel = int(input('Enter the playlist you want to add to'))
        playlist = playlists['items'][pl_sel-1]
    else:
        playlist = sp.playlist(new_pl)
    return playlist

def get_tracks(anime):

    sp_tracks = []

    print('Ops and Eds in', anime['title'], ':')

    tracks = set()
    
    for track in anime['opening_themes']:
        # info = track.replace(u'\xa0', u' ').split(' by ')
        tracks.add(parse_track(track))

    for track in anime['ending_themes']:
        tracks.add(parse_track(track))
    
    print(tracks)


    for track in tracks:
        print('Searching for', track[0], 'by', track[1])
        query = 'track:{}+artist:{}'.format(track[0], track[1])
        res = sp.search(query, type='track', market=MARKET_CODE)
        if res['tracks']['items']:
            for i, tr in enumerate(res['tracks']['items']):
                r = parse_sp_serach(tr)
                print(i+1, r)
            selection = input()
            if selection == 'n':
                continue
            else:
                try:
                    sp_tracks.append(res['tracks']['items'][int(selection)-1])
                except:
                    print('invalid input')
                    exit()
        else:
            print('no tracks found for', track[0], 'by', track[1])
            input('press any key to continue')

    return sp_tracks


def search_anime(anime_name, page_num):
    search_result = jikan.search('anime', anime_name, page=page_num)

    for i, anime in enumerate(search_result['results']):
        print(i+1, ')',anime['title'])

    while True:
        sel = input('Select result or different page: ')
        if sel == 'p':
            if page_num == 1:
                print('no previous page')
            else:
                return search_anime(anime_name, page_num-1)
        elif sel == 'n':
            if page_num + 1 >= search_result['last_page']:
                print('no next page')
            else:
                return search_anime(anime_name, page_num+1)
        else:
            try:
                return search_result['results'][int(sel)-1]
            except ValueError:
                print('Enter a valid input')


if __name__ == '__main__':
    main()