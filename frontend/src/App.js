import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const handleQueryChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearch = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/recommend', { query });
            setResults(response.data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }
    };

    return (
        <div className="App">
            <h1>Restaurant Recommender</h1>
            <input
                type="text"
                value={query}
                onChange={handleQueryChange}
                placeholder="What are you craving?"
            />
            <button onClick={handleSearch}>Search</button>
            <div>
                <h2>Recommendations:</h2>
                <ul>
                    {results.map((result, index) => (
                        <li key={index}>
                            <strong>{result.name}</strong> - {result.categories} (Score: {result.score.toFixed(2)})
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default App;
