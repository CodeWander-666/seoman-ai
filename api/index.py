from flask import Flask, request, jsonify, make_response
from collections import Counter
import re
import os

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
# 🧠 CLASS 1: ENTERPRISE INTELLIGENCE (Logic Engine)
# ==============================================================================
class EnterpriseIntelligence:
    @staticmethod
    def run_deep_analysis(scrape_data, authority_data, speed_data):
        # 1. TRAFFIC ESTIMATION
        auth_score = authority_data.get('page_rank', 0) or 0.1
        word_count = scrape_data.get('content', {}).get('word_count', 0)
        est_traffic = int((auth_score * 15 * word_count) / 40)
        
        # 2. BEHAVIOR ESTIMATION
        speed = speed_data.get('speed_score', 50)
        est_bounce_rate = max(25, min(90, 100 - (speed * 0.6)))
        
        # 3. ADS VALUE ESTIMATION
        keywords = scrape_data.get('content', {}).get('keywords', [])
        monetized_keywords = []
        for word, count in keywords:
            est_cpc = round((len(word) * 0.20) + (count * 0.05), 2)
            monetized_keywords.append({"keyword": word, "count": count, "est_cpc": f"${est_cpc}"})

        return {
            "search_console_projection": {
                "est_monthly_traffic": est_traffic,
                "est_impressions": est_traffic * 15, 
                "ranking_potential": "Elite" if auth_score > 6 else ("High" if auth_score > 3 else "Growing")
            },
            "analytics_projection": {
                "est_bounce_rate": f"{int(est_bounce_rate)}%",
                "est_session_duration": "3m 10s" if speed > 85 else "1m 05s",
                "user_experience": "Smooth" if speed > 85 else "Friction Detected"
            },
            "ads_planner": {
                "top_opportunities": monetized_keywords
            }
        }

# ==============================================================================
# 🔌 CLASS 2: API CONNECTOR (Fixed for Stability)
# ==============================================================================
class APIConnector:
    # --- 1. SCRAPING ---
    @staticmethod
    def stealth_scrape(url):
        import requests
        from bs4 import BeautifulSoup
        
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
        
        ignore = {'the','and','to','of','a','in','is','it','you','that','for','on','with','as','are','this','by','be','your','can'}
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

    # --- 2. GOOGLE PAGESPEED ---
    @staticmethod
    def get_google(url, key):
        import requests
        if not key: return {"speed_score": 0, "lcp": "NO KEY", "cls": "Check Vercel Env"}
        
        try:
            endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            resp = requests.get(endpoint, params={"url": url, "strategy": "mobile", "key": key}, timeout=9)
            
            if resp.status_code != 200: 
                return {"speed_score": 0, "lcp": f"HTTP {resp.status_code}", "cls": "API Error"}
            
            data = resp.json()
            if 'error' in data: 
                err = data['error'].get('message', 'Unknown')
                return {"speed_score": 0, "lcp": "GOOGLE ERR", "cls": err[:15]}

            lh = data.get('lighthouseResult', {})
            score = lh.get('categories', {}).get('performance', {}).get('score', 0)
            audits = lh.get('audits', {})
            
            return {
                "speed_score": int(score * 100),
                "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
        except Exception as e:
            return {"speed_score": 0, "lcp": "CRASH", "cls": str(e)[:15]}

    # --- 3. AUTHORITY ---
    @staticmethod
    def get_authority(url, key):
        import requests
        if not key: raise Exception("No Key")
        
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': key}, timeout=10)
        d = resp.json()['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }

    # --- 4. AI ADVISOR (THE FIX: STABLE ENDPOINT) ---
    @staticmethod
    def get_ai_advice(seo_data, api_key):
        """
        Uses 'gemini-pro' on the stable 'v1' API.
        This fixes the '404 NOT_FOUND' error from the beta flash model.
        """
        if not api_key: return "AI BRAIN: OFFLINE (Missing GEMINI_API_KEY)"
        
        import requests
        
        # ⚡ FIX: Use 'v1' and 'gemini-pro' (Universal Availability)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        
        stats = f"Speed:{seo_data.get('technical',{}).get('speed_score')}, Traffic:{seo_data.get('enterprise',{}).get('search_console_projection',{}).get('est_monthly_traffic')}"
        prompt = f"You are a Senior SEO Auditor. Based on these site stats: [{stats}], provide ONE specific, high-impact technical recommendation. Keep it under 20 words."
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            resp = requests.post(url, json=payload, timeout=9)
            
            if resp.status_code == 200:
                return resp.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Diagnostic Error
            data = resp.json()
            if 'error' in data:
                return f"Google Error: {data['error']['message'][:30]}..."
                
            return f"Status: {resp.status_code}"

        except Exception as e:
            return f"Connection Failed: {str(e)[:15]}"

# ==============================================================================
# 🛡️ CLASS 3: SELF REPAIR
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
# 🖼️ CLASS 4: ASSET HANDLER
# ==============================================================================
class AssetHandler:
    @staticmethod
    def silence_favicon():
        return make_response("", 204)

# ==============================================================================
# 🩺 CLASS 5: DIAGNOSE
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
        if data.get('technical', {}).get('speed_score', 0) < 50: 
            issues.append("CRITICAL: Speed Score is low (<50). Google may penalize.")
        if data.get('content', {}).get('word_count', 0) < 300: 
            issues.append("WARNING: Thin content detected (<300 words).")
        if not data.get('content', {}).get('description'): 
            issues.append("FIX: Meta Description is missing.")
        return issues if issues else ["All Systems Nominal"]

# ==============================================================================
# 🚀 MAIN ROUTES
# ==============================================================================

@app.route('/favicon.ico')
def favicon():
    return AssetHandler.silence_favicon()

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
    AI_KEY = os.environ.get("GEMINI_API_KEY")
    
    output = {}

    # 1. SCRAPE
    def task_scrape():
        raw = APIConnector.stealth_scrape(url)
        raw['strategy']['intent'] = Diagnose.analyze_intent(raw.get('raw_text', ''))
        return raw
    output.update(SelfRepair.guard("Scraping", task_scrape, {"strategy": {"intent": "Unreachable", "status": 0}, "content": {"word_count": 0, "error": "Scrape Fail"}}))
    
    # 2. TECHNICAL
    output['technical'] = SelfRepair.guard("Google", lambda: APIConnector.get_google(url, GOOGLE_KEY), {"speed_score": 0, "lcp": "N/A", "cls": "N/A"})
    
    # 3. AUTHORITY
    output['authority'] = SelfRepair.guard("Auth", lambda: APIConnector.get_authority(url, OPR_KEY), {"page_rank": 0, "rank": "N/A", "domain": "N/A"})
    
    # 4. ENTERPRISE INTELLIGENCE
    output['enterprise'] = SelfRepair.guard(
        "Enterprise",
        lambda: EnterpriseIntelligence.run_deep_analysis(output, output.get('authority',{}), output.get('technical',{})),
        {"error": "Analysis Failed"}
    )

    # 5. DIAGNOSIS
    output['diagnosis'] = Diagnose.check_health(output)

    # 6. AI STRATEGY
    output['ai_strategy'] = SelfRepair.guard("AI", lambda: APIConnector.get_ai_advice(output, AI_KEY), "Recommendation Engine Active")

    return cors_response(output)
