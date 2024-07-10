from flask import Flask, request, jsonify, send_from_directory
import joblib
import os
import re
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  


model = joblib.load('phishing_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

VIRUSTOTAL_API_KEY = '********'  


@app.route('/')
def home():
    return "Welcome !"


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    text = data['email_text']
    
    
    features = vectorizer.transform([text])
    prediction = model.predict(features)[0]
    
    
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
        print("VirusTotal response:", result) 
        
        analysis_id = result['data']['id']
        analysis_status_url = f'https://www.virustotal.com/api/v3/analyses/{analysis_id}'
        
        
        analysis_result = None
        for _ in range(10):  
            analysis_response = requests.get(analysis_status_url, headers=headers)
            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                if analysis_result['data']['attributes']['status'] == 'completed':
                    break
            time.sleep(1)  
        
        if analysis_result and analysis_result['data']['attributes']['status'] == 'completed':
            malicious_count = analysis_result['data']['attributes']['stats']['malicious']
            return 'Malicious' if malicious_count > 0 else 'Clean'
        else:
            return 'Unknown'
    else:
        return 'Error'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
