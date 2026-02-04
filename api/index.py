from flask import Flask, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import textstat
import os

app = Flask(__name__)

# ENV KEYS (Set these in Vercel Settings)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPR_API_KEY = os.environ.get("OPR_API_KEY")

def cors_response(data):
    resp = make_response(jsonify(data))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp

def get_intent(text, title):
    # Logic from "Art of SEO": Classify intent by vocabulary
    blob = (text + " " + title).lower()
    if any(x in blob for x in ['buy', 'price', 'checkout', 'add to cart', 'sale']):
        return "Transactional"
    if any(x in blob for x in ['how to', 'guide', 'what is', 'tutorial', 'learn']):
        return "Informational"
    return "Navigational"

@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def handler():
    if request.method == "OPTIONS": return cors_response({"ok": True})
    
    url = request.args.get('url')
    if not url: return cors_response({"error": "No URL"})
    if not url.startswith('http'): url = 'https://' + url

    final_data = {}

    # --- 1. SCRAPE & CONTENT (Requests + BeautifulSoup) ---
    try:
        headers = {'User-Agent': 'SEOAnalyzer/1.0'}
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        text = soup.get_text(" ", strip=True)
        
        final_data['strategy'] = {
            "intent": get_intent(text[:3000], soup.title.string if soup.title else ""),
            "status": page.status_code,
            "server": page.headers.get('Server', 'Unknown')
        }
        
        final_data['content'] = {
            "word_count": len(text.split()),
            "readability": textstat.flesch_reading_ease(text),
            "title_len": len(soup.title.string) if soup.title else 0,
            "description": True if soup.find('meta', attrs={'name': 'description'}) else False
        }
    except Exception as e:
        final_data['strategy'] = {"error": str(e)}
        final_data['content'] = {"error": str(e)}

    # --- 2. TECHNICAL (Google PageSpeed API) ---
    try:
        g_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
        g_res = requests.get(g_url).json()['lighthouseResult']
        
        final_data['technical'] = {
            "speed_score": int(g_res['categories']['performance']['score'] * 100),
            "lcp": g_res['audits']['largest-contentful-paint']['displayValue'],
            "cls": g_res['audits']['cumulative-layout-shift']['displayValue']
        }
    except:
        final_data['technical'] = {"speed_score": 0, "lcp": "Error", "cls": "Error"}

    # --- 3. AUTHORITY (OpenPageRank API) ---
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        opr_headers = {'API-OPR': OPR_API_KEY}
        opr_res = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}", headers=opr_headers).json()
        
        rank_data = opr_res['response'][0]
        final_data['authority'] = {
            "page_rank": rank_data['page_rank_decimal'] or 0,
            "rank": rank_data['rank'] or "N/A",
            "domain": rank_data['domain']
        }
    except:
        final_data['authority'] = {"page_rank": 0, "rank": "N/A", "domain": domain}

    return cors_response(final_data)
