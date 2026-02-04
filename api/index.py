from flask import Flask, request, jsonify, make_response
import re

app = Flask(__name__)

# --- CORS Helper ---
def cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    return response

# --- Readability Logic ---
def get_readability(text):
    if not text or len(text.split()) < 5: return 0
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text)) or 1
    # Simple Automated Readability Index (ARI) approximation
    score = 4.71 * (len(text) / words) + 0.5 * (words / sentences) - 21.43
    # Normalize to 0-100 (Lower ARI = Easier = Higher Score)
    return max(0, min(100, int(100 - score)))


# ==============================================================================
# 🔌 NEW: API CONNECTOR (Paste this BEFORE the @app.route line)
# ==============================================================================
class APIConnector:
    @staticmethod
    def get_google_data(target_url, api_key):
        """Fetches Core Web Vitals from Google PageSpeed API"""
        if not api_key:
            return {"speed_score": 0, "lcp": "No Key", "cls": "No Key"}
        
        try:
            # We import requests inside to prevent startup crashes if lib is missing
            import requests
            endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                "url": target_url,
                "strategy": "mobile",
                "key": api_key
            }
            
            resp = requests.get(endpoint, params=params, timeout=15)
            data = resp.json()

            # Error Handling (e.g. Quota Limit)
            if 'error' in data:
                code = data['error'].get('code', 500)
                msg = data['error'].get('message', 'Unknown API Error')
                return {"speed_score": 0, "lcp": f"Err {code}", "cls": "API Fail"}

            # Success Parsing
            lh = data.get('lighthouseResult', {})
            score = lh.get('categories', {}).get('performance', {}).get('score', 0)
            audits = lh.get('audits', {})
            
            return {
                "speed_score": int(score * 100),
                "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
        except Exception as e:
            return {"speed_score": 0, "lcp": "Crash", "cls": str(e)[:10]}

    @staticmethod
    def get_authority_data(domain, api_key):
        """Fetches Domain Authority from OpenPageRank"""
        if not api_key:
            return {"page_rank": 0, "rank": "No Key", "domain": "Config Required"}
            
        try:
            import requests
            endpoint = "https://openpagerank.com/api/v1.0/getPageRank"
            headers = {'API-OPR': api_key}
            params = {'domains[]': domain}
            
            resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
            data = resp.json()
            
            if data.get('status_code') != 200:
                return {"page_rank": 0, "rank": "API Error", "domain": domain}

            result = data['response'][0]
            return {
                "page_rank": result['page_rank_decimal'] or 0,
                "rank": result['rank'] or "Unranked",
                "domain": result['domain']
            }
        except Exception as e:
            return {"page_rank": 0, "rank": "N/A", "domain": "Auth Fail"}


# --- Main Handler ---
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})

    # Lazy Imports
    import os
    try:
        import requests
        from bs4 import BeautifulSoup
        from collections import Counter
    except ImportError as e:
        return cors_response({"error": f"Import Failed: {e}"}, 500)

    # ENV KEYS
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_API_KEY = os.environ.get("OPR_API_KEY")

    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    output = {}

    # ----------------------------------------------------
    # 1. STEALTH SCRAPING (Fixes "Word Count 27")
    # ----------------------------------------------------
    def run_scraping():
        # Mimic Real Chrome Browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove scripts and styles to get REAL text
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            text = soup.get_text(" ", strip=True)
            words = re.findall(r'\w+', text.lower())
            
            # Keyword Density
            stopwords = {'the','and','to','of','a','in','is','it','you','that','for','on','with','as','are','this','by','be','or','at','from','your','can','we','an'}
            meaningful = [w for w in words if w not in stopwords and len(w) > 3]
            top_kw = Counter(meaningful).most_common(5)

            # Link Counting
            links = soup.find_all('a', href=True)
            in_links = len([l for l in links if url in l['href'] or l['href'].startswith('/')])
            
            # Social Image
            og_img = soup.find('meta', attrs={'property': 'og:image'})
            
            # Intent
            intent_blob = (soup.title.string or "") + " " + text[:500]
            intent = "Informational"
            if any(x in intent_blob.lower() for x in ['shop', 'price', 'buy', 'cart', 'checkout']): intent = "Transactional"
            elif any(x in intent_blob.lower() for x in ['contact', 'location', 'address']): intent = "Navigational"

            return {
                "strategy": { "intent": intent, "status": resp.status_code, "server": resp.headers.get('Server', 'Linux') },
                "content": {
                    "word_count": len(words),
                    "readability": get_readability(text),
                    "title_len": len(soup.title.string) if soup.title else 0,
                    "description": bool(soup.find('meta', attrs={'name': 'description'})),
                    "keywords": top_kw,
                    "social_image": bool(og_img),
                    "links_internal": in_links,
                    "links_external": len(links) - in_links
                }
            }
        except Exception as e:
            return {
                "strategy": {"intent": "Error", "status": 0}, 
                "content": {"error": str(e), "word_count": 0}
            }

    # Execute Scraping
    scrape_data = run_scraping()
    output.update(scrape_data)

    # ----------------------------------------------------
    # 2. GOOGLE API (With Error Reporting)
    # ----------------------------------------------------
    def run_google():
        if not GOOGLE_API_KEY: 
            return {"speed_score": 0, "lcp": "No Key", "cls": "No Key"}
        
        try:
            g_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
            api_resp = requests.get(g_url)
            data = api_resp.json()

            # DEBUG: Catch Google Errors
            if 'error' in data:
                err = data['error']
                # Return the ACTUAL error message (e.g., "Bad Request", "Quota")
                return {"speed_score": 0, "lcp": "API Error", "cls": str(err.get('code', 500))}

            lh = data.get('lighthouseResult', {})
            score = lh.get('categories', {}).get('performance', {}).get('score', 0)
            
            return {
                "speed_score": int(score * 100),
                "lcp": lh.get('audits', {}).get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "cls": lh.get('audits', {}).get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
        except Exception as e:
            return {"speed_score": 0, "lcp": "Crash", "cls": str(e)}

    output['technical'] = run_google()

    # ----------------------------------------------------
    # 3. AUTHORITY (OPR)
    # ----------------------------------------------------
    def run_opr():
        if not OPR_API_KEY: return {"page_rank": 0, "rank": "No Key", "domain": "Config Required"}
        try:
            domain = url.split("//")[-1].split("/")[0].replace("www.", "")
            resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': OPR_API_KEY})
            d = resp.json()['response'][0]
            return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'] or "Unranked", "domain": d['domain'] }
        except:
            return {"page_rank": 0, "rank": "N/A", "domain": "API Error"}

    output['authority'] = run_opr()

    return cors_response(output)
