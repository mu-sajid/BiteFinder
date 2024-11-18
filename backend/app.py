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
    #send Nearby Request with latitude and longitude
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
