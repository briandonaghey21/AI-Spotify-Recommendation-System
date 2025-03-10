import spotipy
import spotipy.oauth2
import os
import flask
import dotenv
import flask_cors

dotenv.load_dotenv()

app = flask.Flask(__name__)

flask_cors.CORS(app)