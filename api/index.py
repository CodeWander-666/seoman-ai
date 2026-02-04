from flask import Flask, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import textstat
import os
import re

app = Flask(__name__)

# ENV VARIABLES (Set these in Vercel)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPR_API_KEY = os.environ.get("OPR_API_KEY")

# --- CORS HEADERS ---
def corsify(data, code=200):
    resp = make_response(jsonify(data), code)
    resp.headers.add("Access-Control-Allow-Origin", "*")
    resp.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    return resp

# --- HEURISTIC: GUESS USER INTENT ---
def predict_intent(text, title):
    # Based on Art of SEO: Navigational, Informational, Transactional
    blob = (text + " " + title).lower()
    trans_keys = ['buy', 'price', 'cart', 'shop', 'sale', 'checkout', 'pricing']
    info_keys = ['how', 'what', 'guide', 'tutorial', 'tips', 'learn', 'examples']
    
    trans_score = sum(1 for k in trans_keys if k in blob)
    info_score = sum(1 for k in info_keys if k in blob)
    
    if trans_score > info_score: return "Transactional ($)"
    if info_score > trans_score: return "Informational (i)"
    return "Navigational/Hybrid"

# --- MAIN LOGIC ---
@app.route('/api/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    if request.method == "OPTIONS": return corsify({"status": "ok"})
    
    url = request.args.get('url')
    if not url: return corsify({"error": "No URL provided"}, 400)
    if not url.startswith('http'): url = 'https://' + url

    results = {
        "1_strategy": {},
        "2_technical": {},
        "3_content": {},
        "4_authority": {}
    }

    # A. SCRAPE & CONTENT ANALYSIS
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; SEOBot/1.0)'}
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Text extraction
        raw_text = soup.get_text(" ", strip=True)
        word_count = len(raw_text.split())
        
        # 1. Strategy (Intent)
        results['1_strategy']['intent'] = predict_intent(raw_text[:2000], soup.title.string if soup.title else "")
        results['1_strategy']['status_code'] = page.status_code

        # 3. Content Metrics
        results['3_content'] = {
            "title": soup.title.string[:60] + "..." if soup.title and len(soup.title.string) > 60 else (soup.title.string if soup.title else "Missing"),
            "title_len": len(soup.title.string) if soup.title else 0,
            "description": soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else "Missing",
            "h1_count": len(soup.find_all('h1')),
            "word_count": word_count,
            "readability": textstat.flesch_reading_ease(raw_text), # 0-100 Score
            "images_missing_alt": len([img for img in soup.find_all('img') if not img.get('alt')])
        }
    except Exception as e:
        results['3_content']['error'] = str(e)

    # B. TECHNICAL (Google PageSpeed API)
    try:
        psi_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={GOOGLE_API_KEY}"
        psi = requests.get(psi_url).json()['lighthouseResult']
        
        results['2_technical'] = {
            "speed_score": int(psi['categories']['performance']['score'] * 100),
            "lcp": psi['audits']['largest-contentful-paint']['displayValue'],
            "cls": psi['audits']['cumulative-layout-shift']['displayValue'],
            "mobile_friendly": "Yes" # Implied by mobile strategy
        }
    except:
        results['2_technical'] = {"error": "API Limit or Fail"}

    # C. AUTHORITY (OpenPageRank)
    try:
        domain = url.split('/')[2].replace('www.', '')
        opr = requests.get(
            "https://openpagerank.com/api/v1.0/getPageRank",
            headers={'API-OPR': OPR_API_KEY},
            params={'domains[]': domain}
        ).json()
        rank_data = opr['response'][0]
        results['4_authority'] = {
            "score": rank_data['page_rank_decimal'] or 0,
            "global_rank": rank_data['rank'] or "Unranked"
        }
    except:
        results['4_authority'] = {"score": "N/A"}

    return corsify(results)
