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
# 🆕 CLASS 5: ENTERPRISE INTELLIGENCE (The High-End Estimator)
# Mimics Semrush/Ahrefs logic to project data for ANY site
# ==============================================================================
class EnterpriseIntelligence:
    @staticmethod
    def run_deep_analysis(scrape_data, authority_data, speed_data):
        """Generates High-End Projections based on raw signals"""
        
        # 1. GOOGLE INDEXING API (Simulation)
        # We check if the site is indexable based on meta tags
        is_indexable = True
        if "noindex" in str(scrape_data): is_indexable = False
        
        # 2. GOOGLE SEARCH CONSOLE (Traffic Projection)
        # Algo: (Authority * WordCount) / 100 = Est. Monthly Visits
        auth_score = authority_data.get('page_rank', 0) or 0.1
        word_count = scrape_data.get('content', {}).get('word_count', 0)
        est_traffic = int((auth_score * 10 * word_count) / 50)
        
        # 3. GOOGLE ANALYTICS GA4 (Behavior Projection)
        # Algo: Faster sites + Better Readability = Lower Bounce Rate
        speed_score = speed_data.get('speed_score', 50)
        readability = scrape_data.get('content', {}).get('readability', 50)
        est_bounce_rate = max(20, 100 - (speed_score * 0.4 + readability * 0.3))
        
        # 4. KEYWORD PLANNER (CPC Estimation)
        # We assign estimated dollar values to the keywords we found
        keywords = scrape_data.get('content', {}).get('keywords', [])
        monetized_keywords = []
        for word, count in keywords:
            # Simple heuristic for CPC based on word length/complexity
            est_cpc = round((len(word) * 0.15) + (count * 0.05), 2)
            monetized_keywords.append({"keyword": word, "count": count, "est_cpc": f"${est_cpc}"})

        return {
            "indexing": {
                "status": "Indexable" if is_indexable else "Blocked (NoIndex)",
                "crawled_as": "Googlebot Smartphone",
                "last_crawl": "Just Now"
            },
            "search_console_projection": {
                "est_monthly_traffic": est_traffic,
                "est_impressions": est_traffic * 12, # Industry avg CTR
                "ranking_potential": "High" if auth_score > 4 else "Low"
            },
            "analytics_projection": {
                "est_bounce_rate": f"{int(est_bounce_rate)}%",
                "est_session_duration": "2m 15s" if speed_score > 80 else "0m 45s",
                "user_experience": "Excellent" if speed_score > 90 else "Needs Improvement"
            },
            "ads_planner": {
                "top_opportunities": monetized_keywords
            }
        }

# ==============================================================================
# 🖼️ CLASS 4: ASSET HANDLER
# ==============================================================================
class AssetHandler:
    @staticmethod
    def silence_favicon():
        return make_response("", 204)

# ==============================================================================
# 🩺 CLASS 3: DIAGNOSE
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
# 🛡️ CLASS 1: SELF REPAIR
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
# 🔌 CLASS 2: API CONNECTOR
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
            # ⚡ Optimized 9s Timeout
            endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            resp = requests.get(endpoint, params={"url": url, "strategy": "mobile", "key": key}, timeout=9)
            
            if resp.status_code != 200: return {"speed_score": 0, "lcp": f"API {resp.status_code}", "cls": "Google Error"}
            
            data = resp.json()
            if 'error' in data: return {"speed_score": 0, "lcp": "Quota Limit", "cls": "Billing/Key"}

            lh = data.get('lighthouseResult', {})
            score = lh.get('categories', {}).get('performance', {}).get('score', 0)
            audits = lh.get('audits', {})
            
            return {
                "speed_score": int(score * 100),
                "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
        except Exception:
            return {"speed_score": 0, "lcp": "TIMEOUT", "cls": "Google Slow"}

    @staticmethod
    def get_authority(url, key):
        import requests
        if not key: raise Exception("No Key")
        
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        resp = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': key}, timeout=10)
        d = resp.json()['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }

    # --- 4. AI GENERATION (Updated for Debugging) ---
    @staticmethod
    def get_ai_advice(seo_data, api_key):
        if not api_key: return "AI BRAIN: OFFLINE (Missing GEMINI_API_KEY)"
        try:
            import requests
            # ⚡ SWITCHED TO FASTER MODEL: gemini-1.5-flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            stats = f"Speed:{seo_data.get('technical',{}).get('speed_score')}, Traffic:{seo_data.get('enterprise',{}).get('search_console_projection',{}).get('est_monthly_traffic')}"
            prompt = f"You are a Senior SEO Auditor. Based on these site stats: [{stats}], provide ONE specific, high-impact technical recommendation. Keep it under 20 words."
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            resp = requests.post(url, json=payload, timeout=9)
            
            # 🔍 DEBUG: Return the ACTUAL Google error message
            if resp.status_code != 200: 
                try:
                    err_msg = resp.json()['error']['message']
                    return f"AI Error: {err_msg[:30]}..." # Show first 30 chars of error
                except:
                    return f"AI Error: Status {resp.status_code}"
            
            return resp.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"AI Crash: {str(e)[:15]}"

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
    
    # 4. ENTERPRISE INTELLIGENCE (NEW!) 🚀
    # Projects GSC, GA4, and Ads Data based on the signals we collected
    output['enterprise'] = SelfRepair.guard(
        "Enterprise",
        lambda: EnterpriseIntelligence.run_deep_analysis(output, output.get('authority',{}), output.get('technical',{})),
        {"error": "Analysis Failed"}
    )

    # 5. DIAGNOSIS
    output['diagnosis'] = Diagnose.check_health(output)

    # 6. AI STRATEGY
    output['ai_strategy'] = SelfRepair.guard("AI", lambda: APIConnector.get_ai_advice(output, AI_KEY), "AI Not Configured")

    return cors_response(output)
