from flask import Flask, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
# Get keys safely
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPR_API_KEY = os.environ.get("OPR_API_KEY")

def cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    return response

@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return cors_response({"ok": True})
    
    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    output = {}

    # 1. SCRAPE (Native Python only - No Textstat)
    try:
        headers = {'User-Agent': 'SEO-Tool/1.0'}
        resp = requests.get(url, headers=headers, timeout=9)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(" ", strip=True)
        
        # Simple Intent Logic
        blob = (soup.title.string or "") + " " + text[:500]
        intent = "Navigational"
        if any(x in blob.lower() for x in ['buy', 'price', 'cart', 'sale']): intent = "Transactional"
        elif any(x in blob.lower() for x in ['how', 'guide', 'tips']): intent = "Informational"

        output['strategy'] = { "intent": intent, "status": resp.status_code, "server": resp.headers.get('Server','N/A') }
        output['content'] = { 
            "word_count": len(text.split()), 
            "readability": "N/A (Lite Mode)", # Placeholder
            "title_len": len(soup.title.string) if soup.title else 0,
            "description": bool(soup.find('meta', attrs={'name': 'description'}))
        }
    except Exception as e:
        output['strategy'] = {"error": str(e)}
        output['content'] = {"error": str(e)}

    # 2. TECHNICAL (Google)
    try:
        if GOOGLE_API_KEY:
            g_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
            g_data = requests.get(g_url).json().get('lighthouseResult', {})
            output['technical'] = {
                "speed_score": int(g_data.get('categories',{}).get('performance',{}).get('score',0)*100),
                "lcp": g_data.get('audits',{}).get('largest-contentful-paint',{}).get('displayValue','N/A'),
                "cls": g_data.get('audits',{}).get('cumulative-layout-shift',{}).get('displayValue','N/A')
            }
        else:
            output['technical'] = {"error": "Missing Google Key"}
    except:
        output['technical'] = {"speed_score": 0, "lcp": "Error", "cls": "Error"}

    # 3. AUTHORITY (OPR)
    try:
        if OPR_API_KEY:
            domain = url.split("//")[-1].split("/")[0].replace("www.", "")
            opr = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers={'API-OPR': OPR_API_KEY}).json()
            d = opr['response'][0]
            output['authority'] = { "page_rank": d['page_rank_decimal'] or 0, "rank": d['rank'], "domain": d['domain'] }
        else:
            output['authority'] = {"page_rank": 0, "rank": "N/A", "domain": "No Key"}
    except:
        output['authority'] = {"page_rank": 0, "rank": "N/A"}

    return cors_response(output)
