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
    location_lat = data2.get('lat', '')
    location_lng = data2.get('lng', '')
    #search_range = data.get('rng', '')
    search_range = 5000.0

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,  # Replace with your actual API key
        "X-Goog-FieldMask": "places.displayName,places.types"
    }

    data = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
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

    places_result = requests.post(url, headers=headers, json=data).json()
    # Print the results
    documents = []
    for place in places_result['places']:
        #print(place['opening_hours']['open_now'])
        formatted_places = [place.replace('_', ' ').title() for place in place['types']]
        if len(formatted_places) > 1:
            formatted_string = ', '.join(formatted_places[:-1]) + f", and {formatted_places[-1]}"
        else:
            formatted_string = formatted_places[0]
        
#        print(place['displayName']['text'])
#        print(formatted_string)

        documents.append({
                "name": place['displayName']['text'],
                "categories": formatted_string
            })

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
