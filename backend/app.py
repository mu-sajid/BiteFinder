import requests
from vsm_scorer import VSMScorer
from data_parser import DataParser
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

def fetch_json(url, output_file="yelp_academic_dataset_business.json"):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")
    return output_file

# Dropbox direct download link
JSON_URL = "https://www.dropbox.com/scl/fi/75s7a1royurxqfzj5zeme/yelp_academic_dataset_business.json?rlkey=behds5atlzmectcyomfgudpmd&st=mb31p7la&dl=1"

# Download the JSON file dynamically
json_file = fetch_json(JSON_URL)

# Load data and initialize scorer
data_parser = DataParser(json_file)
data_parser.load_data()
scorer = VSMScorer(data_parser.idfs, title_weight=0.5, body_weight=0.5)

load_dotenv()
API_KEY = os.getenv('GCLOUD_API')
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    data2 = data.get('data')
    query = data2.get('query', '')
    location_lat = float(data2.get('lat', 0))
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

            # Get photo reference (if available)
            photo_reference = None
            if 'photos' in place and len(place['photos']) > 0:
                photo_reference = place['photos'][0].get('photo_reference')

            # Format types into categories
            types = place.get('types', [])
            formatted_places = [ptype.replace('_', ' ').title() for ptype in types]
            formatted_string = ', '.join(formatted_places)

            documents.append({
                "name": name,
                "categories": formatted_string,
                "rating": place.get('rating', 'N/A'),
                "price": place.get('price_level', 'N/A'),
                "is_open": place.get('opening_hours', {}).get('open_now', False),
                "image": f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}" if photo_reference else f"https://via.placeholder.com/300x200?text=No+Image+Available"
            })

    # Calculate recommendations based on query
    results = []
    for document in documents:
        score = scorer.calculate_similarity(query, document)
        results.append((document["name"], document["categories"], score, document["rating"], document["price"], document["is_open"], document["image"]))

    # Sort and get the top 5 results
    results = sorted(results, key=lambda x: x[2], reverse=True)[:5]
    recommendations = [
        {
            "name": name,
            "categories": categories,
            "score": score,
            "rating": rating,
            "price": price,
            "is_open": is_open,
            "image": image
        }
        for name, categories, score, rating, price, is_open, image in results
    ]

    return jsonify(recommendations)


if __name__ == '__main__':
    app.run(debug=True)
