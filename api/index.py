from flask import Flask, request, jsonify, make_response
from collections import Counter
import re
import os
import requests

app = Flask(__name__)

# --- CORS Helper ---
def cors_response(data, status=200):
    try:
        response = make_response(jsonify(data), status)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        return response
    except:
        return make_response("JSON Error", 500)

# ==============================================================================
# 🔌 API CONNECTOR (Smart REST Switcher)
# ==============================================================================
class APIConnector:
    @staticmethod
    def stealth_scrape(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
            resp = requests.get(url, headers=headers, timeout=8)
            
            if resp.status_code != 200: 
                return {"error": f"Scrape {resp.status_code}", "word_count": 0, "keywords": []}

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            for x in soup(["script", "style", "svg"]): x.decompose()
            
            text = soup.get_text(" ", strip=True)
            words = re.findall(r'\w+', text.lower())
            good_words = [w for w in words if len(w)>3]
            
            return {
                "word_count": len(words),
                "description": bool(soup.find('meta', attrs={'name': 'description'})),
                "keywords": Counter(good_words).most_common(5),
                "raw_text": text[:500]
            }
        except:
            return {"error": "Scrape Fail", "word_count": 0, "keywords": []}

    @staticmethod
    def get_google_speed(url, key):
        if not key: return {"score": 0}
        try:
            endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            resp = requests.get(endpoint, params={"url": url, "strategy": "mobile", "key": key}, timeout=8)
            data = resp.json()
            score = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
            return {"score": int(score * 100)}
        except:
            return {"score": 0}

    @staticmethod
    def get_authority(url, key):
        if not key: return {"rank": 0}
        try:
            domain = url.split("//")[-1].split("/")[0].replace("www.", "")
            resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': key}, timeout=5)
            return {"rank": resp.json()['response'][0]['page_rank_decimal'] or 0}
        except:
            return {"rank": 0}

    @staticmethod
    def get_ai_advice(stats_text, api_key):
        if not api_key: return "AI Offline: Missing API Key"

        # Tries models in order until one works. No library needed.
        models = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
        prompt = f"SEO Audit Stats: {stats_text}. Give 1 short technical fix (max 15 words)."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                resp = requests.post(url, json=payload, timeout=6)
                if resp.status_code == 200:
                    return resp.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                continue 
        return "AI Busy: Could not connect."

# ==============================================================================
# 🚀 MAIN ROUTE
# ==============================================================================
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})

    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL provided"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_KEY = os.environ.get("OPR_API_KEY")
    AI_KEY = os.environ.get("GEMINI_API_KEY")

    scrape = APIConnector.stealth_scrape(url)
    speed = APIConnector.get_google_speed(url, GOOGLE_KEY)
    auth = APIConnector.get_authority(url, OPR_KEY)
    
    # Projections
    traffic = int((auth['rank'] * 15 * scrape['word_count']) / 40)
    stats_str = f"Speed:{speed['score']}, Words:{scrape['word_count']}, Auth:{auth['rank']}"
    ai_text = APIConnector.get_ai_advice(stats_str, AI_KEY)

    output = {
        "technical": {"speed_score": speed['score'], "lcp": "N/A", "cls": "N/A"},
        "content": {"word_count": scrape['word_count'], "description": scrape.get('description', False), "keywords": scrape.get('keywords', [])},
        "authority": {"page_rank": auth['rank']},
        "enterprise": {
            "search_console_projection": {"est_monthly_traffic": traffic, "est_impressions": traffic * 12},
            "analytics_projection": {"est_bounce_rate": "45%", "est_session_duration": "2m"},
            "ads_planner": {"top_opportunities": []}
        },
        "ai_strategy": ai_text
    }

    return cors_response(output)
