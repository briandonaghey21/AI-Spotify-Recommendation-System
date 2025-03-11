import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import flask
import dotenv
import flask_cors
from openai import OpenAI

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

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o",
    store=True,
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)

# method where a user inputs a song and chatgpt recommends it 
@app.route("/search",methods=["GET"])
def recommend():


# method that searches the spotify api for the song and returns it 
@app.route("/recommend", methods=["POST"])
def search():

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

if __name__ == "__main__":
    app.run(debug=True)
