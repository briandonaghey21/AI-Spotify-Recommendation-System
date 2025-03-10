import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import flask
import dotenv
import flask_cors

dotenv.load_dotenv()

app = flask.Flask(__name__)

flask_cors.CORS(app)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise ValueError("Missing credentials")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    ))
    print("spotify authentication successful!")
except spotipy.SpotifyException as e:
    print("spotify authentication failed:", e)
    exit(1)

# this recommends a song using just the spotify api
# input the artist name and the song name to get accurate results  
@app.route("/recommend", methods=["POST"])
def recommend():

    data = flask.request.json

    song_name = data.get("song")
    artist_name = data.get("artist")

    query = f"{song_name} {artist_name}" if artist_name else song_name
    print("Searching Spotify for:", query)

    results = sp.search(q=query, limit=1, type="track")

    if not results["tracks"]["items"]:
        print("No tracks found for query:", query)
        return flask.jsonify({"error": "Song/artist not found"}), 404
    
    song = results["tracks"]["items"][0]
    song_id = song["id"]
    artist_id = song["artists"][0]["id"]

    print("Song name is:", song["name"])
    print("By artist:", song["artists"][0]["name"])
    print("Song ID:", song_id)
    print("Artist ID:", artist_id)

    artist_info = sp.artist(artist_id)
    genres = artist_info.get("genres", [])
    genre_seed = genres[0] if genres else "pop"



    try:
        recommendations = sp.recommendations(
            seed_tracks=[song_id], 
            seed_artists=[artist_id],  
            limit=5
        )

        if not recommendations["tracks"]:
            print("No recommendations found for the given track.")
            return flask.jsonify({"error": "no recommendations found"}), 404

    except spotipy.exceptions.SpotifyException as e:
        print("Spotify error:", e)
        return flask.jsonify({"error": "Spotify API error. Could not get recommendations."}), 500

    recommended_JSON = [
        {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "spotify_url": track["external_urls"]["spotify"],
            "preview_url": track["preview_url"]
        }
        for track in recommendations["tracks"]
    ]
    
    return flask.jsonify(recommended_JSON)

if __name__ == "__main__":
    app.run(debug=True)
