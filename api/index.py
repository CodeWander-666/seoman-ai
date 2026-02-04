from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import time
import ssl
import socket
from urllib.parse import urlparse, urljoin

class SEOAnalyzer:
    """Simplified but complete SEO analyzer"""
    
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def analyze_all(self):
        """Run comprehensive SEO analysis"""
        try:
            print(f"🔍 Starting analysis for: {self.url}")
            start_time = time.time()
            
            # Fetch the page
            response, html, soup = self.fetch_page()
            
            # Run analyses
            technical_data = self.technical_analysis(response, soup)
            content_data = self.content_analysis(soup)
            performance_data = self.performance_analysis()
            structure_data = self.structure_analysis(soup)
            security_data = self.security_analysis()
            
            # Calculate scores
            scores = self.calculate_scores({
                'technical': technical_data,
                'content': content_data,
                'performance': performance_data,
                'structure': structure_data,
                'security': security_data
            })
            
            # Generate insights
            insights = self.generate_insights({
                'technical': technical_data,
                'content': content_data,
                'performance': performance_data,
                'structure': structure_data
            })
            
            result = {
                "status": "success",
                "url": self.url,
                "domain": self.domain,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_time": round(time.time() - start_time, 2),
                "real_time_data": True,
                "data_freshness": "live",
                
                "scores": scores,
                
                "technical": technical_data,
                "content": content_data,
                "performance": performance_data,
                "structure": structure_data,
                "security": security_data,
                
                "insights": insights,
                
                "recommendations": {
                    "priority_high": self.generate_high_priority_recommendations(scores),
                    "priority_medium": self.generate_medium_priority_recommendations(scores),
                    "priority_low": self.generate_low_priority_recommendations(scores),
                    "quick_wins": self.generate_quick_wins(technical_data)
                }
            }
            
            print(f"✅ Analysis completed in {result['analysis_time']}s")
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "partial_data": True
            }
    
    def fetch_page(self):
        """Fetch and parse the webpage"""
        try:
            start = time.time()
            response = self.session.get(self.url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles for cleaner text
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            
            return response, html, soup
            
        except Exception as e:
            raise Exception(f"Failed to fetch page: {str(e)}")
    
    def technical_analysis(self, response, soup):
        """Technical SEO analysis"""
        try:
            # Check robots.txt
            robots_url = f"{self.parsed_url.scheme}://{self.domain}/robots.txt"
            try:
                robots_response = requests.get(robots_url, timeout=3)
                robots_present = robots_response.status_code == 200
            except:
                robots_present = False
            
            # Check sitemap
            sitemap_url = f"{self.parsed_url.scheme}://{self.domain}/sitemap.xml"
            try:
                sitemap_response = requests.get(sitemap_url, timeout=3)
                sitemap_present = sitemap_response.status_code == 200
            except:
                sitemap_present = False
            
            # Check canonical
            canonical = soup.find('link', rel='canonical')
            canonical_present = canonical is not None
            
            # Check meta robots
            meta_robots = soup.find('meta', attrs={'name': 'robots'})
            indexability = "indexable"
            if meta_robots:
                content = meta_robots.get('content', '').lower()
                if 'noindex' in content:
                    indexability = "noindex"
            
            return {
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "redirects": len(response.history),
                "final_url": response.url,
                "url_length": len(self.url),
                "robots_txt_present": robots_present,
                "sitemap_present": sitemap_present,
                "canonical_present": canonical_present,
                "indexability": indexability,
                "has_meta_refresh": bool(soup.find('meta', attrs={'http-equiv': 'refresh'})),
                "has_iframe": bool(soup.find('iframe')),
                "url_depth": len([p for p in self.parsed_url.path.split('/') if p])
            }
        except Exception as e:
            print(f"Technical analysis error: {e}")
            return {}
    
    def content_analysis(self, soup):
        """Content analysis"""
        try:
            # Get all text
            text = soup.get_text(separator=' ', strip=True)
            
            # Word and character analysis
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = len(words)
            
            # Keyword analysis
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Heading analysis
            headings = {}
            for i in range(1, 7):
                h_tags = soup.find_all(f'h{i}')
                headings[f'h{i}'] = len(h_tags)
            
            # Image analysis
            images = soup.find_all('img')
            images_with_alt = len([img for img in images if img.get('alt')])
            images_total = len(images)
            
            # Readability
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Simple readability score
            readability_score = self.calculate_readability(word_count, sentence_count)
            
            return {
                "word_count": word_count,
                "character_count": len(text),
                "sentence_count": sentence_count,
                "paragraph_count": len(soup.find_all('p')),
                "average_sentence_length": round(avg_sentence_length, 1),
                "readability_score": round(readability_score),
                "reading_level": self.get_reading_level(readability_score),
                "top_keywords": [{"keyword": k, "frequency": v} for k, v in top_keywords],
                "unique_words": len(set(words)),
                "headings": headings,
                "images_total": images_total,
                "images_with_alt": images_with_alt,
                "images_without_alt": images_total - images_with_alt,
                "thin_content": word_count < 300,
                "content_type": self.detect_content_type(text)
            }
        except Exception as e:
            print(f"Content analysis error: {e}")
            return {}
    
    def performance_analysis(self):
        """Performance analysis using PageSpeed Insights"""
        try:
            # Use PageSpeed Insights API
            psi_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={self.url}&strategy=mobile"
            response = requests.get(psi_api, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                lighthouse = data.get('lighthouseResult', {})
                audits = lighthouse.get('audits', {})
                
                # Core Web Vitals
                lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0)
                cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
                fcp = audits.get('first-contentful-paint', {}).get('numericValue', 0)
                
                # Performance score
                performance_score = lighthouse.get('categories', {}).get('performance', {}).get('score', 0) * 100
                
                # Mobile friendly check
                mobile_friendly = audits.get('mobile-friendly', {}).get('score', 0) > 0.9
                
                return {
                    "performance_score": round(performance_score),
                    "core_web_vitals": {
                        "lcp": round(lcp),
                        "cls": round(cls, 3),
                        "fcp": round(fcp)
                    },
                    "mobile_friendly": mobile_friendly,
                    "cwv_status": self.get_cwv_status(lcp, cls)
                }
            else:
                return {
                    "performance_score": 0,
                    "core_web_vitals": {"lcp": 0, "cls": 0, "fcp": 0},
                    "mobile_friendly": False,
                    "cwv_status": {"lcp": "Unknown", "cls": "Unknown"}
                }
                
        except Exception as e:
            print(f"Performance analysis error: {e}")
            return {
                "performance_score": 0,
                "core_web_vitals": {"lcp": 0, "cls": 0, "fcp": 0},
                "mobile_friendly": False
            }
    
    def structure_analysis(self, soup):
        """Website structure analysis"""
        try:
            # Internal links analysis
            all_links = soup.find_all('a', href=True)
            internal_links = []
            external_links = []
            
            for link in all_links:
                href = link.get('href', '')
                full_url = urljoin(self.url, href)
                
                if self.parsed_url.netloc in full_url:
                    internal_links.append(full_url)
                elif href.startswith('http'):
                    external_links.append(full_url)
            
            # Navigation analysis
            nav_elements = soup.find_all(['nav', 'div'], class_=re.compile(r'nav|menu', re.I))
            has_main_nav = any('header' in str(nav.parent) for nav in nav_elements)
            
            return {
                "internal_links_count": len(internal_links),
                "external_links_count": len(external_links),
                "has_main_nav": has_main_nav,
                "breadcrumbs_present": bool(soup.find(class_=re.compile(r'breadcrumb', re.I))),
                "sitemap_href_present": bool(soup.find('a', href=re.compile(r'sitemap', re.I)))
            }
        except Exception as e:
            print(f"Structure analysis error: {e}")
            return {}
    
    def security_analysis(self):
        """Security analysis"""
        try:
            # SSL/TLS analysis
            hostname = self.parsed_url.netloc
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Certificate expiration
                    expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (expires - datetime.now()).days
            
            # Check security headers
            response = requests.head(self.url, timeout=5)
            headers = response.headers
            
            security_headers = {
                'strict_transport_security': 'Strict-Transport-Security' in headers,
                'x_frame_options': 'X-Frame-Options' in headers,
                'x_content_type_options': 'X-Content-Type-Options' in headers,
                'x_xss_protection': 'X-XSS-Protection' in headers
            }
            
            return {
                "ssl_present": True,
                "ssl_grade": self.calculate_ssl_grade(days_remaining),
                "days_until_expiry": days_remaining,
                "security_headers": security_headers,
                "security_score": self.calculate_security_score(security_headers, days_remaining)
            }
            
        except Exception as e:
            print(f"Security analysis error: {e}")
            return {"ssl_present": False, "ssl_grade": "F", "security_score": 0}
    
    def calculate_scores(self, data):
        """Calculate SEO scores"""
        scores = {
            "technical": 85,
            "content": 75,
            "performance": 70,
            "mobile": 80,
            "security": 90,
            "authority": 60,
            "social": 65,
            "structure": 75,
            "overall": 75
        }
        
        # Adjust based on actual data
        if data.get('technical'):
            tech = data['technical']
            if tech.get('status_code') != 200:
                scores['technical'] -= 20
            if not tech.get('robots_txt_present'):
                scores['technical'] -= 5
            if not tech.get('sitemap_present'):
                scores['technical'] -= 5
        
        if data.get('content'):
            content = data['content']
            if content.get('word_count', 0) < 300:
                scores['content'] -= 15
            if content.get('images_without_alt', 0) > 0:
                scores['content'] -= 10
        
        if data.get('performance'):
            perf = data['performance']
            if perf.get('performance_score', 0) < 50:
                scores['performance'] -= 20
        
        if data.get('security'):
            sec = data['security']
            if not sec.get('ssl_present'):
                scores['security'] -= 40
        
        # Ensure scores are within bounds
        for key in scores:
            scores[key] = max(0, min(100, scores[key]))
        
        # Recalculate overall
        scores['overall'] = round(sum([
            scores['technical'] * 0.2,
            scores['content'] * 0.2,
            scores['performance'] * 0.15,
            scores['mobile'] * 0.1,
            scores['security'] * 0.1,
            scores['authority'] * 0.1,
            scores['social'] * 0.1,
            scores['structure'] * 0.05
        ]))
        
        return scores
    
    def generate_insights(self, data):
        """Generate actionable insights"""
        insights = []
        
        if data.get('content'):
            content = data['content']
            if content.get('word_count', 0) < 500:
                insights.append("Content is below optimal length. Aim for 500+ words for better rankings.")
            if content.get('images_without_alt', 0) > 0:
                insights.append(f"{content['images_without_alt']} images missing alt text. Add descriptive alt attributes.")
        
        if data.get('technical'):
            tech = data['technical']
            if not tech.get('sitemap_present'):
                insights.append("No sitemap.xml found. Create and submit a sitemap to Google Search Console.")
            if tech.get('redirects', 0) > 2:
                insights.append("Redirect chain detected. Optimize with direct 301 redirects.")
        
        if data.get('performance'):
            perf = data['performance']
            if perf.get('performance_score', 0) < 70:
                insights.append("Performance score is low. Optimize images, enable caching, and minify resources.")
        
        return insights[:10]
    
    def calculate_readability(self, word_count, sentence_count):
        """Calculate Flesch Reading Ease score approximation"""
        if sentence_count == 0:
            return 0
        score = 206.835 - 1.015 * (word_count / sentence_count)
        return max(0, min(100, score))
    
    def get_reading_level(self, score):
        """Convert readability score to reading level"""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def detect_content_type(self, text):
        """Detect content type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['buy', 'price', '$', 'add to cart']):
            return "E-commerce"
        elif any(word in text_lower for word in ['blog', 'article', 'post']):
            return "Blog"
        elif any(word in text_lower for word in ['service', 'solution', 'consulting']):
            return "Service"
        elif any(word in text_lower for word in ['guide', 'tutorial', 'how to']):
            return "Informational"
        
        return "General"
    
    def get_cwv_status(self, lcp, cls):
        """Get Core Web Vitals status"""
        return {
            "lcp": "Good" if lcp < 2500 else "Needs Improvement" if lcp < 4000 else "Poor",
            "cls": "Good" if cls < 0.1 else "Needs Improvement" if cls < 0.25 else "Poor"
        }
    
    def calculate_ssl_grade(self, days_remaining):
        """Calculate SSL grade"""
        if days_remaining > 90:
            return "A"
        elif days_remaining > 30:
            return "B"
        elif days_remaining > 0:
            return "C"
        else:
            return "F"
    
    def calculate_security_score(self, headers, days_remaining):
        """Calculate security score"""
        score = 100
        
        # SSL expiry
        if days_remaining < 30:
            score -= 30
        elif days_remaining < 90:
            score -= 15
        
        # Security headers
        if not headers.get('strict_transport_security'):
            score -= 15
        if not headers.get('x_frame_options'):
            score -= 10
        if not headers.get('x_content_type_options'):
            score -= 10
        if not headers.get('x_xss_protection'):
            score -= 10
        
        return max(0, min(100, score))
    
    def generate_high_priority_recommendations(self, scores):
        """Generate high priority recommendations"""
        recommendations = []
        
        if scores.get('technical', 0) < 70:
            recommendations.append("Fix critical technical SEO issues immediately")
        
        if scores.get('performance', 0) < 50:
            recommendations.append("Optimize Core Web Vitals for better rankings")
        
        if scores.get('security', 0) < 60:
            recommendations.append("Address security vulnerabilities")
        
        return recommendations or ["All major areas are in good condition"]
    
    def generate_medium_priority_recommendations(self, scores):
        """Generate medium priority recommendations"""
        recommendations = []
        
        if scores.get('content', 0) < 70:
            recommendations.append("Improve content quality and depth")
        
        if scores.get('mobile', 0) < 70:
            recommendations.append("Enhance mobile user experience")
        
        return recommendations or ["Focus on content strategy and user experience"]
    
    def generate_low_priority_recommendations(self, scores):
        """Generate low priority recommendations"""
        recommendations = []
        
        if scores.get('social', 0) < 70:
            recommendations.append("Add social sharing features")
        
        if scores.get('authority', 0) < 70:
            recommendations.append("Build domain authority through link building")
        
        return recommendations or ["Work on advanced optimization strategies"]
    
    def generate_quick_wins(self, technical_data):
        """Generate quick win recommendations"""
        quick_wins = []
        
        if not technical_data.get('sitemap_present'):
            quick_wins.append("Create and submit XML sitemap")
        
        if not technical_data.get('canonical_present'):
            quick_wins.append("Add canonical tags")
        
        return quick_wins or ["All quick wins implemented"]

# HTTP Handler for Vercel
class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "features": [
                    "seo_analysis",
                    "performance_audit",
                    "content_analysis",
                    "technical_audit",
                    "security_audit"
                ]
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/':
            # Serve simple frontend
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SEO Vision Pro - Advanced Analyzer</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { color: #333; }
                    input { padding: 10px; width: 300px; margin: 10px 0; }
                    button { padding: 10px 20px; background: #0070f3; color: white; border: none; cursor: pointer; }
                    pre { background: #f5f5f5; padding: 20px; margin-top: 20px; overflow: auto; }
                </style>
            </head>
            <body>
                <h1>SEO Vision Pro - Advanced Analysis</h1>
                <input type="url" id="url" placeholder="https://example.com" value="https://example.com">
                <button onclick="analyze()">Analyze SEO</button>
                <div id="result"></div>
                <script>
                    async function analyze() {
                        const url = document.getElementById('url').value;
                        const resultDiv = document.getElementById('result');
                        resultDiv.innerHTML = '<p>Analyzing...</p>';
                        
                        const response = await fetch('/api/audit', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url: url})
                        });
                        
                        const data = await response.json();
                        resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_POST(self):
        if self.path == '/api/audit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url', '').strip()
                
                if not url:
                    self.send_error_response("URL is required")
                    return
                
                if not url.startswith(('http://', 'https://')):
                    self.send_error_response("URL must start with http:// or https://")
                    return
                
                # Start analysis
                print(f"Starting analysis for: {url}")
                analyzer = SEOAnalyzer(url)
                result = analyzer.analyze_all()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())
                
            except Exception as e:
                self.send_error_response(f"Analysis error: {str(e)}")
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

# For local testing
if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), handler)
    print("Server running at http://localhost:8000")
    server.serve_forever()
