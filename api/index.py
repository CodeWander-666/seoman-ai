from flask import Flask, request, jsonify, make_response
import re

app = Flask(__name__)

# --- CORS Helper ---
def cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    return response

# --- Simple Readability Calculator (No External Library) ---
def calculate_readability(text):
    if not text: return 0
    sentences = len(re.split(r'[.!?]+', text)) or 1
    words = len(text.split()) or 1
    # Simplified Flesch-Kincaid: Higher is easier to read
    avg_sentence_len = words / sentences
    score = 206.835 - (1.015 * avg_sentence_len) - 10 # Approx adjustment
    return max(0, min(100, int(score)))

# --- Main Route ---
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})

    # Lazy Imports
    import os
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        return cors_response({"error": f"Import Failed: {e}"}, 500)

    # Self-Repair Guard Class
    class SelfRepair:
        @staticmethod
        def guard(func, fallback):
            try: return func()
            except Exception as e:
                print(f"Error: {e}")
                return fallback

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_API_KEY = os.environ.get("OPR_API_KEY")

    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    output = {}

    # 1. LOGIC: Scraping (With Manual Readability)
    def run_scraping():
        headers = {'User-Agent': 'SEO-Pro-Bot/2.0'}
        resp = requests.get(url, headers=headers, timeout=9)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(" ", strip=True)
        
        # Intent Logic
        blob = (soup.title.string or "") + " " + text[:600]
        intent = "Navigational"
        if any(x in blob.lower() for x in ['buy', 'price', 'cart', 'sale', 'shop']): intent = "Transactional"
        elif any(x in blob.lower() for x in ['how', 'guide', 'tips', 'learn', 'tutorial']): intent = "Informational"

        return {
            "strategy": { "intent": intent, "status": resp.status_code, "server": resp.headers.get('Server', 'Unknown') },
            "content": { 
                "word_count": len(text.split()), 
                "readability": calculate_readability(text), 
                "title_len": len(soup.title.string) if soup.title else 0,
                "description": bool(soup.find('meta', attrs={'name': 'description'}))
            }
        }

    output.update(SelfRepair.guard(run_scraping, {
        "strategy": {"intent": "Unknown", "status": 0},
        "content": {"word_count": 0, "readability": 0}
    }))

    # 2. LOGIC: Technical (Better Error Handling)
    def run_google():
        if not GOOGLE_API_KEY: return {"speed_score": 0, "lcp": "No Key", "cls": "No Key"}
        
        g_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
        resp = requests.get(g_url)
        data = resp.json()

        # Check for Google API Errors (Quota, Invalid URL, etc)
        if 'error' in data:
            err_msg = data['error'].get('message', 'API Error')
            return {"speed_score": 0, "lcp": "API Fail", "cls": err_msg[:15]}

        # Extract Data
        lh = data.get('lighthouseResult', {})
        score = lh.get('categories', {}).get('performance', {}).get('score', 0)
        lcp = lh.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A')
        cls = lh.get('audits', {}).get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
        
        return {"speed_score": int(score * 100), "lcp": lcp, "cls": cls}

    output['technical'] = SelfRepair.guard(run_google, {"speed_score": 0, "lcp": "Error", "cls": "Error"})

    # 3. LOGIC: Authority (OPR)
    def run_opr():
        if not OPR_API_KEY: return {"page_rank": 0, "rank": "No Key", "domain": "N/A"}
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        
        resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': OPR_API_KEY})
        data = resp.json()
        
        if data.get('status_code') != 200:
             return {"page_rank": 0, "rank": "API Error", "domain": domain}

        d = data['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'] or "Unranked", "domain": d['domain'] }

    output['authority'] = SelfRepair.guard(run_opr, {"page_rank": 0, "rank": "N/A", "domain": "Unknown"})

    return cors_response(output)
