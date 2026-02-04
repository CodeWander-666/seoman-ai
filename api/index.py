from flask import Flask, request, jsonify, make_response

# 1. Initialize Flask
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
# 🆕 ADDITION 1: ASSET HANDLER (Fixes the 404 Favicon Logs)
# ==============================================================================
class AssetHandler:
    @staticmethod
    def silence_favicon():
        return make_response("", 204)

# ==============================================================================
# 🆕 ADDITION 2: DIAGNOSE CLASS (The Logic You Requested)
# ==============================================================================
class Diagnose:
    @staticmethod
    def analyze_intent(text):
        if not text: return "Unknown"
        text = text.lower()
        if any(x in text for x in ['buy', 'price', 'cart', 'checkout']): return "Transactional"
        if any(x in text for x in ['how', 'guide', 'best', 'review']): return "Informational"
        if any(x in text for x in ['login', 'sign up', 'contact']): return "Navigational"
        return "Commercial"

    @staticmethod
    def check_health(data):
        issues = []
        # Check Technical
        if data.get('technical', {}).get('speed_score', 0) < 50: 
            issues.append("CRITICAL: Speed Score is low (<50). Google may penalize.")
        # Check Content
        if data.get('content', {}).get('word_count', 0) < 300: 
            issues.append("WARNING: Thin content detected (<300 words).")
        # Check Meta
        if not data.get('content', {}).get('description'): 
            issues.append("FIX: Meta Description is missing.")
        
        return issues if issues else ["All Systems Nominal"]

# ==============================================================================
# 🛡️ EXISTING CLASS: SELF REPAIR (Kept Exact)
# ==============================================================================
class SelfRepair:
    @staticmethod
    def guard(task_name, func, fallback):
        try:
            return func()
        except Exception as e:
            print(f"[{task_name} FAILED]: {e}")
            if isinstance(fallback, dict):
                fallback['error'] = f"Recovered from {str(e)[:20]}..."
            return fallback

# ==============================================================================
# 🔌 EXISTING CLASS: API CONNECTOR (Kept Exact)
# ==============================================================================
class APIConnector:
    @staticmethod
    def stealth_scrape(url):
        import requests
        from bs4 import BeautifulSoup
        import re
        from collections import Counter

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/'
        }

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code in [403, 429]: raise Exception(f"Bot Block {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        for x in soup(["script", "style", "svg", "nav", "footer"]): x.decompose()
        
        text = soup.get_text(" ", strip=True)
        words = re.findall(r'\w+', text.lower())
        
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
            "raw_text": text[:1000]
        }

    @staticmethod
    def get_google(url, key):
        import requests
        if not key: return {"speed_score": 0, "lcp": "NO KEY", "cls": "Check Vercel Env"}
        
        try:
            # ⚡ CRITICAL FIX: Timeout set to 9s (Must be under Vercel's 10s limit)
            endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            resp = requests.get(
                endpoint, 
                params={"url": url, "strategy": "mobile", "key": key}, 
                timeout=9 
            )
            
            # Handle Google API Errors
            if resp.status_code != 200:
                return {"speed_score": 0, "lcp": f"API {resp.status_code}", "cls": "Google Error"}
                
            data = resp.json()
            if 'error' in data:
                return {"speed_score": 0, "lcp": "Quota Limit", "cls": "Billing/Key"}

            # Success Parsing
            lh = data.get('lighthouseResult', {})
            score = lh.get('categories', {}).get('performance', {}).get('score', 0)
            audits = lh.get('audits', {})
            
            return {
                "speed_score": int(score * 100),
                "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
            
        except requests.exceptions.Timeout:
            # Graceful fallback if Google is too slow
            return {"speed_score": 0, "lcp": "TIMEOUT", "cls": "Google Slow"}
        except Exception as e:
            # Catch Connection errors
            return {"speed_score": 0, "lcp": "CONN FAIL", "cls": "Network Error"}

    @staticmethod
    def get_authority(url, key):
        import requests
        if not key: raise Exception("No Key")
        
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': key}, timeout=10)
        d = resp.json()['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }

# ==============================================================================
# 🚀 MAIN ROUTES (Updated to use new Classes)
# ==============================================================================

# 1. NEW ROUTE: Stop the 404 Favicon Errors
@app.route('/favicon.ico')
def favicon():
    return AssetHandler.silence_favicon()

# 2. MAIN ROUTE
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})

    try: import os
    except ImportError: return cors_response({"error": "Server Init Failed"}, 500)

    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    GOOGLE_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_KEY = os.environ.get("OPR_API_KEY")
    output = {}

    # Logic: Scrape + Diagnose Intent
    def task_scrape():
        raw = APIConnector.stealth_scrape(url)
        # 🆕 USE DIAGNOSE CLASS
        raw['strategy']['intent'] = Diagnose.analyze_intent(raw.get('raw_text', ''))
        return raw
    
    output.update(SelfRepair.guard("Scraping", task_scrape, {"strategy": {"intent": "Unreachable", "status": 0}, "content": {"word_count": 0, "error": "Scrape Fail"}}))
    
    output['technical'] = SelfRepair.guard("Google", lambda: APIConnector.get_google(url, GOOGLE_KEY), {"speed_score": 0, "lcp": "N/A", "cls": "N/A"})
    
    output['authority'] = SelfRepair.guard("Auth", lambda: APIConnector.get_authority(url, OPR_KEY), {"page_rank": 0, "rank": "N/A", "domain": "N/A"})
    
    # 🆕 USE DIAGNOSE CLASS FOR HEALTH CHECK
    output['diagnosis'] = Diagnose.check_health(output)

    return cors_response(output)
