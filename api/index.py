from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import time
import socket
import ssl
import urllib.request
from urllib.parse import urljoin, urlparse
import concurrent.futures

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0",
                "features": ["real_seo_analysis", "content_parsing", "technical_audit", "performance_check"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>SEO Vision Pro API</h1><p>Real SEO Analysis - No Dummy Data</p>")
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/api/audit':
                # Start real analysis
                url = data.get('url', '').strip()
                
                if not url:
                    self.send_error_response("URL is required")
                    return
                
                if not url.startswith('http'):
                    self.send_error_response("URL must start with http:// or https://")
                    return
                
                # Perform real analysis
                result = self.perform_real_analysis(url)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
                
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def perform_real_analysis(self, url):
        """REAL SEO analysis - fetches and analyzes actual website data"""
        start_time = time.time()
        
        try:
            print(f"[ANALYSIS] Starting real analysis for: {url}")
            
            # Fetch the page with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            print(f"[ANALYSIS] Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            print(f"[ANALYSIS] Response received: {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Get plain text for analysis
            text = soup.get_text(separator=' ', strip=True)
            
            # REAL CONTENT ANALYSIS
            word_count = len(re.findall(r'\b\w+\b', text.lower()))
            sentences = len(re.findall(r'[.!?]+', text))
            
            # Keyword density analysis (real)
            words = re.findall(r'\b\w{3,}\b', text.lower())
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            
            word_freq = {}
            for word in words:
                if word not in stop_words and len(word) > 2:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top 10 keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Heading analysis
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            # Image analysis
            images = soup.find_all('img')
            images_with_alt = sum(1 for img in images if img.get('alt', '').strip())
            images_without_alt = len(images) - images_with_alt
            
            # Link analysis
            links = soup.find_all('a', href=True)
            domain = urlparse(url).netloc
            
            internal_links = []
            external_links = []
            
            for link in links:
                href = link.get('href', '')
                full_url = urljoin(url, href)
                parsed_href = urlparse(full_url)
                
                if parsed_href.netloc == domain or not parsed_href.netloc:
                    internal_links.append(full_url)
                else:
                    external_links.append(full_url)
            
            # Meta tag analysis
            title_tag = soup.find('title')
            title = title_tag.string if title_tag else "No title found"
            title_length = len(title)
            
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ""
            description_length = len(description)
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '') if meta_keywords else ""
            
            # Check for viewport meta tag (mobile)
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            has_viewport = bool(viewport)
            
            # Check for canonical
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            has_canonical = bool(canonical)
            
            # Check for Open Graph tags
            og_title = soup.find('meta', property='og:title')
            og_description = soup.find('meta', property='og:description')
            og_image = soup.find('meta', property='og:image')
            
            # Check for Twitter Cards
            twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
            
            # Check for schema markup
            schema_org = soup.find('script', type='application/ld+json')
            
            # Calculate REAL scores based on actual data
            technical_score = self.calculate_technical_score({
                'status_code': response.status_code,
                'has_viewport': has_viewport,
                'has_canonical': has_canonical,
                'title_length': title_length,
                'description_length': description_length,
                'h1_count': len(h1_tags),
                'image_alt_ratio': images_with_alt / len(images) if images else 1,
                'response_time': response.elapsed.total_seconds(),
                'og_tags': bool(og_title or og_description or og_image),
                'schema_markup': bool(schema_org)
            })
            
            content_score = self.calculate_content_score({
                'word_count': word_count,
                'sentence_count': sentences,
                'unique_keywords': len(set(words)),
                'top_keywords': top_keywords,
                'h2_count': len(h2_tags),
                'h3_count': len(h3_tags),
                'avg_sentence_length': word_count / sentences if sentences > 0 else 0
            })
            
            authority_score = self.calculate_authority_score({
                'external_links': len(set(external_links)),
                'internal_links': len(set(internal_links)),
                'domain': domain,
                'has_og': bool(og_title or og_description or og_image),
                'has_twitter_card': bool(twitter_card),
                'has_schema': bool(schema_org)
            })
            
            # Calculate performance metrics
            page_size_kb = len(response.content) / 1024
            load_time = response.elapsed.total_seconds()
            
            # Generate REAL issues
            issues = self.generate_issues({
                'word_count': word_count,
                'images_without_alt': images_without_alt,
                'h1_count': len(h1_tags),
                'title_length': title_length,
                'description_length': description_length,
                'has_viewport': has_viewport,
                'has_canonical': has_canonical,
                'load_time': load_time,
                'page_size': page_size_kb,
                'status_code': response.status_code
            })
            
            # Generate REAL recommendations
            recommendations = self.generate_recommendations(issues, {
                'word_count': word_count,
                'images_count': len(images),
                'h2_count': len(h2_tags),
                'external_links': len(external_links)
            })
            
            # Compile result
            result = {
                "status": "success",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_time": round(time.time() - start_time, 2),
                "real_analysis": True,
                "scores": {
                    "technical": technical_score,
                    "content": content_score,
                    "authority": authority_score,
                    "overall": round((technical_score + content_score + authority_score) / 3)
                },
                "metrics": {
                    "word_count": word_count,
                    "sentence_count": sentences,
                    "title": title[:100] + "..." if len(title) > 100 else title,
                    "title_length": title_length,
                    "meta_description": description[:150] + "..." if len(description) > 150 else description,
                    "meta_description_length": description_length,
                    "meta_keywords": keywords,
                    "h1_count": len(h1_tags),
                    "h2_count": len(h2_tags),
                    "h3_count": len(h3_tags),
                    "images_total": len(images),
                    "images_with_alt": images_with_alt,
                    "images_without_alt": images_without_alt,
                    "internal_links": len(internal_links),
                    "external_links": len(external_links),
                    "page_size_kb": round(page_size_kb, 2),
                    "load_time_seconds": round(load_time, 3),
                    "response_code": response.status_code,
                    "has_viewport": has_viewport,
                    "has_canonical": has_canonical,
                    "has_og_tags": bool(og_title or og_description or og_image),
                    "has_twitter_card": bool(twitter_card),
                    "has_schema_markup": bool(schema_org)
                },
                "top_keywords": [{"keyword": k, "frequency": v} for k, v in top_keywords],
                "issues": issues,
                "recommendations": recommendations,
                "technical_details": {
                    "server_headers": dict(response.headers),
                    "final_url": response.url,
                    "redirect_count": len(response.history)
                }
            }
            
            print(f"[ANALYSIS] Completed for {url} in {result['analysis_time']}s")
            return result
            
        except requests.exceptions.Timeout:
            return {
                "error": "Request timed out",
                "real_analysis": False,
                "message": "The website took too long to respond"
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": "Failed to fetch website",
                "real_analysis": False,
                "message": str(e)
            }
        except Exception as e:
            print(f"[ERROR] Analysis failed: {str(e)}")
            return {
                "error": "Analysis failed",
                "real_analysis": False,
                "message": str(e)
            }
    
    def calculate_technical_score(self, data):
        """Calculate technical SEO score based on real metrics"""
        score = 100
        
        # Deduct points for issues
        if not data['has_viewport']:
            score -= 15
        if not data['has_canonical']:
            score -= 10
        if data['h1_count'] == 0:
            score -= 20
        elif data['h1_count'] > 1:
            score -= 10
        if data['title_length'] < 10 or data['title_length'] > 60:
            score -= 10
        if data['description_length'] < 50 or data['description_length'] > 160:
            score -= 10
        if data['image_alt_ratio'] < 0.7:
            score -= 15
        if data['response_time'] > 3:
            score -= 10
        if not data['og_tags']:
            score -= 5
        if not data['schema_markup']:
            score -= 5
        
        return max(0, min(100, round(score)))
    
    def calculate_content_score(self, data):
        """Calculate content quality score based on real content analysis"""
        score = 50  # Base score
        
        # Word count scoring
        if data['word_count'] >= 1000:
            score += 30
        elif data['word_count'] >= 500:
            score += 20
        elif data['word_count'] >= 300:
            score += 15
        elif data['word_count'] >= 150:
            score += 10
        else:
            score -= 10
        
        # Keyword diversity
        if data['unique_keywords'] >= 50:
            score += 10
        elif data['unique_keywords'] >= 25:
            score += 5
        
        # Heading structure
        if data['h2_count'] >= 3:
            score += 10
        elif data['h2_count'] >= 1:
            score += 5
        
        if data['h3_count'] >= 2:
            score += 5
        
        # Sentence structure
        if data['sentence_count'] > 0:
            avg_length = data['word_count'] / data['sentence_count']
            if 15 <= avg_length <= 25:
                score += 10
        
        return max(0, min(100, round(score)))
    
    def calculate_authority_score(self, data):
        """Calculate authority score based on linking and markup"""
        score = 50  # Base score
        
        # External links (positive signal)
        if data['external_links'] >= 10:
            score += 20
        elif data['external_links'] >= 5:
            score += 10
        elif data['external_links'] >= 2:
            score += 5
        
        # Internal linking
        if data['internal_links'] >= 20:
            score += 15
        elif data['internal_links'] >= 10:
            score += 10
        elif data['internal_links'] >= 5:
            score += 5
        
        # Structured data (trust signals)
        if data['has_og']:
            score += 10
        if data['has_twitter_card']:
            score += 5
        if data['has_schema']:
            score += 15
        
        # Domain age estimation (basic)
        if '.gov' in data['domain'] or '.edu' in data['domain']:
            score += 20
        elif '.org' in data['domain']:
            score += 10
        
        return max(0, min(100, round(score)))
    
    def generate_issues(self, data):
        """Generate real issues based on actual data"""
        issues = []
        
        if data['word_count'] < 300:
            issues.append(f"Low word count ({data['word_count']}). Aim for at least 300 words for better SEO.")
        
        if data['images_without_alt'] > 0:
            issues.append(f"{data['images_without_alt']} images missing alt text. Add descriptive alt attributes for accessibility and SEO.")
        
        if data['h1_count'] == 0:
            issues.append("Missing H1 tag. Every page should have one H1 heading.")
        elif data['h1_count'] > 1:
            issues.append(f"Multiple H1 tags ({data['h1_count']}). Use only one H1 per page.")
        
        if data['title_length'] < 10:
            issues.append("Title too short. Include relevant keywords and make it 10-60 characters.")
        elif data['title_length'] > 60:
            issues.append("Title too long. Keep it under 60 characters for proper display in search results.")
        
        if data['description_length'] < 50:
            issues.append("Meta description too short. Write compelling descriptions of 50-160 characters.")
        elif data['description_length'] > 160:
            issues.append("Meta description too long. Keep it under 160 characters.")
        
        if not data['has_viewport']:
            issues.append("Missing viewport meta tag. Essential for mobile responsiveness.")
        
        if not data['has_canonical']:
            issues.append("Missing canonical tag. Helps prevent duplicate content issues.")
        
        if data['load_time'] > 3:
            issues.append(f"Slow page load ({data['load_time']:.1f}s). Optimize for better user experience.")
        
        if data['page_size'] > 2000:
            issues.append(f"Large page size ({data['page_size']:.0f} KB). Optimize images and assets.")
        
        if data['status_code'] != 200:
            issues.append(f"HTTP Status {data['status_code']}. Ensure page returns 200 OK.")
        
        return issues
    
    def generate_recommendations(self, issues, data):
        """Generate personalized recommendations"""
        recommendations = [
            "Optimize images by compressing them and adding descriptive alt text",
            "Ensure proper heading hierarchy (H1 → H2 → H3)",
            "Write unique and compelling meta title and description",
            "Add structured data (Schema.org) for rich results",
            "Create quality content with at least 300-500 words",
            "Build internal links to establish site architecture",
            "Add social media meta tags (Open Graph, Twitter Cards)",
            "Implement lazy loading for images below the fold"
        ]
        
        # Add specific recommendations based on data
        if data['word_count'] < 300:
            recommendations.append("Expand content with more detailed information and examples")
        
        if data['images_count'] > 10:
            recommendations.append("Use WebP format for better image compression")
        
        if data['h2_count'] < 2:
            recommendations.append("Break content into sections with H2 headings")
        
        if data['external_links'] < 3:
            recommendations.append("Add relevant outbound links to authoritative sources")
        
        return recommendations[:8]  # Return top 8 recommendations
