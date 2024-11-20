import React, { useState } from 'react';
import axios from 'axios';
import GooglePlacesAutocomplete from 'react-google-places-autocomplete';
import './SearchPage.css';
import { loadGoogleMapsAPI } from './LoadGoogle';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState(null);
  const [geolocation, setGeoLocation] = useState(null);
  const API_KEY = process.env.REACT_APP_GCLOUD_API;

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSearch = async () => {
    if (!geolocation) {
      setError('Please select a location first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = {
        query,
        lat: geolocation.lat,
        lng: geolocation.lng,
      };
      const response = await axios.post('http://127.0.0.1:5000/recommend', { data });
      setResults(response.data);
    } catch (err) {
      setError('Error fetching recommendations.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLocation = async (newLocation) => {
    setLocation(newLocation);

    const lat = newLocation?.value?.geometry?.location?.lat;
    const lng = newLocation?.value?.geometry?.location?.lng;

    setGeoLocation({ lat, lng });
  };

  return (
    <div className="search-page">
      <header>
        <h1>Bite Finder</h1>
        <div className="location">
          <GooglePlacesAutocomplete
            apiKey={API_KEY}
            selectProps={{
              value: location,
              onChange: handleUpdateLocation,
              placeholder: 'Enter your location...',
            }}
          />
        </div>
      </header>

      <div className="search-bar">
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="I'm feeling hungry for..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {loading && <p className="loading">Loading recommendations...</p>}
      {error && <p className="error">{error}</p>}

      <div className="results">
        {results.length === 0 && !loading && !error && (
          <p>No recommendations yet. Try searching for something!</p>
        )}
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="result-info">
              <h2>{result.name}</h2>
              <p>{result.categories}</p>
            </div>
            <div className="result-meta">
              <span className="distance">{result.distance_km} km</span>
              <span className="price">{result.price || '$$'}</span>
              <span className="score">Score: {result.score.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchPage;
