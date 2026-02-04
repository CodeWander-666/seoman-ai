import requests
from bs4 import BeautifulSoup
import time
from collections import OrderedDict, deque
import google.generativeai as genai
import os
import re
import ssl
import socket
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
import concurrent.futures
from user_agents import parse

# ==================== SECURITY & CACHE ====================
class SecurityManager:
    """Thread-safe rate limiting and security"""
    def __init__(self, limit=30, period=60):
        self.limit = limit
        self.period = period
        self.requests = OrderedDict()
        self.blocked_ips = set()
        self.lock = threading.RLock()
    
    def is_allowed(self, ip: str) -> bool:
        with self.lock:
            if ip in self.blocked_ips:
                return False
            
            now = time.time()
            # Clean old entries
            while self.requests and now - list(self.requests.values())[0] > self.period:
                self.requests.popitem(last=False)
            
            # Check rate limit
            ip_requests = [t for ip_addr, t in self.requests.items() if ip_addr == ip]
            if len(ip_requests) >= self.limit:
                self.blocked_ips.add(ip)
                # Auto-unblock after 1 hour
                threading.Timer(3600, lambda: self.blocked_ips.discard(ip)).start()
                return False
            
            self.requests[ip] = now
            return True

class LRUCache:
    """Least Recently Used cache with TTL"""
    def __init__(self, max_size=1000, ttl=300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.cache.move_to_end(key)
                return value
            else:
                self.delete(key)
        return None
    
    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, time.time())
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]

# ==================== API CONNECTOR ====================
class APIConnector:
    """Handles all external API calls with stealth techniques"""
    
    def __init__(self, user_agent: str):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        self.timeout = 10
        self.robots_cache = {}
    
    def get_technical_audit(self, url: str) -> Dict:
        """Comprehensive technical SEO audit"""
        try:
            # Fetch with stealth headers
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Core Web Vitals via PageSpeed Insights
            core_vitals = self._get_core_web_vitals(url)
            
            # SSL/TLS Analysis
            ssl_grade = self._check_ssl(url)
            
            # Mobile friendliness
            mobile_friendly = self._check_mobile_friendly(soup, response.text)
            
            # Canonical analysis
            canonical_issues = self._analyze_canonical(soup, url)
            
            # Schema validation
            schema_present = self._check_schema(soup)
            
            return {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_type': response.headers.get('content-type', ''),
                'canonical': soup.find('link', rel='canonical'),
                'core_web_vitals': core_vitals,
                'ssl_grade': ssl_grade,
                'mobile_friendly': mobile_friendly,
                'canonical_issues': canonical_issues,
                'schema_present': schema_present,
                'page_size_kb': len(response.content) / 1024,
                'compression': response.headers.get('content-encoding', 'none'),
                'cache_headers': {
                    'cache_control': response.headers.get('cache-control', ''),
                    'expires': response.headers.get('expires', '')
                }
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status_code': 0,
                'core_web_vitals': {'lcp': 0, 'cls': 0, 'inp': 0}
            }
    
    def get_content_audit(self, url: str) -> Dict:
        """Advanced content analysis with entity recognition"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content
            text = soup.get_text()
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = len(words)
            
            # Keyword extraction (TF-IDF style)
            keyword_freq = {}
            for word in words:
                if len(word) > 3 and word not in STOP_WORDS:
                    keyword_freq[word] = keyword_freq.get(word, 0) + 1
            
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # Readability score
            readability = self._calculate_readability(text)
            
            # Entity salience analysis
            entities = self._extract_entities(text)
            
            # Intent classification
            intent = self._classify_intent(text)
            
            # Thin content risk
            thin_risk = word_count < 300 or len(entities) < 5
            
            return {
                'word_count': word_count,
                'top_keywords': top_keywords,
                'readability_score': readability,
                'entity_salience': entities,
                'intent_classification': intent,
                'thin_content_risk': thin_risk,
                'heading_structure': self._analyze_headings(soup),
                'image_alt_coverage': self._check_image_alts(soup),
                'internal_link_count': len(soup.find_all('a', href=True))
            }
            
        except Exception as e:
            return {'error': str(e), 'word_count': 0}
    
    def get_authority_audit(self, url: str) -> Dict:
        """Domain authority and backlink analysis"""
        try:
            domain = urlparse(url).netloc
            
            # Open PageRank API
            opr_score = self._get_open_pagerank(domain)
            
            # Basic backlink estimation
            backlinks = self._estimate_backlinks(domain)
            
            # YMYL classification
            ymyl = self._classify_ymyl(url)
            
            # E-E-A-T scoring
            e_e_a_t = self._calculate_eeat_score(url, opr_score)
            
            # Link toxicity estimation
            toxicity = self._estimate_toxicity(opr_score, backlinks)
            
            return {
                'authority_score': opr_score,
                'backlinks': backlinks,
                'domain': domain,
                'e_e_a_t_score': e_e_a_t,
                'link_toxicity_risk': toxicity,
                'ymyl_category': ymyl,
                'social_signals': self._check_social_presence(domain)
            }
            
        except Exception as e:
            return {'error': str(e), 'authority_score': 0}
    
    # ========== PRIVATE METHODS ==========
    
    def _get_core_web_vitals(self, url: str) -> Dict:
        """Fetch Core Web Vitals from PageSpeed Insights"""
        try:
            psi_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile"
            response = requests.get(psi_url, timeout=15)
            data = response.json()
            
            audits = data.get('lighthouseResult', {}).get('audits', {})
            
            return {
                'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0),
                'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                'inp': audits.get('interaction-to-next-paint', {}).get('numericValue', 0),
                'fcp': audits.get('first-contentful-paint', {}).get('numericValue', 0),
                'tti': audits.get('interactive', {}).get('numericValue', 0),
                'speed_index': audits.get('speed-index', {}).get('numericValue', 0),
                'performance_score': data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100
            }
        except:
            return {'lcp': 0, 'cls': 0, 'inp': 0, 'performance_score': 0}
    
    def _check_ssl(self, url: str) -> str:
        """Check SSL/TLS configuration"""
        try:
            hostname = urlparse(url).hostname
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (expires - datetime.now()).days
                    
                    if days_left < 30:
                        return 'F'
                    elif days_left < 90:
                        return 'C'
                    else:
                        return 'A'
        except:
            return 'F'
    
    def _calculate_readability(self, text: str) -> float:
        """Flesch-Kincaid reading ease approximation"""
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(re.findall(r'\b\w+\b', text))
        syllables = len(re.findall(r'[aeiouy]+', text.lower()))
        
        if sentences == 0 or words == 0:
            return 0
        
        readability = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        return max(0, min(100, readability))
    
    def _extract_entities(self, text: str) -> Dict:
        """Simple entity extraction"""
        entities = {}
        # Look for proper nouns (capitalized words)
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        for word in words:
            if len(word) > 2:
                entities[word] = entities.get(word, 0) + 1
        
        return dict(sorted(entities.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _classify_intent(self, text: str) -> str:
        """Classify search intent"""
        text_lower = text.lower()
        
        # Transactional intent words
        transactional = ['buy', 'purchase', 'order', 'price', 'deal', 'discount', 'sale']
        # Informational intent words
        informational = ['how', 'what', 'why', 'guide', 'tutorial', 'learn', 'explain']
        # Navigational intent words
        navigational = ['home', 'login', 'contact', 'about', 'services', 'products']
        
        t_count = sum(1 for word in transactional if word in text_lower)
        i_count = sum(1 for word in informational if word in text_lower)
        n_count = sum(1 for word in navigational if word in text_lower)
        
        max_count = max(t_count, i_count, n_count)
        
        if max_count == t_count:
            return 'transactional'
        elif max_count == i_count:
            return 'informational'
        else:
            return 'navigational'

# ==================== ADVANCED INTELLIGENCE ====================
class AdvancedIntelligence:
    """Implements the forecasting and competitiveness algorithms from The Art of SEO"""
    
    def calculate_traffic_forecast(self, authority_score: float, word_count: int, 
                                  backlinks: int, seasonality: int) -> Dict:
        """
        Traffic forecasting algorithm based on:
        Authority Multiplier (Auth Score * 25)
        Content Depth (Word Count / 50)
        Backlink Value (Backlinks * 0.8)
        """
        # Base formula from The Art of SEO principles
        base_traffic = (authority_score * 25) + (word_count / 50) + (backlinks * 0.8)
        
        # Competition factor (rich get richer)
        if authority_score > 4:
            base_traffic *= 1.2
        
        # Seasonal adjustment (Q4 boost)
        if seasonality in [10, 11, 12]:  # October-December
            base_traffic *= 1.1
        
        # Apply industry variance
        return {
            'pessimistic': int(base_traffic * 0.8),
            'expected': int(base_traffic),
            'optimistic': int(base_traffic * 1.5),
            'formula': 'Traffic = (Authority × 25) + (Words ÷ 50) + (Backlinks × 0.8)',
            'seasonality_boost': seasonality in [10, 11, 12],
            'competition_boost': authority_score > 4
        }
    
    def analyze_competitiveness(self, keywords: List[Tuple[str, int]], 
                               authority_score: float, word_count: int) -> Dict:
        """Calculate opportunity scores for keywords"""
        opportunities = []
        
        for keyword, frequency in keywords[:10]:  # Top 10 keywords
            # Keyword difficulty approximation
            difficulty = min(100, (100 - (authority_score * 10)) + (frequency * 2))
            
            # Opportunity score (inverse of difficulty, weighted by frequency)
            opportunity_score = max(0, 100 - difficulty)
            
            # Content gap detection
            content_gap = difficulty < 50 and word_count < 1000
            
            opportunities.append({
                'keyword': keyword,
                'frequency': frequency,
                'difficulty': round(difficulty, 1),
                'opportunity_score': round(opportunity_score, 1),
                'content_gap': content_gap,
                'recommendation': self._get_keyword_recommendation(difficulty, opportunity_score)
            })
        
        # Overall competitiveness score
        avg_difficulty = sum(o['difficulty'] for o in opportunities) / len(opportunities) if opportunities else 0
        avg_opportunity = sum(o['opportunity_score'] for o in opportunities) / len(opportunities) if opportunities else 0
        
        return {
            'keywords': opportunities,
            'overall_difficulty': round(avg_difficulty, 1),
            'overall_opportunity': round(avg_opportunity, 1),
            'competitiveness_level': self._get_competitiveness_level(avg_difficulty),
            'recommended_actions': self._get_competitive_actions(avg_difficulty, avg_opportunity)
        }
    
    def _get_keyword_recommendation(self, difficulty: float, opportunity: float) -> str:
        if opportunity > 70:
            return "High Priority - Low competition, high opportunity"
        elif opportunity > 40:
            return "Medium Priority - Moderate competition"
        else:
            return "Low Priority - Highly competitive"
    
    def _get_competitiveness_level(self, difficulty: float) -> str:
        if difficulty < 30:
            return "Low Competition"
        elif difficulty < 60:
            return "Moderate Competition"
        else:
            return "High Competition"
    
    def _get_competitive_actions(self, difficulty: float, opportunity: float) -> List[str]:
        actions = []
        
        if opportunity > 60:
            actions.append("Focus on quick-win keywords with content optimization")
        if difficulty > 50:
            actions.append("Build authority through backlinks and partnerships")
        if opportunity < 30:
            actions.append("Consider long-tail variations with less competition")
        
        return actions

# ==================== GEMINI AI INTEGRATION ====================
class GeminiAI:
    """AI Strategic Advisor using Google's Gemini models"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = self._discover_model()
        else:
            self.model = None
    
    def _discover_model(self):
        """Discover available Gemini models with fallbacks"""
        model_priority = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro'
        ]
        
        for model_name in model_priority:
            try:
                model = genai.GenerativeModel(model_name)
                # Test with small prompt
                model.generate_content("Test")
                return model
            except:
                continue
        
        return None
    
    def is_available(self) -> bool:
        return self.model is not None
    
    def generate_audit_stream(self, metrics: Dict):
        """Streaming AI analysis for real-time insights"""
        if not self.model:
            yield "AI Advisor unavailable. Please check API configuration."
            return
        
        prompt = f"""
        ACT as: Senior SEO Consultant with 15+ years experience, author of "The Art of SEO" 4th Edition.
        
        ANALYZE these metrics for strategic SEO recommendations:
        
        TECHNICAL HEALTH:
        - Core Web Vitals: {metrics.get('technical', {}).get('core_web_vitals', {})}
        - Mobile Friendly: {metrics.get('technical', {}).get('mobile_friendly', False)}
        - SSL Grade: {metrics.get('technical', {}).get('ssl_grade', 'F')}
        
        CONTENT QUALITY:
        - Word Count: {metrics.get('content', {}).get('word_count', 0)}
        - Readability: {metrics.get('content', {}).get('readability_score', 0)}
        - Intent: {metrics.get('content', {}).get('intent_classification', 'unknown')}
        
        AUTHORITY SIGNALS:
        - Authority Score: {metrics.get('authority', {}).get('authority_score', 0)}
        - E-E-A-T Score: {metrics.get('authority', {}).get('e_e_a_t_score', 0)}
        - YMYL Category: {metrics.get('authority', {}).get('ymyl_category', None)}
        
        Provide your analysis in this EXACT JSON format:
        {{
            "technical_fixes": ["Fix 1", "Fix 2", "Fix 3"],
            "content_opportunities": ["Opportunity 1", "Opportunity 2"],
            "quick_wins": ["Quick win 1"],
            "strategic_recommendations": ["Long-term strategy 1", "Long-term strategy 2"],
            "risk_assessment": "Assessment text",
            "sge_preparedness": "Preparedness analysis for Search Generative Experience"
        }}
        
        Base recommendations on "The Art of SEO" 4th Edition principles.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                },
                stream=True
            )
            
            for chunk in response:
                yield chunk.text
                
        except Exception as e:
            yield f"AI Analysis Error: {str(e)}"

# ==================== CRAWL STATISTICS ====================
class CrawlStats:
    """Analyze internal link structure and crawlability"""
    
    def __init__(self, start_url: str, max_pages: int = 50, max_depth: int = 3):
        self.start_url = start_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited = set()
        self.internal_links = set()
        self.external_links = set()
        self.orphan_pages = set()
        self.redirect_chains = []
        
    def analyze(self) -> Dict:
        """Perform limited crawl analysis"""
        try:
            self._crawl_recursive(self.start_url, depth=0)
            
            return {
                'pages_crawled': len(self.visited),
                'internal_links_found': len(self.internal_links),
                'external_links_found': len(self.external_links),
                'orphan_pages_detected': len(self.orphan_pages),
                'crawl_depth_achieved': self.max_depth,
                'internal_link_ratio': len(self.internal_links) / max(len(self.visited), 1),
                'site_structure_health': self._calculate_structure_health(),
                'crawl_warnings': self._generate_crawl_warnings()
            }
        except Exception as e:
            return {'crawl_error': str(e)}
    
    def _crawl_recursive(self, url: str, depth: int):
        """Recursive crawl with depth limit"""
        if depth >= self.max_depth or len(self.visited) >= self.max_pages:
            return
        
        if url in self.visited:
            return
        
        self.visited.add(url)
        
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                absolute_url = urljoin(url, href)
                
                # Classify link
                if self._is_internal(absolute_url):
                    self.internal_links.add(absolute_url)
                    if depth < self.max_depth - 1:
                        self._crawl_recursive(absolute_url, depth + 1)
                else:
                    self.external_links.add(absolute_url)
                    
        except:
            pass
    
    def _is_internal(self, url: str) -> bool:
        """Check if URL is internal to the domain"""
        start_domain = urlparse(self.start_url).netloc
        url_domain = urlparse(url).netloc
        return url_domain == start_domain or url_domain.endswith(start_domain)
    
    def _calculate_structure_health(self) -> float:
        """Calculate site structure health score"""
        if len(self.visited) == 0:
            return 0
        
        internal_ratio = len(self.internal_links) / len(self.visited)
        depth_score = min(1, self.max_depth / 5)
        
        return (internal_ratio * 0.7 + depth_score * 0.3) * 100
    
    def _generate_crawl_warnings(self) -> List[str]:
        """Generate crawl warnings"""
        warnings = []
        
        if len(self.orphan_pages) > 0:
            warnings.append(f"{len(self.orphan_pages)} orphan pages detected")
        
        if len(self.visited) < 5:
            warnings.append("Limited crawl coverage - site may be small or have crawl barriers")
        
        if len(self.external_links) > len(self.internal_links) * 2:
            warnings.append("High external link ratio - may dilute PageRank")
        
        return warnings

# Common English stop words
STOP_WORDS = {
    'the', 'and', 'to', 'of', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'you', 
    'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'all', 'have', 'new', 'more', 
    'an', 'was', 'we', 'will', 'home', 'can', 'us', 'about', 'if', 'page', 'my', 'has', 'search', 
    'free', 'but', 'our', 'one', 'other', 'do', 'no', 'time', 'they', 'site', 'he', 'up', 'may', 
    'what', 'which', 'their', 'news', 'out', 'use', 'any', 'there', 'see', 'only', 'so', 'his', 
    'when', 'contact', 'here', 'business', 'who', 'web', 'also', 'now', 'help', 'get', 'pm', 'view', 
    'online', 'c', 'e', 'first', 'am', 'been', 'would', 'how', 'were', 'me', 's', 'services', 
    'some', 'these', 'click', 'its', 'like', 'service', 'x', 'than', 'find', 'price', 'date', 
    'back', 'top', 'people', 'had', 'list', 'name', 'just', 'over', 'state', 'year', 'day', 'into', 
    'email', 'two', 'health', 'n', 'world', 're', 'next', 'used', 'go', 'b', 'work', 'last', 'most', 
    'products', 'music', 'buy', 'data', 'make', 'them', 'should', 'product', 'system', 'post', 
    'her', 'city', 't', 'add', 'policy', 'number', 'such', 'please', 'available', 'copyright', 
    'support', 'message', 'after', 'best', 'software', 'then', 'jan', 'good', 'video', 'well', 
    'd', 'where', 'info', 'rights', 'public', 'books', 'high', 'school', 'through', 'm', 'each', 
    'links', 'she', 'review', 'years', 'order', 'very', 'privacy', 'book', 'items', 'company', 
    'r', 'read', 'group', 'sex', 'need', 'many', 'user', 'said', 'de', 'does', 'set', 'under', 
    'general', 'research', 'university', 'january', 'mail', 'full', 'map', 'reviews', 'program', 
    'life', 'know', 'games', 'way', 'days', 'management', 'p', 'part', 'could', 'great', 'united', 
    'hotel', 'real', 'f', 'item', 'international', 'center', 'ebay', 'must', 'store', 'travel', 
    'comments', 'made', 'development', 'report', 'off', 'member', 'details', 'line', 'terms', 
    'before', 'hotels', 'did', 'send', 'right', 'type', 'because', 'local', 'those', 'using', 
    'results', 'office', 'education', 'national', 'car', 'design', 'take', 'posted', 'internet', 
    'address', 'community', 'within', 'states', 'area', 'want', 'phone', 'dvd', 'shipping', 
    'reserved', 'subject', 'between', 'forum', 'family', 'l', 'long', 'based', 'w', 'code', 
    'show', 'o', 'even', 'black', 'check', 'special', 'prices', 'website', 'index', 'being', 
    'women', 'much', 'sign', 'file', 'link', 'open', 'today', 'technology', 'south', 'case', 
    'project', 'same', 'pages', 'uk', 'version', 'section', 'own', 'found', 'sports', 'house', 
    'related', 'security', 'both', 'g', 'county', 'american', 'photo', 'game', 'members', 'power', 
    'while', 'care', 'network', 'down', 'computer', 'systems', 'three', 'total', 'place', 'end', 
    'following', 'download', 'h', 'him', 'without', 'per', 'access', 'think', 'north', 'resources', 
    'current', 'posts', 'big', 'media', 'law', 'control', 'water', 'history', 'pictures', 'size', 
    'art', 'personal', 'since', 'including', 'guide', 'shop', 'directory', 'board', 'location', 
    'change', 'white', 'text', 'small', 'rating', 'rate', 'government', 'children', 'during', 
    'usa', 'return', 'students', 'v', 'shopping', 'account', 'times', 'sites', 'level', 'digital', 
    'profile', 'previous', 'form', 'events', 'love', 'old', 'john', 'main', 'call', 'hours', 
    'image', 'department', 'title', 'description', 'non', 'k', 'y', 'insurance', 'another', 
    'why', 'shall', 'property', 'class', 'cd', 'still', 'money', 'quality', 'every', 'listing', 
    'content', 'country', 'private', 'little', 'visit', 'save', 'tools', 'low', 'reply', 
    'customer', 'december', 'compare', 'movies', 'include', 'college', 'value', 'article', 
    'york', 'man', 'card', 'jobs', 'provide', 'j', 'food', 'source', 'author', 'different', 
    'press', 'u', 'learn', 'sale', 'around', 'print', 'course', 'job', 'canada', 'process', 
    'teen', 'room', 'stock', 'training', 'too', 'credit', 'point', 'join', 'science', 'men', 
    'categories', 'advanced', 'west', 'sales', 'look', 'english', 'left', 'team', 'estate', 
    'box', 'conditions', 'select', 'windows', 'photos', 'gay', 'thread', 'week', 'category', 
    'note', 'live', 'large', 'gallery', 'table', 'register', 'however', 'june', 'october', 
    'november', 'market', 'library', 'really', 'action', 'start', 'series', 'model', 'features', 
    'air', 'industry', 'plan', 'human', 'provided', 'tv', 'yes', 'required', 'second', 'hot', 
    'accessories', 'cost', 'movie', 'forums', 'march', 'la', 'september', 'better', 'say', 
    'questions', 'july', 'yahoo', 'going', 'medical', 'test', 'friend', 'come', 'dec', 'server', 
    'pc', 'study', 'application', 'cart', 'staff', 'articles', 'san', 'feedback', 'again', 
    'play', 'looking', 'issues', 'april', 'never', 'users', 'complete', 'street', 'topic', 
    'comment', 'financial', 'things', 'working', 'against', 'standard', 'tax', 'person', 
    'below', 'mobile', 'less', 'got', 'blog', 'party', 'payment', 'equipment', 'login', 
    'student', 'let', 'programs', 'offers', 'legal', 'above', 'recent', 'park', 'stores', 
    'side', 'act', 'problem', 'red', 'give', 'memory', 'performance', 'social', 'q', 
    'august', 'quote', 'language', 'story', 'sell', 'options', 'experience', 'rates', 'create', 
    'key', 'body', 'young', 'america', 'important', 'field', 'few', 'east', 'paper', 'single', 
    'ii', 'age', 'activities', 'club', 'example', 'girls', 'additional', 'password', 'z', 
    'latest', 'something', 'road', 'gift', 'question', 'changes', 'night', 'ca', 'hard', 
    'texas', 'oct', 'pay', 'four', 'poker', 'status', 'browse', 'issue', 'range', 'building', 
    'seller', 'court', 'february', 'always', 'result', 'audio', 'light', 'write', 'war', 
    'nov', 'offer', 'blue', 'groups', 'al', 'easy', 'given', 'files', 'event', 'release', 
    'analysis', 'request', 'fax', 'china', 'making', 'picture', 'needs', 'possible', 'might', 
    'professional', 'yet', 'month', 'major', 'star', 'areas', 'future', 'space', 'committee', 
    'hand', 'sun', 'cards', 'problems', 'london', 'washington', 'meeting', 'rss', 'become', 
    'interest', 'id', 'child', 'keep', 'enter', 'california', 'porn', 'share', 'similar', 
    'garden', 'schools', 'million', 'added', 'reference', 'companies', 'listed', 'baby', 
    'learning', 'energy', 'run', 'delivery', 'net', 'popular', 'term', 'film', 'stories', 
    'put', 'computers', 'journal', 'reports', 'co', 'try', 'welcome', 'central', 'images', 
    'president', 'notice', 'god', 'original', 'head', 'radio', 'until', 'cell', 'color', 
    'self', 'council', 'away', 'includes', 'track', 'australia', 'discussion', 'archive', 
    'once', 'others', 'entertainment', 'agreement', 'format', 'least', 'society', 'months', 
    'log', 'safety', 'friends', 'sure', 'faq', 'trade', 'edition', 'cars', 'messages', 
    'marketing', 'tell', 'further', 'updated', 'association', 'able', 'having', 'provides', 
    'david', 'fun', 'already', 'green', 'studies', 'close', 'common', 'drive', 'specific', 
    'several', 'gold', 'feb', 'living', 'sep', 'collection', 'called', 'short', 'arts', 
    'lot', 'ask', 'display', 'limited', 'powered', 'solutions', 'means', 'director', 
    'daily', 'beach', 'past', 'natural', 'whether', 'due', 'et', 'electronics', 'five', 
    'upon', 'period', 'planning', 'database', 'says', 'official', 'weather', 'mar', 'land', 
    'average', 'done', 'technical', 'window', 'france', 'pro', 'region', 'island', 'record', 
    'direct', 'microsoft', 'conference', 'environment', 'records', 'st', 'district', 
    'calendar', 'costs', 'style', 'url', 'front', 'statement', 'update', 'parts', 'aug', 
    'ever', 'downloads', 'early', 'miles', 'sound', 'resource', 'present', 'applications', 
    'either', 'ago', 'document', 'word', 'works', 'material', 'bill', 'apr', 'written', 
    'talk', 'federal', 'hosting', 'rules', 'final', 'adult', 'tickets', 'thing', 'centre', 
    'requirements', 'via', 'cheap', 'nude', 'kids', 'finance', 'true', 'minutes', 'else', 
    'mark', 'third', 'rock', 'gifts', 'europe', 'reading', 'topics', 'bad', 'individual', 
    'tips', 'plus', 'auto', 'cover', 'usually', 'edit', 'together', 'videos', 'percent', 
    'fast', 'function', 'fact', 'unit', 'getting', 'global', 'tech', 'meet', 'far', 
    'economic', 'en', 'player', 'projects', 'lyrics', 'often', 'subscribe', 'submit', 
    'germany', 'amount', 'watch', 'included', 'feel', 'though', 'bank', 'risk', 'thanks', 
    'everything', 'deals', 'various', 'words', 'linux', 'jul', 'production', 'commercial', 
    'james', 'weight', 'town', 'heart', 'advertising', 'received', 'choose', 'treatment', 
    'newsletter', 'archives', 'points', 'knowledge', 'magazine', 'error', 'camera', 'jun', 
    'girl', 'currently', 'construction', 'toys', 'registered', 'clear', 'golf', 'receive', 
    'domain', 'methods', 'chapter', 'makes', 'protection', 'policies', 'loan', 'wide', 
    'beauty', 'manager', 'india', 'position', 'taken', 'sort', 'listings', 'models', 
    'michael', 'known', 'half', 'cases', 'step', 'engineering', 'florida', 'simple', 
    'quick', 'none', 'wireless', 'license', 'paul', 'friday', 'lake', 'whole', 'annual', 
    'published', 'basic', 'sony', 'shows', 'corporate', 'google', 'church', 'method', 
    'purchase', 'customers', 'active', 'response', 'practice', 'hardware', 'figure', 
    'materials', 'fire', 'holiday', 'chat', 'enough', 'designed', 'along', 'among', 
    'death', 'writing', 'speed', 'html', 'countries', 'loss', 'face', 'brand', 'discount', 
    'higher', 'effects', 'created', 'remember', 'standards', 'oil', 'bit', 'yellow', 
    'political', 'increase', 'advertise', 'kingdom', 'base', 'near', 'environmental', 
    'thought', 'stuff', 'french', 'storage', 'oh', 'japan', 'doing', 'loans', 'shoes', 
    'entry', 'stay', 'nature', 'orders', 'availability', 'africa', 'summary', 'turn', 
    'mean', 'growth', 'notes', 'agency', 'king', 'monday', 'european', 'activity', 'copy', 
    'although', 'drug', 'pics', 'western', 'income', 'force', 'cash', 'employment', 
    'overall', 'bay', 'river', 'commission', 'ad', 'package', 'contents', 'seen', 'players', 
    'engine', 'port', 'album', 'regional', 'stop', 'supplies', 'started', 'administration', 
    'bar', 'institute', 'views', 'plans', 'double', 'dog', 'build', 'screen', 'exchange', 
    'types', 'soon', 'sponsored', 'lines', 'electronic', 'continue', 'across', 'benefits', 
    'needed', 'season', 'apply', 'someone', 'held', 'ny', 'anything', 'printer', 'condition', 
    'effective', 'believe', 'organization', 'effect', 'asked', 'eur', 'mind', 'sunday', 
    'selection', 'casino', 'pdf', 'lost', 'tour', 'menu', 'volume', 'cross', 'anyone', 
    'mortgage', 'hope', 'silver', 'corporation', 'wish', 'inside', 'solution', 'mature', 
    'role', 'rather', 'weeks', 'addition', 'came', 'supply', 'nothing', 'certain', 'usr', 
    'executive', 'running', 'lower', 'necessary', 'union', 'jewelry', 'according', 'dc', 
    'clothing', 'mon', 'com', 'particular', 'fine', 'names', 'robert', 'homepage', 'hour', 
    'gas', 'skills', 'six', 'bush', 'islands', 'advice', 'career', 'military', 'rental', 
    'decision', 'leave', 'british', 'teens', 'pre', 'huge', 'sat', 'woman', 'facilities', 
    'zip', 'bid', 'kind', 'sellers', 'middle', 'move', 'cable', 'opportunities', 'taking', 
    'values', 'division', 'coming', 'tuesday', 'object', 'lesbian', 'appropriate', 'machine', 
    'logo', 'length', 'actually', 'nice', 'score', 'statistics', 'client', 'ok', 'returns', 
    'capital', 'follow', 'sample', 'investment', 'sent', 'shown', 'saturday', 'christmas', 
    'england', 'culture', 'band', 'flash', 'ms', 'lead', 'george', 'choice', 'went', 
    'starting', 'registration', 'fri', 'thursday', 'courses', 'consumer', 'hi', 'airport', 
    'foreign', 'artist', 'outside', 'furniture', 'levels', 'channel', 'letter', 'mode', 
    'phones', 'ideas', 'wednesday', 'structure', 'fund', 'summer', 'allow', 'degree', 
    'contract', 'button', 'releases', 'wed', 'homes', 'super', 'male', 'matter', 'custom', 
    'virginia', 'almost', 'took', 'located', 'multiple', 'asian', 'distribution', 'editor', 
    'inn', 'industrial', 'cause', 'potential', 'song', 'cnet', 'ltd', 'los', 'hp', 'focus', 
    'late', 'fall', 'featured', 'idea', 'rooms', 'female', 'responsible', 'inc', 'communications', 
    'win', 'associated', 'thomas', 'primary', 'cancer', 'numbers', 'reason', 'tool', 
    'browser', 'spring', 'foundation', 'answer', 'voice', 'eg', 'friendly', 'schedule', 
    'documents', 'communication', 'purpose', 'feature', 'bed', 'comes', 'police', 'everyone', 
    'independent', 'ip', 'approach', 'cameras', 'brown', 'physical', 'operating', 'hill', 
    'maps', 'medicine', 'deal', 'hold', 'ratings', 'chicago', 'forms', 'glass', 'happy', 
    'tue', 'smith', 'wanted', 'developed', 'thank', 'safe', 'unique', 'survey', 'prior', 
    'telephone', 'sport', 'ready', 'feed', 'animal', 'sources', 'mexico', 'population', 
    'pa', 'regular', 'secure', 'navigation', 'operations', 'therefore', 'ass', 'simply', 
    'evidence', 'station', 'christian', 'round', 'paypal', 'favorite', 'understand', 
    'option', 'master', 'valley', 'recently', 'probably', 'thu', 'rentals', 'sea', 'built', 
    'publications', 'blood', 'cut', 'worldwide', 'improve', 'connection', 'publisher', 
    'hall', 'larger', 'anti', 'networks', 'earth', 'parents', 'nokia', 'impact', 'transfer', 
    'introduction', 'kitchen', 'strong', 'tel', 'carolina', 'wedding', 'properties', 
    'hospital', 'ground', 'overview', 'ship', 'accommodation', 'owners', 'disease', 
    'excellent', 'paid', 'italy', 'perfect', 'hair', 'opportunity', 'kit', 'classic', 
    'basis', 'command', 'cities', 'william', 'express', 'anal', 'award', 'distance', 
    'tree', 'peter', 'assessment', 'ensure', 'thus', 'wall', 'ie', 'involved', 'extra', 
    'especially', 'interface', 'pussy', 'partners', 'budget', 'rated', 'guides', 'success', 
    'maximum', 'ma', 'operation', 'existing', 'quite', 'selected', 'boy', 'amazon', 
    'patients', 'restaurants', 'beautiful', 'warning', 'wine', 'locations', 'horse', 
    'vote', 'forward', 'flowers', 'stars', 'significant', 'lists', 'technologies', 
    'owner', 'retail', 'animals', 'useful', 'directly', 'manufacturer', 'ways', 'est', 
    'son', 'providing', 'rule', 'mac', 'housing', 'takes', 'iii', 'gmt', 'bring', 
    'catalog', 'searches', 'max', 'trying', 'mother', 'authority', 'considered', 'told', 
    'xml', 'traffic', 'programme', 'joined', 'input', 'strategy', 'feet', 'agent', 
    'valid', 'bin', 'modern', 'senior', 'ireland', 'sexy', 'teaching', 'door', 'grand', 
    'testing', 'trial', 'charge', 'units', 'instead', 'canadian', 'cool', 'normal', 
    'wrote', 'enterprise', 'ships', 'entire', 'educational', 'md', 'leading', 'metal', 
    'positive', 'fl', 'fitness', 'chinese', 'opinion', 'mb', 'asia', 'football', 'abstract', 
    'uses', 'output', 'funds', 'mr', 'greater', 'likely', 'develop', 'employees', 'artists', 
    'alternative', 'processing', 'responsibility', 'resolution', 'java', 'guest', 
    'seems', 'publication', 'pass', 'relations', 'trust', 'van', 'contains', 'session', 
    'multi', 'photography', 'republic', 'fees', 'components', 'vacation', 'century', 
    'academic', 'assistance', 'completed', 'skin', 'graphics', 'indian', 'prev', 'ads', 
    'mary', 'il', 'expected', 'ring', 'grade', 'dating', 'pacific', 'mountain', 'organizations', 
    'pop', 'filter', 'mailing', 'vehicle', 'longer', 'consider', 'int', 'northern', 
    'behind', 'panel', 'floor', 'german', 'buying', 'match', 'proposed', 'default', 
    'require', 'iraq', 'boys', 'outdoor', 'deep', 'morning', 'otherwise', 'allows', 
    'rest', 'protein', 'plant', 'reported', 'hit', 'transportation', 'mm', 'pool', 
    'mini', 'politics', 'partner', 'disclaimer', 'authors', 'boards', 'faculty', 'parties', 
    'fish', 'membership', 'mission', 'eye', 'string', 'sense', 'modified', 'pack', 
    'released', 'stage', 'internal', 'goods', 'recommended', 'born', 'unless', 'richard', 
    'detailed', 'japanese', 'race', 'approved', 'background', 'target', 'except', 
    'character', 'usb', 'maintenance', 'ability', 'maybe', 'functions', 'ed', 'moving', 
    'brands', 'places', 'php', 'pretty', 'trademarks', 'phentermine', 'spain', 'southern', 
    'yourself', 'etc', 'winter', 'rape', 'battery', 'youth', 'pressure', 'submitted', 
    'boston', 'incest', 'debt', 'keywords', 'medium', 'television', 'interested', 
    'core', 'break', 'purposes', 'throughout', 'sets', 'dance', 'wood', 'msn', 'itself', 
    'defined', 'papers', 'playing', 'awards', 'fee', 'studio', 'reader', 'virtual', 
    'device', 'established', 'answers', 'rent', 'las', 'remote', 'dark', 'programming', 
    'external', 'apple', 'le', 'regarding', 'instructions', 'min', 'offered', 'theory', 
    'enjoy', 'remove', 'aid', 'surface', 'minimum', 'visual', 'host', 'variety', 
    'teachers', 'isbn', 'martin', 'manual', 'block', 'subjects', 'agents', 'increased', 
    'repair', 'fair', 'civil', 'steel', 'understanding', 'songs', 'fixed', 'wrong', 
    'beginning', 'hands', 'associates', 'finally', 'az', 'updates', 'desktop', 'classes', 
    'paris', 'ohio', 'gets', 'sector', 'capacity', 'requires', 'jersey', 'un', 'fat', 
    'fully', 'father', 'electric', 'saw', 'instruments', 'quotes', 'officer', 'driver', 
    'businesses', 'dead', 'respect', 'unknown', 'specified', 'restaurant', 'mike', 
    'trip', 'pst', 'worth', 'mi', 'procedures', 'poor', 'teacher', 'xxx', 'eyes', 
    'relationship', 'workers', 'farm', 'fucking', 'georgia', 'peace', 'traditional', 
    'campus', 'tom', 'showing', 'creative', 'coast', 'benefit', 'progress', 'funding', 
    'devices', 'lord', 'grant', 'sub', 'agree', 'fiction', 'hear', 'sometimes', 'watches', 
    'careers', 'beyond', 'goes', 'families', 'led', 'museum', 'themselves', 'fan', 
    'transport', 'interesting', 'blogs', 'wife', 'evaluation', 'accepted', 'former', 
    'implementation', 'ten', 'hits', 'zone', 'complex', 'th', 'cat', 'galleries', 
    'references', 'die', 'presented', 'jack', 'flat', 'flow', 'agencies', 'literature', 
    'respective', 'parent', 'spanish', 'michigan', 'columbia', 'setting', 'dr', 'scale', 
    'stand', 'economy', 'highest', 'helpful', 'monthly', 'critical', 'frame', 'musical', 
    'definition', 'secretary', 'angeles', 'networking', 'path', 'australian', 'employee', 
    'chief', 'gives', 'kb', 'bottom', 'magazines', 'packages', 'detail', 'francisco', 
    'laws', 'changed', 'pet', 'heard', 'begin', 'individuals', 'colorado', 'royal', 
    'clean', 'switch', 'russian', 'largest', 'african', 'guy', 'titles', 'relevant', 
    'guidelines', 'justice', 'connect', 'bible', 'dev', 'cup', 'basket', 'applied', 
    'weekly', 'vol', 'installation', 'described', 'demand', 'pp', 'suite', 'vegas', 
    'na', 'square', 'chris', 'attention', 'advance', 'skip', 'diet', 'army', 'auction', 
    'gear', 'lee', 'os', 'difference', 'allowed', 'correct', 'charles', 'nation', 
    'selling', 'lots', 'piece', 'sheet', 'firm', 'seven', 'older', 'illinois', 
    'regulations', 'elements', 'species', 'jump', 'cells', 'module', 'course', 
    'carey', 'approach', 'query', 'climate', 'feeds', 'banking', 'officer', 
    'sum', 'defined', 'pub', 'roman', 'basis', 'apply', 'said', 'award', 'site', 
    'net', 'catalog', 'takes', 'young', 'null', 'zero', 'one', 'two', 'three', 
    'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
}
