import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import flask
import dotenv
import flask_cors
import openai
import json 
import nltk

from nltk.corpus import stopwords
from textblob import TextBlob
import spacy

#todo: set up nlp

# set up api keys and such
dotenv.load_dotenv()
app = flask.Flask(__name__)
flask_cors.CORS(app)
nlp = spacy.load("en_core_web_sm")
nltk.download('stopwords')


SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
BAD_SONGS_FILE = "bad_songs.json"

openai.api_key = os.getenv("OPENAI_KEY")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise ValueError("Missing credentials")

# authenticate with spotify API
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    ))
    print("spotify authentication successful!")
except spotipy.SpotifyException as e:
    print("spotify authentication failed:", e)
    exit(1)


# NLP function to clean and analyze query
def process_query(user_query):

    user_query = user_query.lower()
    # tokenization
    words = [word for word in user_query.split() if word not in stopwords.words('english')]

    # gets keywords like genre, artist, etc.
    doc = nlp(user_query)
    entities = {ent.label_: ent.text for ent in doc.ents}
    # positive, negative, neutral songs
    sentiment_score = TextBlob(user_query).sentiment.polarity
    sentiment = "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"

    return {
        "cleaned_query": " ".join(words),
        "entities": entities,
        "sentiment": sentiment
    }

# this is our bad song database, safely loads bad_songs.json
def load_bad_songs():
    try:
        with open(BAD_SONGS_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return []  # Return an empty list if the file is empty
            return json.loads(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# saves bad songs into bad_songs.json
def logBadSong(song, artist, query):
    bad_songs = load_bad_songs()
    
    # Prevent duplicate bad songs
    for entry in bad_songs:
        if entry["song_name"] == song and entry["artist_name"] == artist:
            return

    bad_songs.append({
        "song_name": song,
        "artist_name": artist,
        "query": query
    })

    with open(BAD_SONGS_FILE, "w") as f:
        json.dump(bad_songs, f, indent=4)


# method that searches the spotify API for the song and returns it
def searchSpotify(song, artist):
    query = f"track:{song} artist:{artist}"  
    results = sp.search(q=query, limit=1, type="track")

    if results["tracks"]["items"]:
        song = results["tracks"]["items"][0]
        album_images = song["album"]["images"]  
        return {
            "song_name": song["name"],
            "artist": song["artists"][0]["name"],
            "album": song["album"]["name"],
            "spotify_url": song["external_urls"]["spotify"],
            "album_cover": album_images[0]["url"]
        }
    return None


# method that searches chatgpt for song recommendations and validates them on spotify
@app.route("/recommend_song", methods=["GET"])
def search():
    bad_songs = load_bad_songs()
    excluded_songs = [f"{entry['song_name']} - {entry['artist_name']}" for entry in bad_songs]

    query = flask.request.args.get("query")
    processed_query = process_query(query)
    genre = processed_query["entities"].get("GENRE")
    artistQ = processed_query["entities"].get("PERSON")  # SpaCy often tags artists as PERSON
    sentiment = processed_query["sentiment"]
    
    if not query:
        return flask.jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        songs_info = []
        while len(songs_info) < 10:
            prompt = f"""
            Recommend fifteen real and popular songs available on Spotify based on this request: '{query}'.
            Format each recommendation exactly as 'Song Name ; Artist' on a new line.
            Do not say anything else besides the recommendations and do not include numbers in the recommendation
            Do not make up fake songs or artists.
            If an artist is featured in the song, do not include it.
            Consider these factors: 
                - Sentiment: {sentiment} mood
                - Preferred Genre: {genre if genre else "Any"}
                - Artist preference: {artistQ if artistQ else "Any"}
            Do not include these songs, as they are either nonexistent, disliked, or already recommended: {', '.join(excluded_songs)}.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )

            ai_response = response["choices"][0]["message"]["content"]
            print(f"Response to prompt:\n{ai_response}")  # prints ai response to debug

            lines = ai_response.split("\n")
            for recommendation in lines:
                info = recommendation.split(";")
                if len(info) == 2:
                    song = info[0].strip()
                    artist = info[1].strip()
                    print(f"Verifying '{song}' by '{artist}' exists...")

                    song_info = searchSpotify(song, artist)
                    if song_info:
                        print("Song successfully found")
                        songs_info.append(song_info)
                        excluded_songs.append(f"{song} - {artist}")
                    else:
                        print("Song not found.")
                        logBadSong(song, artist, query)
                else:
                    print("Skipping invalid line generated by OpenAI")

        return flask.jsonify(songs_info)

    except Exception as e:
        return flask.jsonify({"error": f"Failed to get song recommendation: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
