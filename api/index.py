from flask import Flask, request, jsonify, make_response

# Initialize Flask globally
app = Flask(__name__)

# --- CORS Helper ---
def cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    return response

# --- Main Route ---
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    # 1. Handle Preflight
    if request.method == "OPTIONS":
        return cors_response({"ok": True})

    # 2. Lazy Imports (Prevents Startup Crash)
    import os
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        return cors_response({"error": f"Library Missing: {str(e)}"}, 500)

    # ---------------------------------------------------------
    # 🛠️ NEW SELF-REPAIR CLASS (Put Exact Code Here)
    # ---------------------------------------------------------
    class SelfRepair:
        @staticmethod
        def guard(task_name, logic_function, fallback_data):
            """
            Executes a function. If it crashes, logs error and returns fallback.
            """
            try:
                # Try to run the dangerous logic
                return logic_function()
            except Exception as e:
                # If it fails, capture error and return safe default
                print(f"[{task_name} REPAIRED]: {str(e)}")
                # Inject the error message into the fallback data for UI to see
                fallback_data['error'] = str(e)
                return fallback_data
    # ---------------------------------------------------------

    # 3. Get Keys
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    OPR_API_KEY = os.environ.get("OPR_API_KEY")

    # 4. Input Check
    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL provided"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    output = {}

    
    # 5. Logic: Strategy & Content (Protected by SelfRepair)
    def run_scraping():
        headers = {'User-Agent': 'SEO-Bot/1.0'}
        resp = requests.get(url, headers=headers, timeout=9)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(" ", strip=True)
        
        # Intent Logic
        blob = (soup.title.string or "") + " " + text[:500]
        intent = "Navigational"
        if any(x in blob.lower() for x in ['buy', 'price', 'cart', 'sale']): intent = "Transactional"
        elif any(x in blob.lower() for x in ['how', 'guide', 'tips']): intent = "Informational"

        return {
            "strategy": { "intent": intent, "status": resp.status_code },
            "content": { 
                "word_count": len(text.split()), 
                "readability": "N/A", 
                "title_len": len(soup.title.string) if soup.title else 0,
                "description": bool(soup.find('meta', attrs={'name': 'description'}))
            }
        }

    # Execute Scraping with Safety Net
    scrape_data = SelfRepair.guard(
        task_name="Scraping",
        logic_function=run_scraping,
        fallback_data={
            "strategy": {"intent": "Unknown", "status": 0}, 
            "content": {"word_count": 0, "title_len": 0, "description": False}
        }
    )
    output.update(scrape_data)

    # 6. Logic: Technical (Protected by SelfRepair)
    def run_google():
        if not GOOGLE_API_KEY: raise Exception("No Google Key")
        g_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
        g_data = requests.get(g_url).json().get('lighthouseResult', {})
        return {
            "speed_score": int(g_data.get('categories',{}).get('performance',{}).get('score',0)*100),
            "lcp": g_data.get('audits',{}).get('largest-contentful-paint',{}).get('displayValue','N/A'),
            "cls": g_data.get('audits',{}).get('cumulative-layout-shift',{}).get('displayValue','N/A')
        }

    # Execute Google with Safety Net
    output['technical'] = SelfRepair.guard(
        task_name="GoogleAPI",
        logic_function=run_google,
        fallback_data={"speed_score": 0, "lcp": "N/A", "cls": "N/A"}
    )

    # 7. Logic: Authority (Protected by SelfRepair)
    def run_opr():
        if not OPR_API_KEY: raise Exception("No OPR Key")
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        opr = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': OPR_API_KEY}).json()
        d = opr['response'][0]
        return { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }

    # Execute OPR with Safety Net
    output['authority'] = SelfRepair.guard(
        task_name="AuthorityAPI",
        logic_function=run_opr,
        fallback_data={"page_rank": 0, "rank": "N/A", "domain": "Unknown"}
    )

    return cors_response(output)
