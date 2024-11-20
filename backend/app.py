from flask import Flask, request, jsonify
from vsm_scorer import VSMScorer
from data_parser import DataParser
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
CORS(app)

global documents

data_parser = DataParser("yelp_academic_dataset_business.json")
data_parser.load_data()
#documents = data_parser.get_documents()
scorer = VSMScorer(data_parser.idfs, title_weight=0.5, body_weight=0.5)

load_dotenv()
API_KEY = os.getenv('GCLOUD_API')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    data2 = data.get('data')
    query = data2.get('query', '')
    location_lat = float(data2.get('lat', 0))  # Convert to float
    location_lng = float(data2.get('lng', 0))
    search_range = 5000.0  # 5km radius

    # Correct Places API Endpoint
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{location_lat},{location_lng}",
        "radius": search_range,
        "type": "restaurant",
        "keyword": query,
        "key": API_KEY
    }

    # Fetch places from Google Places API
    places_result = requests.get(url, params=params).json()

    # Parse results into documents
    documents = []
    seen_names = set()  # Track unique names
    if "results" in places_result:
        for place in places_result['results']:
            name = place.get('name', "Unknown")
            if name in seen_names:
                continue  # Skip duplicates
            seen_names.add(name)

            # Format types into categories
            types = place.get('types', [])
            formatted_places = [ptype.replace('_', ' ').title() for ptype in types]
            formatted_string = ', '.join(formatted_places)

            documents.append({
                "name": name,
                "categories": formatted_string,
            })

    # Calculate recommendations based on query
    results = []
    for document in documents:
        score = scorer.calculate_similarity(query, document)
        results.append((document["name"], document["categories"], score))

    # Sort and get the top 5 results
    results = sorted(results, key=lambda x: x[2], reverse=True)[:5]
    recommendations = [
        {"name": name, "categories": categories, "score": score}
        for name, categories, score in results
    ]

    return jsonify(recommendations)


if __name__ == '__main__':
    app.run(debug=True)
