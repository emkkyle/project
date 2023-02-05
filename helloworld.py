import os
from flask import Flask, session, render_template, request, redirect
from flask_session import Session
import spotipy
import spotipy.util as util

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session'
Session(app)


@app.route("/")
def signin():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-private, user-read-email, playlist-read-private, user-top-read',
                                                cache_handler=cache_handler,
                                                show_dialog=True)
    
    if request.args.get("code"):
        auth_manager.get_access_token(request.arg.get("code"))
        return redirect("/")
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \
    
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/result")
def result():
    output = request.form.to_dict()
    user = output["user"]

if __name__=="__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8888)