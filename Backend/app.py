from flask import Flask, request, jsonify, send_from_directory
import joblib
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model and vectorizer
model = joblib.load('phishing_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Define the root route
@app.route('/')
def home():
    return "Welcome to the Phishing Detection API!"

# Define a prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    text = data['email_text']
    features = vectorizer.transform([text])
    prediction = model.predict(features)
    return jsonify({'prediction': int(prediction[0])})

# Handle favicon.ico request
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
