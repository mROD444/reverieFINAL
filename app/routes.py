import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import render_template, redirect, url_for, flash, request, send_file, session
from flask_login import login_user, current_user, login_required, logout_user
from app import app
from app.models import User, db, Song



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
    session.clear()
    return redirect(url_for('home'))
    



@app.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    static_song_list = ['Song 1', 'Song 2', 'Song 3', 'Song 4']

    spotify_song_list = []
    if request.method == 'POST':
        song_search = request.form['song_search']
        rating = int(request.form['rating'])
        description = request.form['description']

        new_song = Song(title=song_search, rating=rating, description=description, user_id=current_user.id)

        current_user.songs.append(new_song)

        db.session.add(new_song)
        db.session.commit()

        return redirect(url_for('discover'))

    return render_template('discover.html', static_song_list=static_song_list, spotify_song_list=spotify_song_list )







def get_recently_played_tracks():
    token_info = sp_oauth.get_cached_token()

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    time_period = 'pasthour'

    time_range_map = {
        'pasthour': 'short_term',
    }

    range_param = time_range_map.get(time_period, 'short_term')
    try:
        results = sp.current_user_recently_played(limit=25, time_range=range_param)
        recently_played_tracks = results['items']
    except Exception as e:
        print(f"Error fetching recently played tracks: {e}")
        recently_played_tracks = []

    return recently_played_tracks


@app.route('/recently_played')
@login_required
def recently_played():
    if not current_user.is_authenticated:
        return redirect(url_for('spotify_login'))
    
    recently_played_tracks = get_recently_played_tracks()
    print(recently_played_tracks)
    return render_template('recently-played.html', recently_played_tracks=recently_played_tracks)





@app.route('/lyrics')
def lyrics():
    return render_template('lyrics.html')






@app.route('/topartists')
@login_required
def topArtists():
    if not current_user.is_authenticated:
        return redirect(url_for('spotify_login'))

    time_period = request.args.get('time_period', 'short_term')

    token_info = sp_oauth.get_cached_token()
    
    if not token_info:
        return redirect(url_for('spotify_login'))

    access_token = token_info['access_token']

    sp = spotipy.Spotify(auth=access_token)

    time_range_map = {
        'past2weeks': 'short_term',
        'past6months': 'medium_term',
        'lifetime': 'long_term',
    }

    range_param = time_range_map.get(time_period, 'short_term')

    top_artists = sp.current_user_top_artists(limit=15, time_range=range_param)

    artists_info = []
    for artist in top_artists['items']:
        artists_info.append({
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,
            'popularity': artist['popularity'],
        })

    return render_template('artists.html', top_artists=artists_info, time_period=time_period)







@app.route('/topgenres')
@login_required
def topGenres():
    if not current_user.is_authenticated:
        return redirect(url_for('spotify_login'))

    time_period = request.args.get('time_period', 'short_term')

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        return redirect(url_for('spotify_login'))

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    time_range_map = {
        'past2weeks': 'short_term',
        'past6months': 'medium_term',
        'lifetime': 'long_term'
    }

    range_parameter = time_range_map.get(time_period, 'short_term')

    top_artists = sp.current_user_top_artists(limit=15, time_range=range_parameter)

    top_genres = set()  # Use a set to eliminate duplicates

    for artist in top_artists['items']:
        genres = artist.get('genres', [])
        top_genres.update(genres)

    genre_info = [{'name': genre} for genre in top_genres]

    return render_template('genres.html', top_genres=genre_info, time_period=time_period)





@app.route('/toptracks')
@login_required
def topTracks():
    if not current_user.is_authenticated:
        return redirect(url_for('spotify_login'))
    
    time_period = request.args.get('time_period', 'short_term')

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        return redirect(url_for('spotify_login'))
    
    access_token = token_info['access_token']

    sp = spotipy.Spotify(auth=access_token)

    time_range_map = {
        'past2weeks': 'short_term',
        'past6months': 'medium_term',
        'lifetime': 'long_term',
    }

    range_param = time_range_map.get(time_period, 'short_term')

    top_tracks = sp.current_user_top_tracks(limit=15, time_range=range_param)

    track_info = []
    for track in top_tracks['items']:
        track_info.append({
            'name': track['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
        })


    return render_template('songs.html', top_tracks=track_info, time_period=time_period)


