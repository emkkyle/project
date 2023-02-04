import requests
import json
import webbrowser
import matplotlib.image as img
import urllib
import os
import io
import sys
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from json.decoder import JSONDecodeError
from urllib.request import urlopen
from pprint import pprint
from PIL import Image

#if len(sys.argv) > 1:
#    username = sys.argv[1]
#else:
#    print("Whoops, need a username!")
    
username = input("What is your user? ")
#username = 'nqppwjraxdwti11bc43ta2z8r'
scope = 'user-read-private, user-read-email, playlist-read-private, user-top-read'
client_id = '9bddb30b534d4f77ba81842887740305'
client_secret = 'df588f5407d74e3bb29a338b8875f84b'
redirect_uri = 'https://localhost:8888/callback'

try: 
    token = util.prompt_for_user_token(username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
except:
    os.remove(f".cache-nqppwjraxdwti11bc43ta2z8r")
    token = util.prompt_for_user_token(username)

client_credentials_manager = SpotifyClientCredentials()
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp = spotipy.Spotify(auth=token)

user = sp.current_user()

print('hi ' + user['display_name'] +'!\n')

search_str = 'sheinnovates sample playlist emily'
result = sp.search(search_str, type='playlist')
#print(result)

#print(json.dumps(result, sort_keys=True, indent=4))

x = 0
count = 0
final_list_values = {}

for i in result['playlists']['items']:
    if(i['name'] != search_str):
        #print(i['name'])
        #print('sorry :/( we cant find your playlist. make sure you spelled everything right!')
        continue
    playlist_id = i['uri']
    playlist_tracks = sp.playlist_items(playlist_id, fields='items.track.name,items.track.id,items.track.album.images,items.track.artists,total',additional_types=['track'])
    #print(json.dumps(playlist_tracks, sort_keys=True, indent=4))
    for s in playlist_tracks['items']:
        R = 0
        G = 0
        B = 0
        pixel_count = 0
        color_dict = {}
        
        track_name = s['track']['name']
        
        #get album image url
        images = s['track']['album']['images'][0]['url'] 
        
        #gets album image height and width (usually 640x640)
        image_height = s['track']['album']['images'][0]['height']
        image_width = s['track']['album']['images'][0]['width']
        artist = ''
        
        a = 0
        for arts in s['track']['artists']:
            if (a == 0):
                artist += arts['name']
            else:
                artist += ', '
                artist += arts['name']
            a+=1
        track_image = io.BytesIO(urllib.request.urlopen(images).read())
        img = Image.open(track_image)

        print(track_name)
        #print(json.dumps(s['track']['artists'], sort_keys=True, indent=4))
        
        pixels = list(img.getdata())
        for x in range(image_width):
            for y in range(image_height):
                #print(x, y)
                try:
                    curr = img.getpixel((x,y))
                except IndexError:
                    continue
                #R += curr[0]
                #G += curr[1]
                #B += curr[2]
                pixel_count += 1
                if curr in color_dict:
                    color_dict[curr] = color_dict[curr] + 1
                else:
                    color_dict[curr] = 1
        sorted_color_dict = sorted(color_dict.items(), key = lambda x:x[1], reverse = True)

        one = 0
        for key, value in sorted_color_dict:
            if one < 1:
                main_color_value = key
            else:
                break
        
        features = sp.audio_features(s['track']['id'])
        valence = features[0]['valence']
    
        items_list = [main_color_value, valence, artist]

        final_list_values[track_name] = items_list

    # else:
    #    break
    # count+=1
    print(final_list_values)
    break
