import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required, logout_user
from app import app
from app.models import User, db



SPOTIPY_CLIENT_ID = '24f5696040ef42d6a4d1e90f7b55da4d'
SPOTIPY_CLIENT_SECRET = "7b3a085bf59e40d29d14646f81a5e24b"
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/spotify_callback'

sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-top-read')



@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')



@app.route('/spotify_login')
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)



@app.route('/spotify_callback')
def spotify_callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    access_token = token_info['access_token']

    sp = spotipy.Spotify(auth=access_token)
    user_info = sp.me()

    user = User.query.filter_by(spotify_id=user_info['id']).first()

    if not user:
        user = User(username=user_info['display_name'], spotify_id=user_info['id'])
        db.session.add(user)
        db.session.commit()


    login_user(user)

    flash('Successfully logged in with Spotify!', 'success')
    return redirect(url_for('home'))




@app.route('/logout')
@login_required
def logout():
    flash('Successfully logged out!', 'warning')
    logout_user()
    return redirect(url_for('home'))
    


@app.route('/discover')
def discover():
    return render_template('discover.html')



@app.route('/recently_played')
def recently_played():
    return render_template('recently-played.html')




@app.route('/lyrics')
def lyrics():
    return render_template('lyrics.html')



@app.route('/topartists')
@login_required
def topArtists():
    if not current_user.is_authenticated:
        return redirect(url_for('spotify_login'))


    token_info = sp_oauth.get_access_token(user=current_user)
    access_token = token_info['access_token']

    
    sp = spotipy.Spotify(auth=access_token)

    
    top_artists = sp.current_user_top_artists(limit=15)

    artists_info = []
    for artist in top_artists['items']:
        artists_info.append({
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,
            'popularity': artist['popularity'],
        })

    return render_template('artists.html', top_artists=artists_info)








@app.route('/topgenres')
def topGenres():
    return render_template('genres.html')



@app.route('/toptracks')
def topTracks():
    return render_template('songs.html')