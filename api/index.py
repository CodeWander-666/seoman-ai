from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import hashlib
import time
import os
import json
from datetime import datetime, timedelta
from _utils import (
    SecurityManager, 
    LRUCache, 
    APIConnector, 
    AdvancedIntelligence,
    GeminiAI,
    CrawlStats
)
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://*.vercel.app", "http://localhost:3000"])

# Configuration matching The Art of SEO principles
class Config:
    RATE_LIMIT = 30  # requests per minute
    RATE_LIMIT_PERIOD = 60
    CACHE_TTL = 300  # 5 minutes
    TIMEOUT = 30  # seconds for overall request
    AI_TIMEOUT = 25  # seconds for AI processing
    MAX_PAGES_FREE = 50
    CRAWL_DELAY = 3  # seconds between requests
    USER_AGENT = "SEO-VISION-PRO/1.0 (+https://seovision.pro; research-bot@seovision.pro)"

config = Config()

# Initialize core components
security_manager = SecurityManager(limit=config.RATE_LIMIT, period=config.RATE_LIMIT_PERIOD)
cache = LRUCache(max_size=1000, ttl=config.CACHE_TTL)
api_connector = APIConnector(config.USER_AGENT)
advanced_intel = AdvancedIntelligence()
gemini_ai = GeminiAI()

@app.before_request
def before_request():
    """Security and rate limiting middleware"""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    if not security_manager.is_allowed(client_ip):
        return jsonify({
            "error": "Rate limit exceeded. Please try again in 60 seconds.",
            "code": "RATE_LIMIT"
        }), 429

@app.route('/api/health', methods=['GET'])
def health_check():
    """System health endpoint"""
    return jsonify({
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "components": {
            "security": "active",
            "cache": "active",
            "ai_engine": "active" if gemini_ai.is_available() else "degraded",
            "apis": "active"
        }
    })

@app.route('/api/audit', methods=['POST'])
def perform_audit():
    """Main audit endpoint - 360-degree analysis"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL parameter is required"}), 400
        
        url = data['url'].strip()
        plan = data.get('plan', 'free')  # free/pro
        
        # URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return jsonify({"error": "Invalid URL protocol"}), 400
        
        # Check cache first
        cache_key = hashlib.md5(f"{url}:{plan}".encode()).hexdigest()
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['cached'] = True
            cached_result['cache_hit'] = True
            return jsonify(cached_result)
        
        # Plan-based limits
        if plan == 'free':
            max_pages = config.MAX_PAGES_FREE
            crawl_depth = 3
        else:
            max_pages = 500
            crawl_depth = 10
        
        # Phase 1: Technical Health Scan (Chapter 10 principles)
        print(f"[AUDIT] Starting technical scan for {url}")
        technical_data = api_connector.get_technical_audit(url)
        
        if technical_data.get('status_code') != 200:
            return jsonify({
                "error": f"Target returned {technical_data.get('status_code')}",
                "technical": technical_data
            }), 400
        
        # Phase 2: Content & Authority Analysis
        print(f"[AUDIT] Starting content analysis for {url}")
        content_data = api_connector.get_content_audit(url)
        authority_data = api_connector.get_authority_audit(url)
        
        # Phase 3: Crawl & Internal Structure Analysis
        print(f"[AUDIT] Crawling internal structure (max {max_pages} pages)")
        crawl_stats = CrawlStats(url, max_pages=max_pages, max_depth=crawl_depth)
        internal_data = crawl_stats.analyze()
        
        # Phase 4: Advanced Intelligence Processing
        print(f"[AUDIT] Running advanced intelligence models")
        traffic_forecast = advanced_intel.calculate_traffic_forecast(
            authority_score=authority_data.get('authority_score', 0),
            word_count=content_data.get('word_count', 0),
            backlinks=authority_data.get('backlinks', 0),
            seasonality=datetime.now().month
        )
        
        competitiveness = advanced_intel.analyze_competitiveness(
            keywords=content_data.get('top_keywords', []),
            authority_score=authority_data.get('authority_score', 0),
            word_count=content_data.get('word_count', 0)
        )
        
        # Compile enterprise report
        enterprise_data = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "audit_duration": round(time.time() - start_time, 2),
            "technical": {
                **technical_data,
                "core_web_vitals": technical_data.get('core_web_vitals', {}),
                "mobile_friendly": technical_data.get('mobile_friendly', False),
                "ssl_grade": technical_data.get('ssl_grade', 'F'),
                "canonical_issues": technical_data.get('canonical_issues', [])
            },
            "content": {
                **content_data,
                "readability_score": content_data.get('readability_score', 0),
                "entity_salience": content_data.get('entity_salience', {}),
                "intent_classification": content_data.get('intent_classification', 'unknown'),
                "thin_content_risk": content_data.get('thin_content_risk', False)
            },
            "authority": {
                **authority_data,
                "e_e_a_t_score": authority_data.get('e_e_a_t_score', 0),
                "link_toxicity_risk": authority_data.get('link_toxicity_risk', 'low'),
                "ymyl_category": authority_data.get('ymyl_category', None)
            },
            "internal": internal_data,
            "forecasting": traffic_forecast,
            "competitiveness": competitiveness,
            "plan": plan
        }
        
        # Cache the result
        cache.set(cache_key, enterprise_data)
        
        return jsonify(enterprise_data)
        
    except Exception as e:
        app.logger.error(f"AUDIT ERROR: {str(e)}", exc_info=True)
        return jsonify({
            "error": "System error during audit",
            "code": "AUDIT_FAILED",
            "message": str(e)
        }), 500

@app.route('/api/ai-strategy', methods=['POST'])
def get_ai_strategy():
    """Streaming AI strategic advisor endpoint"""
    @stream_with_context
    def generate():
        try:
            data = request.get_json()
            metrics = data.get('metrics', {})
            
            # Streaming AI response
            for chunk in gemini_ai.generate_audit_stream(metrics):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
            yield f"data: {json.dumps({'complete': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/api/benchmark', methods=['POST'])
def benchmark_competitors():
    """Competitor benchmarking (Pro feature)"""
    data = request.get_json()
    urls = data.get('urls', [])
    
    if len(urls) > 5:  # Limit for free plan
        return jsonify({"error": "Maximum 5 URLs for benchmarking"}), 400
    
    results = []
    for url in urls:
        try:
            tech = api_connector.get_technical_audit(url)
            auth = api_connector.get_authority_audit(url)
            
            results.append({
                "url": url,
                "performance_score": tech.get('performance_score', 0),
                "authority_score": auth.get('authority_score', 0),
                "core_vitals": tech.get('core_web_vitals', {})
            })
        except:
            continue
    
    return jsonify({"competitors": results})

# Serverless handler for Vercel
def handler(request):
    return app(request)
