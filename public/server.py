from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/audit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            result = self.perform_audit(data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def perform_audit(self, data):
        url = data.get('url', '')
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple analysis
            text = soup.get_text()
            word_count = len(re.findall(r'\w+', text))
            
            issues = []
            if word_count < 300:
                issues.append(f"Low word count ({word_count})")
            
            h1_count = len(soup.find_all('h1'))
            if h1_count != 1:
                issues.append(f"Found {h1_count} H1 tags (should be 1)")
            
            return {
                "status": "success",
                "url": url,
                "scores": {
                    "technical": 85,
                    "content": min(100, word_count / 5),
                    "authority": 65,
                    "overall": 75
                },
                "metrics": {
                    "word_count": word_count,
                    "title": soup.title.string[:50] if soup.title else "No title",
                    "h1_count": h1_count,
                    "images_total": len(soup.find_all('img')),
                    "images_with_alt": len([img for img in soup.find_all('img') if img.get('alt')]),
                    "internal_links": 0,
                    "external_links": 0
                },
                "issues": issues,
                "recommendations": [
                    "Add meta description if missing",
                    "Ensure all images have alt text",
                    "Use only one H1 tag per page"
                ]
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), CORSRequestHandler)
    print("Server running at http://localhost:8000")
    print("Open http://localhost:8000 in browser")
    server.serve_forever()
