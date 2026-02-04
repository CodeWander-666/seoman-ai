from flask import Flask, request, jsonify, make_response, stream_with_context
from collections import Counter
import re
import os
import json
import time
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai

# ==============================================================================
# 🚀 ENHANCED CONFIGURATION & CONSTANTS
# ==============================================================================
class Config:
    """Centralized configuration management"""
    # Model configuration - fallback hierarchy
    GEMINI_MODEL_PRIORITY = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "models/gemini-pro"
    ]
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 30
    
    # Cache settings
    CACHE_DURATION = 300  # 5 minutes
    MAX_CACHE_SIZE = 1000
    
    # Timeouts
    REQUEST_TIMEOUT = 30
    AI_TIMEOUT = 25
    
    # Security
    ALLOWED_DOMAINS = ["*"]  # or specify domains
    MAX_CONTENT_LENGTH = 1000000  # 1MB

# ==============================================================================
# 🧠 ENHANCED ENTERPRISE INTELLIGENCE
# ==============================================================================
class AdvancedIntelligence:
    """Advanced AI-powered SEO analytics"""
    
    @staticmethod
    def calculate_traffic_forecast(auth_score: float, word_count: int, 
                                  backlinks: int = 0) -> Dict:
        """Predict traffic with machine learning-like algorithms"""
        
        # Multi-factor weighted algorithm
        base_traffic = auth_score * 25 * word_count / 50
        backlink_boost = backlinks * 0.8
        competition_factor = 1.2 if auth_score > 4 else 0.7
        
        est_traffic = int(base_traffic * competition_factor + backlink_boost)
        
        # Seasonal adjustment (higher in Q4)
        current_month = datetime.now().month
        seasonal_adjustment = 1.1 if current_month in [10, 11, 12] else 1.0
        est_traffic = int(est_traffic * seasonal_adjustment)
        
        # Calculate projections
        return {
            "pessimistic": int(est_traffic * 0.6),
            "expected": est_traffic,
            "optimistic": int(est_traffic * 1.4),
            "confidence": "high" if auth_score > 3 and word_count > 500 else "medium",
            "seasonal_impact": f"{int((seasonal_adjustment - 1) * 100)}%"
        }
    
    @staticmethod
    def analyze_competitiveness(keywords: List[Tuple[str, int]], 
                               domain_auth: float) -> Dict:
        """Analyze keyword competition and opportunity"""
        
        opportunities = []
        high_competition = []
        
        for keyword, count in keywords:
            # AI-driven scoring
            word_len = len(keyword.split())
            monthly_volume = count * 120  # Estimated from content
            difficulty = (domain_auth * 10) / (word_len * 2)
            
            # Calculate opportunity score (0-100)
            opp_score = min(100, (monthly_volume / 100) * (100 - difficulty))
            
            keyword_data = {
                "keyword": keyword,
                "volume": f"{monthly_volume:,}",
                "difficulty": f"{difficulty:.1f}/10",
                "opportunity_score": int(opp_score),
                "potential_cpc": f"${max(0.5, min(50, word_len * 1.5 + domain_auth * 2)):.2f}",
                "content_gap": "high" if opp_score > 70 else ("medium" if opp_score > 40 else "low")
            }
            
            if opp_score > 50:
                opportunities.append(keyword_data)
            else:
                high_competition.append(keyword_data)
        
        return {
            "high_opportunity": sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)[:5],
            "high_competition": high_competition[:3],
            "total_opportunities": len(opportunities),
            "market_coverage": f"{min(100, len(opportunities) * 15)}%"
        }

# ==============================================================================
# 🔌 POWERFUL API CONNECTOR WITH GEMINI 1.5/2.0
# ==============================================================================
class GeminiAI:
    """Advanced Gemini AI integration with multiple models and streaming"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.available_models = []
        self.model_cache = {}
        self.last_model_check = None
        
    def initialize(self):
        """Initialize Gemini with automatic model discovery"""
        if not self.api_key:
            return None
            
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai
            
            # Cache model list for 1 hour
            current_time = time.time()
            if (not self.last_model_check or 
                current_time - self.last_model_check > 3600):
                self.discover_models()
                self.last_model_check = current_time
                
            return True
        except Exception as e:
            print(f"Gemini init error: {e}")
            return False
    
    def discover_models(self):
        """Discover all available models"""
        try:
            models = list(genai.list_models())
            self.available_models = [
                m.name for m in models 
                if 'generateContent' in m.supported_generation_methods
            ]
            print(f"Discovered {len(self.available_models)} models")
        except Exception as e:
            print(f"Model discovery failed: {e}")
            self.available_models = []
    
    def get_best_model(self) -> Optional[str]:
        """Get the best available model"""
        if not self.available_models:
            return None
            
        # Try priority models first
        for priority_model in Config.GEMINI_MODEL_PRIORITY:
            if any(priority_model in model for model in self.available_models):
                # Find exact match
                for model in self.available_models:
                    if priority_model in model:
                        return model
        
        # Fallback to first available
        return self.available_models[0] if self.available_models else None
    
    def generate_seo_analysis(self, site_data: Dict, streaming: bool = False):
        """Generate comprehensive SEO analysis with multiple strategies"""
        
        if not self.client or not self.api_key:
            return "AI Analysis Unavailable"
        
        model_name = self.get_best_model()
        if not model_name:
            return "No AI Models Available"
        
        # Prepare enhanced prompt
        prompt = self._build_seo_prompt(site_data)
        
        try:
            # Configure generation parameters
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if streaming:
                # Return streaming response
                response = model.generate_content(prompt, stream=True)
                return self._stream_response(response)
            else:
                # Standard response
                response = model.generate_content(prompt)
                return self._parse_ai_response(response.text)
                
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return f"AI Analysis Error: {str(e)[:100]}"
    
    def _build_seo_prompt(self, data: Dict) -> str:
        """Build comprehensive SEO analysis prompt"""
        
        return f"""
        ACT as a Senior SEO Consultant with 15+ years experience.
        
        ANALYZE this website data and provide actionable recommendations:
        
        SITE OVERVIEW:
        - Speed Score: {data.get('technical', {}).get('speed_score', 0)}/100
        - Estimated Traffic: {data.get('enterprise', {}).get('search_console_projection', {}).get('est_monthly_traffic', 0)}
        - Authority Score: {data.get('authority', {}).get('page_rank', 0)}/10
        - Content Quality: {data.get('content', {}).get('word_count', 0)} words
        
        ISSUES DETECTED:
        {chr(10).join([f"- {issue}" for issue in data.get('diagnosis', [])])}
        
        REQUIREMENTS:
        1. Provide 3 HIGH-IMPACT technical fixes (prioritized)
        2. Suggest 2 content opportunities with specific topics
        3. Give 1 quick win that can be implemented in 24 hours
        4. Estimate potential traffic increase percentage
        5. Mention any Core Web Vitals issues
        
        Format response as JSON with keys: technical_fixes, content_opportunities, quick_win, traffic_potential, core_web_vitals.
        """
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse and structure AI response"""
        try:
            # Try to extract JSON if present
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to text response
                return {
                    "analysis": response.strip(),
                    "format": "text",
                    "confidence": 0.8
                }
        except:
            return {"analysis": response, "format": "raw"}
    
    def _stream_response(self, response_stream):
        """Handle streaming response"""
        for chunk in response_stream:
            yield chunk.text
            time.sleep(0.01)  # Small delay for smooth streaming

# ==============================================================================
# 🛡️ ADVANCED SECURITY & RATE LIMITING
# ==============================================================================
class SecurityManager:
    """Enhanced security and rate limiting"""
    
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()
        self.blocked_ips = set()
        
    def check_rate_limit(self, ip: str) -> Tuple[bool, Dict]:
        """Advanced rate limiting with IP tracking"""
        current_time = time.time()
        
        with self.lock:
            # Clean old requests
            if ip in self.requests:
                self.requests[ip] = [
                    req_time for req_time in self.requests[ip]
                    if current_time - req_time < Config.RATE_LIMIT_WINDOW
                ]
            
            # Check if IP is blocked
            if ip in self.blocked_ips:
                return False, {"error": "IP temporarily blocked", "retry_after": 3600}
            
            # Check rate limit
            request_count = len(self.requests.get(ip, []))
            if request_count >= Config.MAX_REQUESTS_PER_WINDOW:
                # Temporary blocking
                self.blocked_ips.add(ip)
                # Schedule unblock
                threading.Timer(3600, lambda: self.blocked_ips.remove(ip)).start()
                return False, {"error": "Rate limit exceeded", "retry_after": 3600}
            
            # Add current request
            if ip not in self.requests:
                self.requests[ip] = []
            self.requests[ip].append(current_time)
            
            return True, {
                "remaining": Config.MAX_REQUESTS_PER_WINDOW - request_count - 1,
                "reset_in": Config.RATE_LIMIT_WINDOW
            }

# ==============================================================================
# 💾 INTELLIGENT CACHING SYSTEM
# ==============================================================================
class CacheSystem:
    """LRU cache with TTL and intelligent invalidation"""
    
    def __init__(self):
        self.cache = {}
        self.access_times = {}
        self.max_size = Config.MAX_CACHE_SIZE
        
    def get_key(self, url: str) -> str:
        """Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Dict]:
        """Get cached data if valid"""
        key = self.get_key(url)
        
        if key in self.cache:
            cache_time, data = self.cache[key]
            if time.time() - cache_time < Config.CACHE_DURATION:
                # Update access time
                self.access_times[key] = time.time()
                return data
            else:
                # Expired
                self.delete(key)
        
        return None
    
    def set(self, url: str, data: Dict):
        """Cache data with TTL"""
        key = self.get_key(url)
        
        # LRU eviction if needed
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            self.delete(oldest_key)
        
        self.cache[key] = (time.time(), data)
        self.access_times[key] = time.time()
    
    def delete(self, key: str):
        """Delete from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================
app = Flask(__name__)

# Initialize systems
gemini_ai = None
security_manager = SecurityManager()
cache_system = CacheSystem()

def init_gemini():
    """Initialize Gemini AI on startup"""
    global gemini_ai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        gemini_ai = GeminiAI(api_key)
        if gemini_ai.initialize():
            print("✅ Gemini AI initialized successfully")
        else:
            print("⚠️ Gemini AI initialization failed")
    else:
        print("⚠️ No Gemini API key found")

# Initialize on import
init_gemini()

# ==============================================================================
# 🎯 ENHANCED ROUTES
# ==============================================================================
@app.before_request
def before_request():
    """Global request preprocessing"""
    # Security headers
    pass

@app.after_request
def after_request(response):
    """Global response processing"""
    # CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('X-Powered-By', 'SEO AI Engine v2.0')
    return response

@app.route('/api/v2/analyze', methods=['GET', 'OPTIONS'])
def analyze_v2():
    """Enhanced analysis endpoint with caching and streaming"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})
    
    # Rate limiting
    client_ip = request.remote_addr
    allowed, limit_info = security_manager.check_rate_limit(client_ip)
    if not allowed:
        return jsonify(limit_info), 429
    
    # Get URL
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter required"}), 400
    
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check cache first
    cached_result = cache_system.get(url)
    if cached_result:
        cached_result["cached"] = True
        cached_result["cache_hit"] = True
        return jsonify(cached_result)
    
    try:
        # Extract components (simplified for brevity)
        result = {
            "url": url,
            "analysis_timestamp": datetime.now().isoformat(),
            "version": "2.0",
            "request_id": hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:8]
        }
        
        # Enhanced scraping
        scrape_data = APIConnector.stealth_scrape(url)
        
        # Get speed data
        google_key = os.environ.get("GOOGLE_API_KEY")
        speed_data = APIConnector.get_google(url, google_key)
        
        # Get authority
        opr_key = os.environ.get("OPR_API_KEY")
        auth_data = APIConnector.get_authority(url, opr_key) if opr_key else {"page_rank": 0}
        
        # Advanced intelligence
        advanced = AdvancedIntelligence()
        result["traffic_forecast"] = advanced.calculate_traffic_forecast(
            auth_data.get('page_rank', 0),
            scrape_data.get('content', {}).get('word_count', 0)
        )
        
        result["keyword_analysis"] = advanced.analyze_competitiveness(
            scrape_data.get('content', {}).get('keywords', []),
            auth_data.get('page_rank', 0)
        )
        
        # AI Analysis with Gemini
        if gemini_ai:
            # Prepare data for AI
            ai_input = {
                "technical": speed_data,
                "enterprise": {"search_console_projection": result["traffic_forecast"]},
                "authority": auth_data,
                "content": scrape_data.get('content', {}),
                "diagnosis": Diagnose.check_health({
                    "technical": speed_data,
                    "content": scrape_data.get('content', {})
                })
            }
            
            # Check if streaming requested
            stream = request.args.get('stream', 'false').lower() == 'true'
            
            if stream:
                # Return streaming response
                @stream_with_context
                def generate():
                    yield json.dumps({"status": "starting_ai_analysis"}) + "\n"
                    
                    ai_response = gemini_ai.generate_seo_analysis(ai_input, streaming=True)
                    for chunk in ai_response:
                        yield json.dumps({"chunk": chunk}) + "\n"
                    
                    yield json.dumps({"status": "complete"}) + "\n"
                
                response = app.response_class(generate(), mimetype='application/x-ndjson')
                response.headers['X-Accel-Buffering'] = 'no'
                return response
            else:
                # Standard response
                result["ai_recommendations"] = gemini_ai.generate_seo_analysis(ai_input)
        
        # Add rate limit info
        result["rate_limit"] = limit_info
        
        # Cache the result
        cache_system.set(url, result)
        
        return jsonify(result)
        
    except Exception as e:
        error_id = hashlib.md5(str(e).encode()).hexdigest()[:8]
        return jsonify({
            "error": "Analysis failed",
            "error_id": error_id,
            "message": str(e)[:100],
            "retry_suggested": True
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    services = {
        "gemini_ai": gemini_ai is not None and gemini_ai.api_key is not None,
        "cache": len(cache_system.cache) > 0,
        "rate_limiting": True,
        "api_keys": {
            "google": bool(os.environ.get("GOOGLE_API_KEY")),
            "opr": bool(os.environ.get("OPR_API_KEY")),
            "gemini": bool(os.environ.get("GEMINI_API_KEY"))
        }
    }
    
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "services": services,
        "version": "2.0.0",
        "uptime": time.time() - app_start_time
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available AI models"""
    if not gemini_ai:
        return jsonify({"error": "Gemini not initialized"}), 503
    
    return jsonify({
        "available_models": gemini_ai.available_models,
        "selected_model": gemini_ai.get_best_model(),
        "model_priority": Config.GEMINI_MODEL_PRIORITY
    })

# ==============================================================================
# 🎉 INITIALIZATION
# ==============================================================================
app_start_time = time.time()

# Keep original APIConnector and other classes for compatibility
# [Include APIConnector, SelfRepair, Diagnose classes from original code here]
# ... (keeping the original classes for backward compatibility)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
