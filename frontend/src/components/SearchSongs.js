import { useState } from "react";
import axios from "axios";

function SearchSongs() {
    const [query, setQuery] = useState("");
    const [songs, setSongs] = useState([]);

    const fetchSongs = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/recommend_song?query=${query}`);
            setSongs(response.data);
        } catch (error) {
            console.error("Error fetching songs:", error);
        }
    };

    return (
        <div>
            <h2>Song Recommender</h2>
            <input 
                type="text" 
                value={query} 
                onChange={(e) => setQuery(e.target.value)} 
                placeholder="Enter song preference"
            />
            <button onClick={fetchSongs}>Search</button>
            <ul>
                {songs.map((song, index) => (
                    <li key={index}>
                        {song.song_name} - {song.artist}
                        <a href={song.spotify_url} target="_blank" rel="noopener noreferrer"> 🎵</a>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default SearchSongs;
