from flask import Flask, request, jsonify, send_from_directory
import joblib
import os
import re
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model and vectorizer
model = joblib.load('phishing_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

VIRUSTOTAL_API_KEY = '4eedd9229a98abe547a4654b42eea68e4717588ed8c8ff28c625ff9078e78766'  # Add your VirusTotal API key here

# Define the root route
@app.route('/')
def home():
    return "Welcome to the Phishing Detection API!"

# Define a prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    text = data['email_text']
    
    # Phishing model prediction
    features = vectorizer.transform([text])
    prediction = model.predict(features)[0]
    
    # URL extraction and VirusTotal check
    urls = re.findall(r'(https?://\S+)', text)
    url_checks = {}
    
    for url in urls:
        url_checks[url] = check_url_with_virustotal(url)
    
    return jsonify({
        'prediction': 'Phishing' if prediction == 1 else 'Safe',
        'url_checks': url_checks
    })

def check_url_with_virustotal(url):
    headers = {
        'x-apikey': VIRUSTOTAL_API_KEY
    }
    response = requests.post(
        'https://www.virustotal.com/api/v3/urls',
        headers=headers,
        data={'url': url}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("VirusTotal response:", result)  # Log the response
        
        analysis_id = result['data']['id']
        analysis_status_url = f'https://www.virustotal.com/api/v3/analyses/{analysis_id}'
        
        # Wait for the analysis to complete
        analysis_result = None
        for _ in range(10):  # Try up to 10 times
            analysis_response = requests.get(analysis_status_url, headers=headers)
            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                if analysis_result['data']['attributes']['status'] == 'completed':
                    break
            time.sleep(1)  # Wait 1 second before checking again
        
        if analysis_result and analysis_result['data']['attributes']['status'] == 'completed':
            malicious_count = analysis_result['data']['attributes']['stats']['malicious']
            return 'Malicious' if malicious_count > 0 else 'Clean'
        else:
            return 'Unknown'
    else:
        return 'Error'

# Handle favicon.ico request
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
