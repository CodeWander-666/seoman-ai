from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

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
                "message": "SEO Vision Pro API is running"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>SEO Vision Pro API</h1><p>Use POST /api/audit with JSON body</p>")
            
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
                result = self.perform_audit(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            elif self.path == '/api/ai-analysis':
                result = self.perform_ai_analysis(data)
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
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }).encode())
    
    def perform_audit(self, data):
        """Perform SEO audit without external dependencies"""
        url = data.get('url', '').strip()
        
        if not url:
            return {"error": "URL is required"}
        
        if not url.startswith('http'):
            return {"error": "URL must start with http:// or https://"}
        
        try:
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metrics
            text = soup.get_text()
            words = re.findall(r'\w+', text.lower())
            word_count = len(words)
            
            # Get title
            title = soup.title.string if soup.title else "No title"
            title_length = len(title)
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            desc_length = len(description)
            
            # Count headings
            h1_count = len(soup.find_all('h1'))
            h2_count = len(soup.find_all('h2'))
            h3_count = len(soup.find_all('h3'))
            
            # Count images with alt text
            images = soup.find_all('img')
            images_with_alt = len([img for img in images if img.get('alt', '')])
            
            # Count links
            links = soup.find_all('a')
            internal_links = 0
            external_links = 0
            
            for link in links:
                href = link.get('href', '')
                if href:
                    if href.startswith('/') or url in href:
                        internal_links += 1
                    else:
                        external_links += 1
            
            # Check for common issues
            issues = []
            if h1_count == 0:
                issues.append("No H1 heading found")
            elif h1_count > 1:
                issues.append(f"Multiple H1 headings ({h1_count}) found")
            
            if title_length == 0:
                issues.append("No title tag found")
            elif title_length > 60:
                issues.append(f"Title too long ({title_length} characters)")
            
            if desc_length == 0:
                issues.append("No meta description found")
            elif desc_length > 160:
                issues.append(f"Meta description too long ({desc_length} characters)")
            
            if word_count < 300:
                issues.append(f"Low word count ({word_count}) - aim for 300+ words")
            
            if images_with_alt < len(images):
                issues.append(f"{len(images) - images_with_alt} images missing alt text")
            
            # Calculate scores
            technical_score = 85
            content_score = min(100, word_count / 15)
            authority_score = 65  # Placeholder
            
            # Adjust scores based on issues
            technical_score -= len(issues) * 5
            technical_score = max(0, min(100, technical_score))
            
            if word_count > 800:
                content_score = min(100, content_score + 10)
            
            if images_with_alt == len(images) and len(images) > 0:
                technical_score += 5
            
            overall_score = round((technical_score + content_score + authority_score) / 3)
            
            # Generate recommendations
            recommendations = [
                "Ensure all images have descriptive alt text",
                "Use only one H1 tag per page",
                "Optimize title tag (50-60 characters)",
                "Write compelling meta description (120-160 characters)",
                "Aim for at least 300 words of quality content",
                "Use internal links to establish site hierarchy"
            ]
            
            if word_count < 300:
                recommendations.append("Expand content to cover topic more thoroughly")
            
            if h1_count != 1:
                recommendations.append("Ensure exactly one H1 tag with main keyword")
            
            # Return result
            result = {
                "status": "success",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "response_code": response.status_code,
                "scores": {
                    "technical": round(technical_score),
                    "content": round(content_score),
                    "authority": round(authority_score),
                    "overall": overall_score
                },
                "metrics": {
                    "word_count": word_count,
                    "title": title[:100] + "..." if len(title) > 100 else title,
                    "title_length": title_length,
                    "meta_description": description[:150] + "..." if len(description) > 150 else description,
                    "meta_description_length": desc_length,
                    "h1_count": h1_count,
                    "h2_count": h2_count,
                    "h3_count": h3_count,
                    "images_total": len(images),
                    "images_with_alt": images_with_alt,
                    "internal_links": internal_links,
                    "external_links": external_links,
                    "page_size_kb": round(len(response.content) / 1024, 2)
                },
                "issues": issues,
                "recommendations": recommendations[:5],  # Top 5 recommendations
                "plan": data.get("plan", "free")
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "error": "Failed to fetch URL",
                "message": str(e),
                "code": "FETCH_ERROR"
            }
        except Exception as e:
            return {
                "error": "Analysis failed",
                "message": str(e),
                "code": "ANALYSIS_ERROR"
            }
    
    def perform_ai_analysis(self, data):
        """Simple AI analysis without external API"""
        metrics = data.get('metrics', {})
        
        # Generate AI-like recommendations based on metrics
        issues = []
        
        if metrics.get('word_count', 0) < 300:
            issues.append("Content is too thin. Expand with more detailed information.")
        
        if metrics.get('h1_count', 0) != 1:
            issues.append(f"Found {metrics.get('h1_count', 0)} H1 tags. Should have exactly 1.")
        
        if metrics.get('images_with_alt', 0) < metrics.get('images_total', 0):
            issues.append(f"{metrics.get('images_total', 0) - metrics.get('images_with_alt', 0)} images missing alt text.")
        
        technical_fixes = [
            "Optimize images for faster loading",
            "Minify CSS and JavaScript files",
            "Enable browser caching"
        ]
        
        content_opportunities = [
            "Add more internal links to related content",
            "Include schema markup for better rich results",
            "Create a table of contents for long articles"
        ]
        
        quick_wins = [
            "Fix missing alt text on images",
            "Optimize title and meta description",
            "Check for broken links"
        ]
        
        return {
            "technical_fixes": technical_fixes,
            "content_opportunities": content_opportunities,
            "quick_wins": quick_wins,
            "issues": issues,
            "ai_generated": True,
            "note": "AI analysis based on SEO best practices"
        }
