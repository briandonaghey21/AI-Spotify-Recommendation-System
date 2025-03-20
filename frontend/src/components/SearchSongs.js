import React, { useState } from "react";
import axios from "axios";
import "../searchStyles.css";
import { motion } from "framer-motion";
import playIcon from "../spotify_play.png";
import spotifyLogo from "../spotify_logo.png"; 

const SearchSongs = () => {
  const [query, setQuery] = useState("");
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch songs from Flask backend
  const fetchSongs = async () => {
    setError("");
    setLoading(true);
    setSongs([]);

    
    try {
      const response = await axios.get(`https://ai-spotify-recommendation-system.onrender.com/recommend_song`, {
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
            placeholder="Give me a phrase to generate song predictions."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="search-button" onClick={fetchSongs} disabled={loading}>
            <img src={playIcon} alt="Play" className="play-icon" />
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
          </div>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}

      <div className="songs-grid">
        {songs.map((song, index) => (
          <motion.div
            key={index}
            className="song-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.001}}
            whileHover={{ scale: 1.1 }}
          >
            <a href={song.spotify_url} target="_blank" rel="noopener noreferrer">
              <img src={song.album_cover} alt={song.song_name} className="album-cover"/>
              <strong>{song.song_name}</strong>
              <p>{song.artist}</p>
              <button className="listen-button">Listen on Spotify</button>
            </a>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default SearchSongs;
