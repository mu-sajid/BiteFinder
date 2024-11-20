import React, { useState } from 'react';
import axios from 'axios';
import GooglePlacesAutocomplete from 'react-google-places-autocomplete';
import './SearchPage.css';
import { loadGoogleMapsAPI } from './LoadGoogle';
import Logo from './file.png'


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
    setLoading(true);
    setError(null);
    try {
      const data = {
        query: query,
        lat: geolocation?.lat || 0,
        lng: geolocation?.lng || 0,
      };
      const response = await axios.post('https://backendbitefinder-ad6c593f7e29.herokuapp.com/recommend', { data });
      setResults(response.data);
    } catch (err) {
      setError('Error fetching recommendations');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLocation = async (newLocation) => {
    setLocation(newLocation);
    loadGoogleMapsAPI(API_KEY, ['places']).then(async (google) => {
      const { Place } = await google.maps.importLibrary('places');
      const place = new Place({
        id: newLocation.value.place_id,
        requestedLanguage: 'en',
      });
      await place.fetchFields({
        fields: ['displayName', 'location'],
      });
      setGeoLocation(place.Eg.location);
    });
  };

  return (
    <div className="search-page">
  <header className="app-header">
    <img src={Logo} alt="BiteFinder Logo" className="logo" />
    <h1>BiteFinder</h1>
    <div className="location">
      <GooglePlacesAutocomplete
        apiKey={API_KEY}
        selectProps={{
          location,
          onChange: handleUpdateLocation,
          placeholder: 'Enter your location...',
        }}
      />
    </div>
  </header>


      <div className="search-bar">
      <label className="search-label">I'm feeling hungry for...</label>
      <div className="search-input-container">
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Type cuisine or dish"
          className="search-input"
        />
        <button onClick={handleSearch} className="search-button">Search</button>
      </div>
    </div>

      {loading && <p className="loading">Loading recommendations...</p>}
      {error && <p className="error">{error}</p>}

      <div className="results">
        {results.length === 0 && !loading && !error && <p>No recommendations yet. Try searching for something!</p>}
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <img src={result.image} alt={result.name} className="result-image" />
            <div className="result-info">
              <h2>{result.name}</h2>
              <p>{result.categories}</p>
              <p style={{ color: result.is_open ? 'green' : 'red' }}>{result.is_open ? 'Open Now' : 'Closed'}</p>
            </div>
            <div className="result-meta">
              <span>
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${result.name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on Maps
                </a>
              </span>
              <span>{result.price*"$" || '$$'}</span>
              <span>Rating: {result.rating !== 'N/A' ? `${result.rating} ⭐` : 'N/A'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchPage;
