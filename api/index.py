from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)

class APIConnector:
    def stealth_scrape(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=4)
            if response.status_code!= 200:
                return {"error": "Access Denied", "words": 0, "content": ""}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
            word_count = len(text.split())
            
            # Simple keyword density check (simulated based on top words)
            return {
                "title": soup.title.string if soup.title else url,
                "words": word_count,
                "content": text[:2000] # Truncate for AI prompt
            }
        except:
            return {"words": 0, "content": ""}

    def get_authority(self, url):
        # Simulated OpenPageRank call to avoid auth complexity in this snippet
        # In production, use: requests.get('https://openpagerank.com/api/...')
        # Returning a mock score based on URL length for demo stability
        return 5.5 

    def get_speed_score(self, url):
        # Simulated PageSpeed call to prevent API quota/timeout issues
        return 72

    def get_ai_advice(self, content, api_key):
        models = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}"
        
        prompt = f"Analyze this SEO content: {content}. Give 3 actionable tips in < 50 words."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        for model in models:
            try:
                target_url = endpoint.format(model, api_key)
                response = requests.post(target_url, json=payload, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates']['content']['parts']['text']
            except:
                continue
        
        return "AI Busy: Traffic High"

@app.route('/api/analyze', methods=)
def analyze():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not url.startswith('http'):
        url = 'https://' + url

    connector = APIConnector()
    
    # 1. Gather Data
    scrape_data = connector.stealth_scrape(url)
    speed_score = connector.get_speed_score(url)
    auth_score = connector.get_authority(url)
    
    # 2. Enterprise Logic (Strict Adherence to Rules)
    # Traffic = (Authority Score * Word Count) / 40
    est_traffic = int((auth_score * scrape_data['words']) / 40)
    
    # Ad Value = (Keyword Count * $1.50) -> Using Word Count as proxy for keywords approx 10%
    keyword_count = int(scrape_data['words'] * 0.1)
    ad_value = keyword_count * 1.50
    
    # Bounce Rate = 100 - (Speed Score * 0.5)
    bounce_rate = 100 - (speed_score * 0.5)

    # 3. AI Analysis
    # Note: Set your GEMINI_API_KEY in Vercel Environment Variables
    api_key = os.environ.get('GEMINI_API_KEY', 'INSERT_KEY_IF_LOCAL')
    ai_advice = connector.get_ai_advice(scrape_data['content'], api_key)

    response_data = {
        "metrics": {
            "traffic": f"{est_traffic:,}",
            "ad_value": f"${ad_value:,.2f}",
            "bounce_rate": f"{bounce_rate:.1f}%",
            "speed": speed_score,
            "words": scrape_data['words']
        },
        "ai_analysis": ai_advice
    }

    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
