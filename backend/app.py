import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import flask
import dotenv
import flask_cors
import openai

# set up api keys and such
dotenv.load_dotenv()
app = flask.Flask(__name__)
flask_cors.CORS(app)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_API_KEY

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



# method that searches the spotify api for the song and returns it 
@app.route("/recommend_song", methods=["POST"])
def search():

    query = flask.request.args.get("query")
    if not query:
        return flask.jsonify({"error": "Missing 'query' parameter"}), 400
    prompt =f"Recommend five songs based on this user's request: {query}"
    try:
         response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
         # TODO: search spotify using chatgpts response
         print("Searching Spotify for:", query)
         results = sp.search(q=query, limit=1, type="track")
         if not results["tracks"]["items"]:
            print("No tracks found for query:", query)
            return flask.jsonify({"error": "Song/artist not found"}), 404
         """
         song = results["tracks"]["items"][0]
         song_id = song["id"]
         artist_id = song["artists"][0]["id"]
         print("Song name is:", song["name"])
         print("By artist:", song["artists"][0]["name"])
         print("Song ID:", song_id)
         print("Artist ID:", artist_id)"
         """
    except Exception as e:
        return flask.jsonify({"error": f"Failed to get song recommendation: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
