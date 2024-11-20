from flask import Flask, request, jsonify
from vsm_scorer import VSMScorer
from data_parser import DataParser
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

global documents

data_parser = DataParser("yelp_academic_dataset_business.json")
data_parser.load_data()
documents = data_parser.get_documents()
scorer = VSMScorer(data_parser.idfs, title_weight=0.1, body_weight=0.9)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    query = data.get('query', '')
    
    #location_lat = data.get('lat', '')
    #location_lng = data.get('lng', '')
    #range = data.get('rng', '')
    search_range = 50
    location_lat = 37.7937
    location_lng = -122.3965
    data = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 100,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": location_lat,
                    "longitude": location_lng
                },
                "radius": search_range
            }
        }
    }
    endpoint = 'https://places.googleapis.com/v1/places:searchNearby'
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': ,
        'X-Goog-FieldMask': 'places.displayName.text, places.types, places.editorialSummary.text, places.regularOpeningHours.openNow, places.priceLevel'
    }
    response = requests.post(endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to retrieve data', 'status_code': response.status_code}), response.status_code
    #construct documents out of those place, pass them through scorer as done below

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
