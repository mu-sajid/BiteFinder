import React, { useState } from 'react';
import axios from 'axios';
import './SearchPage.css';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/recommend', { query });
      setResults(response.data);
    } catch (err) {
      setError('Error fetching recommendations');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-page">
      <header>
        <h1>Bite Finder</h1>
        <div className="location">Location: College Station</div>
      </header>

      <div className="search-bar">
        <label>I'm feeling hungry for...</label>
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Type cuisine or dish"
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {loading && <p className="loading">Loading recommendations...</p>}
      {error && <p className="error">{error}</p>}

      <div className="results">
        {results.length === 0 && !loading && !error && <p>No recommendations yet. Try searching for something!</p>}
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="result-info">
              <h2>{result.name}</h2>
              <p>{result.categories}</p>
            </div>
            <div className="result-meta">
              <span>{result.distance_km} km</span>
              <span>{result.price || "$$"}</span>
              <span>Score: {result.score.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchPage;
