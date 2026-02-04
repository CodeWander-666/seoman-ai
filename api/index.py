from flask import Flask, request, jsonify
import requests
import hashlib
import time
import os
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Simple CORS handling without flask-cors
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Simple cache
cache = {}

# User agent for requests
USER_AGENT = "SEO-VISION-PRO/1.0 (+https://seovision.pro)"

@app.route('/')
def home():
    return "SEO Vision Pro API is running!"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    })

@app.route('/api/audit', methods=['POST', 'OPTIONS'])
def perform_audit():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL parameter is required"}), 400
        
        url = data['url'].strip()
        
        # Validate URL
        if not (url.startswith('http://') or url.startswith('https://')):
            return jsonify({"error": "Invalid URL. Include http:// or https://"}), 400
        
        # Check cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < 300:
            result = cache[cache_key]['data']
            result['cached'] = True
            return jsonify(result)
        
        print(f"[AUDIT] Starting audit for {url}")
        
        # Get basic page info
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return jsonify({
                "error": f"Failed to fetch URL: {str(e)}",
                "code": "FETCH_ERROR"
            }), 400
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Calculate basic metrics
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        # Extract title and meta
        title = soup.title.string if soup.title else "No title"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else "No description"
        
        # Count headings
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        
        # Count images with alt
        images = soup.find_all('img')
        images_with_alt = len([img for img in images if img.get('alt')])
        
        # Count links
        links = soup.find_all('a')
        internal_links = len([link for link in links if link.get('href') and (link['href'].startswith('/') or url in link['href'])])
        external_links = len(links) - internal_links
        
        # Check for common SEO issues
        issues = []
        if h1_count == 0:
            issues.append("No H1 tag found")
        if h1_count > 1:
            issues.append(f"Multiple H1 tags ({h1_count})")
        if word_count < 300:
            issues.append(f"Low word count ({word_count}) - consider adding more content")
        if images_with_alt < len(images) * 0.7:
            issues.append(f"Only {images_with_alt}/{len(images)} images have alt text")
        
        # Calculate scores
        technical_score = 80
        content_score = min(100, word_count / 10)
        authority_score = 50  # Placeholder
        
        # Adjust scores based on issues
        technical_score -= len(issues) * 5
        if word_count > 1000:
            content_score += 10
        if images_with_alt == len(images) and len(images) > 0:
            technical_score += 10
        
        # Ensure scores are within bounds
        technical_score = max(0, min(100, technical_score))
        content_score = max(0, min(100, content_score))
        authority_score = max(0, min(100, authority_score))
        overall_score = round((technical_score + content_score + authority_score) / 3)
        
        # Generate report
        result = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "scores": {
                "technical": round(technical_score),
                "content": round(content_score),
                "authority": round(authority_score),
                "overall": overall_score
            },
            "metrics": {
                "word_count": word_count,
                "page_title": title[:100] + "..." if len(title) > 100 else title,
                "meta_description": description[:150] + "..." if len(description) > 150 else description,
                "h1_count": h1_count,
                "h2_count": h2_count,
                "images_total": len(images),
                "images_with_alt": images_with_alt,
                "internal_links": internal_links,
                "external_links": external_links,
                "response_code": response.status_code,
                "page_size_kb": len(response.content) / 1024
            },
            "issues": issues,
            "recommendations": [
                "Ensure all images have descriptive alt text",
                "Include one clear H1 tag per page",
                "Aim for at least 300 words of quality content",
                "Use internal links to establish site hierarchy",
                "Optimize meta title and description for keywords"
            ],
            "plan": data.get('plan', 'free')
        }
        
        # Cache result
        cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        print(f"[AUDIT] Completed audit for {url}")
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] Audit failed: {str(e)}")
        return jsonify({
            "error": "System error during audit",
            "message": str(e),
            "code": "AUDIT_FAILED"
        }), 500

# AI analysis endpoint (simplified)
@app.route('/api/ai-analysis', methods=['POST', 'OPTIONS'])
def ai_analysis():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        metrics = data.get('metrics', {})
        
        # Simple AI analysis without external API
        analysis = {
            "technical_fixes": [
                "Optimize page load speed by compressing images",
                "Ensure mobile responsiveness across all devices",
                "Fix any broken links or 404 errors"
            ],
            "content_opportunities": [
                "Expand on main topic with more detailed content",
                "Add relevant internal links to related pages",
                "Include more headings (H2, H3) for better structure"
            ],
            "quick_wins": [
                "Add missing meta description if not present",
                "Ensure all images have alt text",
                "Check and fix duplicate title tags"
            ],
            "ai_generated": True,
            "model": "SEO-Vision-Pro-Local"
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Vercel serverless
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(debug=True)
