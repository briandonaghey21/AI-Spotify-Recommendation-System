import React, { useState } from "react";
import axios from "axios";
import "../searchStyles.css";
import playIcon from "../spotify_play.png";
import spotifyLogo from "../spotify_logo.png"; 

const SearchSongs = () => {
  const [query, setQuery] = useState("");
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // fetch songs from Flask backend
  const fetchSongs = async () => {
    setError("");
    setLoading(true);
    setSongs([]);

    try {
      const response = await axios.get(`http://127.0.0.1:5000/recommend_song`, {
        params: { query },
      });
      setSongs(response.data);
    } catch (err) {
      setError("Failed to fetch songs. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <img src={spotifyLogo} alt="Spotify Logo" className="spotify-logo" />
        <h1>AI-Powered Song Recommender</h1>
      </div>

      <div className="search-container">
        <div className="search-box">
          <input
            type="text"
            className="search-input"
            placeholder="What do you want to play?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="search-button" onClick={fetchSongs} disabled={loading}>
            <img src={playIcon} alt="Play" className="play-icon" />
          </button>
        </div>
      </div>

      {loading && <p>Loading songs...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}


      <div className="songs-grid">
        {songs.map((song, index) => (
          <div key={index} className="song-card">
            <img src={song.album_cover} alt={song.song_name} />
            <strong>{song.song_name}</strong> 
            <p>{song.artist}</p>
            <a href={song.spotify_url} target="_blank" rel="noopener noreferrer">
              Listen on Spotify
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchSongs;
