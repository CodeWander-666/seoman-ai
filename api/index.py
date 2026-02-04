from flask import Flask, request, jsonify, make_response

# 1. Initialize Flask (Global)
app = Flask(__name__)

# --- CORS Helper ---
def cors_response(data, status=200):
    try:
        response = make_response(jsonify(data), status)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        return response
    except:
        return make_response("CORS Error", 500)

# ==============================================================================
# 🛡️ CLASS 1: SELF REPAIR (The Safety Net)
# ==============================================================================
class SelfRepair:
    @staticmethod
    def guard(task_name, func, fallback):
        """Executes a function safely. If it crashes, returns fallback data."""
        try:
            return func()
        except Exception as e:
            # We can log the error internally here if needed
            print(f"[{task_name} FAILED]: {e}")
            # Inject the error message into the fallback so the UI knows
            if isinstance(fallback, dict):
                fallback['error'] = f"Recovered from {str(e)[:20]}..."
            return fallback

# ==============================================================================
# 🔌 CLASS 2: API CONNECTOR (The External Link)
# ==============================================================================
class APIConnector:
    @staticmethod
    def stealth_scrape(url):
        import requests
        from bs4 import BeautifulSoup
        import re
        from collections import Counter

        # Stealth Headers (Mimic Chrome)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/'
        }

        resp = requests.get(url, headers=headers, timeout=10)
        
        # Check for Bot Blocks
        if resp.status_code in [403, 429]:
            raise Exception(f"Bot Block {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        for x in soup(["script", "style", "svg", "nav", "footer"]): x.decompose()
        
        text = soup.get_text(" ", strip=True)
        words = re.findall(r'\w+', text.lower())
        
        # Keywords
        ignore = {'the','and','to','of','a','in','is','it','you','that','for','on','with','as','are','this','by','be'}
        good_words = [w for w in words if len(w)>3 and w not in ignore]
        
        return {
            "strategy": {"status": resp.status_code, "server": resp.headers.get('Server', 'Linux')},
            "content": {
                "word_count": len(words),
                "readability": 100 if len(words) > 100 else 0, 
                "title_len": len(soup.title.string) if soup.title else 0,
                "description": bool(soup.find('meta', attrs={'name': 'description'})),
                "keywords": Counter(good_words).most_common(5),
                "social_image": bool(soup.find('meta', attrs={'property': 'og:image'})),
                "links_internal": len(soup.find_all('a')),
                "links_external": 0
            },
            "raw_text": text[:1000] # For intent analysis
        }

    @staticmethod
    def get_google(url, key):
        import requests
        if not key: raise Exception("No Key")
        
        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        resp = requests.get(endpoint, params={"url": url, "strategy": "mobile", "key": key}, timeout=15)
        
        if resp.status_code != 200: raise Exception(f"API {resp.status_code}")
        
        data = resp.json()
        if 'error' in data: raise Exception("Quota/Limit")
        
        lh = data.get('lighthouseResult', {})
        score = lh.get('categories', {}).get('performance', {}).get('score', 0)
        audits = lh.get('audits', {})
        
        return {
            "speed_score": int(score * 100),
            "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
            "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
        }

    @staticmethod
    def get_authority(url, key):
        import requests
        if not key: raise Exception("No Key")
        
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': key}, timeout=10)
        d = resp.json()['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }

# ==============================================================================
# 🩺 CLASS 3: DIAGNOSE (The Doctor)
# ==============================================================================
class Diagnose:
    @staticmethod
    def analyze_intent(text):
        if not text: return "Unknown"
        text = text.lower()
        if any(x in text for x in ['buy', 'price', 'cart', 'checkout', 'shop']): return "Transactional"
        if any(x in text for x in ['how to', 'guide', 'best', 'review', 'tips']): return "Informational"
        if any(x in text for x in ['login', 'sign up', 'contact', 'about']): return "Navigational"
        return "Commercial"

    @staticmethod
    def check_health(data):
        """Analyzes the raw data and adds a 'health check' summary"""
        issues = []
        if data.get('technical', {}).get('speed_score', 0) < 50:
            issues.append("Critical: Slow Load Time")
        if data.get('content', {}).get('word_count', 0) < 300:
            issues.append("Warning: Thin Content")
        if not data.get('content', {}).get('description'):
            issues.append("Fix: Missing Meta Description")
        return issues

# ==============================================================================
# 🚀 MAIN ROUTE (The Orchestrator)
# ==============================================================================
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})

    # Lazy Imports (Safety)
    try:
        import os
    except ImportError:
        return cors_response({"error": "Server Init Failed"}, 500)

    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_KEY = os.environ.get("OPR_API_KEY")
    
    output = {}

    # 1. RUN SCRAPING (Protected by SelfRepair)
    def task_scrape():
        raw_data = APIConnector.stealth_scrape(url)
        # Use Diagnose Class to determine Intent
        raw_data['strategy']['intent'] = Diagnose.analyze_intent(raw_data.get('raw_text', ''))
        return raw_data
    
    scrape_result = SelfRepair.guard(
        "Scraping", 
        task_scrape, 
        fallback={"strategy": {"intent": "Unreachable", "status": 0}, "content": {"word_count": 0, "error": "Scrape Fail"}}
    )
    output.update(scrape_result)

    # 2. RUN GOOGLE (Protected by SelfRepair)
    output['technical'] = SelfRepair.guard(
        "GoogleAPI",
        lambda: APIConnector.get_google(url, GOOGLE_KEY),
        fallback={"speed_score": 0, "lcp": "N/A", "cls": "N/A"}
    )

    # 3. RUN AUTHORITY (Protected by SelfRepair)
    output['authority'] = SelfRepair.guard(
        "AuthorityAPI",
        lambda: APIConnector.get_authority(url, OPR_KEY),
        fallback={"page_rank": 0, "rank": "N/A", "domain": "N/A"}
    )

    # 4. FINAL DIAGNOSIS (New Feature)
    output['diagnosis'] = Diagnose.check_health(output)

    return cors_response(output)
