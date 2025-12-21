import json 
import os
from flask import Flask, request, jsonify
from Classifier import Classifier

app = Flask(__name__)

classifier = Classifier("jarvisMk3")

@app.route('/classify', methods=['POST'])
def classify():
    response = request.get_json(force=True)
    if 'query' not in response:
        return jsonify(json.loads('{"request": "UNKNOWN"}'))
    return jsonify(classifier.get_classification(response['query']))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)