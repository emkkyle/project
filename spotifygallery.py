import os
from flask import Flask, session, render_template, request, redirect
from flask_session import Session
import spotipy
import spotipy.util as util
import requests
import json
import webbrowser
import matplotlib.image as img
import urllib
import io
import sys
from spotipy.oauth2 import SpotifyClientCredentials
from json.decoder import JSONDecodeError
from urllib.request import urlopen
from pprint import pprint
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session'
Session(app)

CLIENT_SIDE_URL = "http://localhost:8888"
PORT = 8888

cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
auth_manager = spotipy.oauth2.SpotifyOAuth(redirect_uri='http://localhost:8888/callback', scope='user-read-private, user-read-email, playlist-read-private, user-top-read',
                                           cache_handler=cache_handler,
                                           show_dialog=True)

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect("/signin")

@app.route('/signin', methods = ['POST', 'GET'])
def signin():

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/signin')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template("index.html", auth_url = auth_url)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/result')


@app.route('/result', methods=['POST', 'GET'])
def result():
    #return f'<a href="/search">search</a> | '
    return render_template("login.html")


@app.route('/search', methods=['POST', 'GET'])
def search():
    
    if request.method == 'GET':
        return f"cannot access data"
    if request.method == 'POST':
        form_data = request.form
        
    playlist_id = form_data.getlist('Search')[0].replace(
        "https://open.spotify.com/playlist/", "spotify:playlist:").split("?", 1)[0]
    #print(playlist_id)

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/signin')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    #search_str = 'sheinnovates sample playlist emily'
    #result = sp.search(search_str, type='playlist')
    #x = 0

    res = sp.playlist_items(playlist_id=playlist_id,
                            fields='items.track.name,items.track.id,items.track.album.images,items.track.artists,total', limit=20, offset=0, additional_types=['track'])
    
    final_list_values = {}
    total = res['total']
    for s in res['items']:
        R = 0
        G = 0
        B = 0
        pixel_count = 0
        color_dict = {}

        track_name = s['track']['name']

        # get album image url
        images = s['track']['album']['images'][0]['url']

        # gets album image height and width (usually 640x640)
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
            a += 1
        track_image = io.BytesIO(urllib.request.urlopen(images).read())
        img = Image.open(track_image)


        pixels = list(img.getdata())
        for x in range(image_width):
            for y in range(image_height):
                try:
                    curr = img.getpixel((x, y))
                except IndexError:
                    continue
                pixel_count += 1
                if curr in color_dict:
                    color_dict[curr] = color_dict[curr] + 1
                else:
                    color_dict[curr] = 1
        sorted_color_dict = sorted(
            color_dict.items(), key=lambda x: x[1], reverse=True)

        one = 0
        for key, value in sorted_color_dict:
            if one < 1:
                main_color_value = key
            else:
                break

        features = sp.audio_features(s['track']['id'])
        valence = features[0]['valence']
        if 0 < valence <= 0.25:
            valence = 0
        elif 0.25 < valence <= 0.5:
            valence = 1
        elif 0.5 < valence <= 0.75:
            valence = 2
        else:
            valence = 3
        

        items_list = [main_color_value, valence, artist]

        final_list_values[track_name] = items_list

        #print(json.dumps(final_list_values, sort_keys=True, indent=4))
        #break
    avg_val = 0
    for val in final_list_values:
        avg_val+=final_list_values[val][1]
    avg_val = round(avg_val/total)
    print(avg_val)
    #return render_template('resultPage.html', final_list_values = final_list_values, avg_val = avg_val)
    return final_list_values

@app.route('/sign_out')
def sign_out():
    session.clear()
    session.pop("token_info", None)
    return redirect('/')


@app.route('/callback', methods=['POST', 'GET'])
def callback():
    #return render_template("selectionPage.html")
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/signin')  

if __name__=="__main__":
    app.run(threaded=True, port=8888)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8888)