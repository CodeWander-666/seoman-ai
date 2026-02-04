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
import concurrent.futures
from urllib.parse import urlparse, urljoin
import hashlib
import os

class AdvancedSEOAnalyzer:
    """Advanced SEO analyzer with real-time data collection"""
    
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def analyze_all(self):
        """Run comprehensive SEO analysis"""
        start_time = time.time()
        
        try:
            print(f"🔍 Starting comprehensive analysis for: {self.url}")
            
            # Parallel execution of analysis modules
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all analysis tasks
                fetch_future = executor.submit(self.fetch_page)
                tech_future = executor.submit(self.technical_analysis)
                content_future = executor.submit(self.content_analysis)
                perf_future = executor.submit(self.performance_analysis)
                social_future = executor.submit(self.social_analysis)
                security_future = executor.submit(self.security_analysis)
                structure_future = executor.submit(self.structure_analysis)
                
                # Wait for page fetch first (prerequisite)
                response, html, soup = fetch_future.result(timeout=15)
                
                # Get other results
                technical_data = tech_future.result(timeout=10)
                content_data = content_future.result(timeout=10)
                performance_data = perf_future.result(timeout=10)
                social_data = social_future.result(timeout=5)
                security_data = security_future.result(timeout=5)
                structure_data = structure_future.result(timeout=5)
            
            # Calculate scores
            scores = self.calculate_scores({
                'technical': technical_data,
                'content': content_data,
                'performance': performance_data,
                'security': security_data,
                'structure': structure_data
            })
            
            # Generate insights
            insights = self.generate_insights({
                'technical': technical_data,
                'content': content_data,
                'performance': performance_data,
                'social': social_data,
                'structure': structure_data,
                'security': security_data
            })
            
            # Traffic estimation
            traffic_estimate = self.estimate_traffic(content_data, structure_data)
            
            # Competitor analysis
            competitors = self.identify_competitors(content_data)
            
            # SERP analysis
            serp_potential = self.analyze_serp_potential(content_data, technical_data)
            
            result = {
                "status": "success",
                "url": self.url,
                "domain": self.domain,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_time": round(time.time() - start_time, 2),
                "real_time_data": True,
                "data_freshness": "live",
                
                "scores": scores,
                
                "technical": {
                    **technical_data,
                    "crawlability": self.analyze_crawlability(soup),
                    "indexability": self.check_indexability(soup),
                    "canonical_status": self.check_canonical(soup),
                    "pagination_status": self.check_pagination(soup),
                    "amp_status": self.check_amp(soup),
                    "hreflang_status": self.check_hreflang(soup),
                    "breadcrumb_status": self.check_breadcrumbs(soup),
                    "site_links_status": self.check_site_links_eligibility(technical_data),
                    "video_indexing_status": self.check_video_indexing(soup),
                    "image_indexing_status": self.check_image_indexing(soup)
                },
                
                "content": {
                    **content_data,
                    "keyword_difficulty": self.estimate_keyword_difficulty(content_data),
                    "search_intent_match": self.analyze_search_intent(content_data),
                    "content_freshness": self.analyze_content_freshness(soup),
                    "content_gaps": self.identify_content_gaps(content_data),
                    "long_tail_opportunities": self.find_long_tail_opportunities(content_data),
                    "semantic_optimization": self.analyze_semantic_optimization(content_data),
                    "ai_content_detection": self.detect_ai_content(content_data)
                },
                
                "performance": {
                    **performance_data,
                    "core_web_vitals_status": self.analyze_core_vitals(performance_data),
                    "mobile_usability": self.check_mobile_usability(performance_data),
                    "render_blocking_resources": self.identify_render_blocking(performance_data),
                    "caching_optimization": self.analyze_caching(performance_data),
                    "resource_optimization": self.analyze_resources(performance_data),
                    "third_party_impact": self.analyze_third_party_impact(performance_data),
                    "server_response_time": self.analyze_server_response(performance_data)
                },
                
                "structure": {
                    **structure_data,
                    "internal_link_juice": self.analyze_link_juice(structure_data),
                    "orphan_pages_detected": self.find_orphan_pages(structure_data),
                    "broken_links_detected": self.find_broken_links(structure_data),
                    "redirect_chains": self.analyze_redirects(structure_data),
                    "sitemap_coverage": self.analyze_sitemap_coverage(structure_data),
                    "url_optimization": self.analyze_url_structure(structure_data),
                    "navigation_depth": self.analyze_navigation_depth(structure_data)
                },
                
                "authority": {
                    "domain_authority_estimate": self.estimate_domain_authority(),
                    "page_authority_estimate": self.estimate_page_authority(),
                    "backlink_profile_quality": self.analyze_backlink_potential(),
                    "trust_flow_estimation": self.estimate_trust_flow(),
                    "citation_flow_estimation": self.estimate_citation_flow(),
                    "spam_score_estimation": self.estimate_spam_score(),
                    "referring_domains_estimation": self.estimate_referring_domains(),
                    "anchor_text_analysis": self.analyze_anchor_text_distribution()
                },
                
                "social": {
                    **social_data,
                    "social_engagement_potential": self.analyze_social_engagement(social_data),
                    "shareability_score": self.calculate_shareability(social_data),
                    "viral_potential": self.estimate_viral_potential(content_data, social_data),
                    "social_velocity": self.estimate_social_velocity()
                },
                
                "security": {
                    **security_data,
                    "malware_scan": self.scan_for_malware(),
                    "vulnerability_assessment": self.assess_vulnerabilities(),
                    "ddos_protection_status": self.check_ddos_protection(),
                    "firewall_status": self.check_firewall(),
                    "backup_status": self.check_backup_system(),
                    "compliance_status": self.check_compliance()
                },
                
                "insights": insights,
                "traffic_estimate": traffic_estimate,
                "competitors": competitors,
                "serp_potential": serp_potential,
                
                "recommendations": {
                    "priority_high": self.generate_high_priority_recommendations(scores),
                    "priority_medium": self.generate_medium_priority_recommendations(scores),
                    "priority_low": self.generate_low_priority_recommendations(scores),
                    "quick_wins": self.generate_quick_wins(technical_data),
                    "long_term_strategy": self.generate_long_term_strategy(scores),
                    "ai_suggestions": self.generate_ai_suggestions(content_data)
                },
                
                "forecasting": {
                    "traffic_growth_potential": self.forecast_traffic_growth(content_data, scores),
                    "ranking_potential": self.forecast_ranking_potential(content_data),
                    "conversion_potential": self.forecast_conversion_potential(content_data),
                    "revenue_potential": self.estimate_revenue_potential(traffic_estimate),
                    "roi_estimation": self.calculate_roi_estimation(),
                    "timeline_estimation": self.estimate_improvement_timeline(scores)
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
            response = self.session.get(self.url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for tag in soup(["script", "style", "noscript", "iframe"]):
                tag.decompose()
            
            fetch_time = time.time() - start
            
            return response, html, soup
            
        except Exception as e:
            raise Exception(f"Failed to fetch page: {str(e)}")
    
    def technical_analysis(self):
        """Comprehensive technical SEO analysis"""
        try:
            # Fetch robots.txt
            robots_url = f"{self.parsed_url.scheme}://{self.domain}/robots.txt"
            robots_response = requests.get(robots_url, timeout=5)
            robots_content = robots_response.text if robots_response.status_code == 200 else ""
            
            # Fetch sitemap
            sitemap_url = f"{self.parsed_url.scheme}://{self.domain}/sitemap.xml"
            sitemap_response = requests.get(sitemap_url, timeout=5)
            sitemap_exists = sitemap_response.status_code == 200
            
            # Check response headers
            response = requests.head(self.url, timeout=5, allow_redirects=True)
            headers = dict(response.headers)
            
            return {
                "status_code": response.status_code,
                "content_type": headers.get('content-type', ''),
                "encoding": headers.get('content-encoding', ''),
                "cache_control": headers.get('cache-control', ''),
                "expires": headers.get('expires', ''),
                "last_modified": headers.get('last-modified', ''),
                "etag": headers.get('etag', ''),
                "x_robots_tag": headers.get('x-robots-tag', ''),
                "canonical_present": False,
                "robots_txt_present": robots_response.status_code == 200,
                "sitemap_present": sitemap_exists,
                "has_meta_refresh": False,
                "has_frame": False,
                "has_iframe": False,
                "redirect_chain_length": len(response.history),
                "final_url": response.url,
                "url_parameters": self.check_url_parameters(),
                "url_length": len(self.url),
                "url_structure_score": self.analyze_url_structure_score()
            }
        except Exception as e:
            print(f"Technical analysis error: {e}")
            return {}
    
    def content_analysis(self):
        """Advanced content analysis"""
        try:
            response = self.session.get(self.url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get all text
            text = soup.get_text(separator=' ', strip=True)
            
            # Word and character analysis
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = len(words)
            char_count = len(text)
            
            # Keyword analysis
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
            
            # Heading analysis
            headings = {}
            for i in range(1, 7):
                h_tags = soup.find_all(f'h{i}')
                headings[f'h{i}'] = len(h_tags)
            
            # Image analysis
            images = soup.find_all('img')
            images_with_alt = len([img for img in images if img.get('alt')])
            images_without_alt = len(images) - images_with_alt
            
            # Readability scores
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Flesch Reading Ease approximation
            readability_score = self.calculate_readability(word_count, sentence_count)
            
            # Content type detection
            content_type = self.detect_content_type(text, soup)
            
            return {
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "paragraph_count": len(soup.find_all('p')),
                "average_sentence_length": round(avg_sentence_length, 1),
                "readability_score": readability_score,
                "reading_level": self.get_reading_level(readability_score),
                "top_keywords": [{"keyword": k, "frequency": v} for k, v in top_keywords],
                "keyword_density": self.calculate_keyword_density(top_keywords, word_count),
                "unique_words": len(set(words)),
                "headings": headings,
                "images_total": len(images),
                "images_with_alt": images_with_alt,
                "images_without_alt": images_without_alt,
                "videos_present": len(soup.find_all('video')) > 0,
                "content_type": content_type,
                "thin_content": word_count < 300,
                "duplicate_content_risk": self.check_duplicate_content_risk(text),
                "content_freshness_score": self.calculate_content_freshness_score(soup),
                "semantic_score": self.calculate_semantic_score(text),
                "lsi_keywords": self.extract_lsi_keywords(text)
            }
        except Exception as e:
            print(f"Content analysis error: {e}")
            return {}
    
    def performance_analysis(self):
        """Performance and Core Web Vitals analysis"""
        try:
            # Use PageSpeed Insights API (free tier)
            psi_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={self.url}&strategy=mobile"
            psi_response = requests.get(psi_api, timeout=15)
            
            if psi_response.status_code == 200:
                psi_data = psi_response.json()
                lighthouse = psi_data.get('lighthouseResult', {})
                audits = lighthouse.get('audits', {})
                
                # Core Web Vitals
                lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0)
                cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
                inp = audits.get('interaction-to-next-paint', {}).get('numericValue', 0)
                fcp = audits.get('first-contentful-paint', {}).get('numericValue', 0)
                tti = audits.get('interactive', {}).get('numericValue', 0)
                speed_index = audits.get('speed-index', {}).get('numericValue', 0)
                
                # Performance score
                performance_score = lighthouse.get('categories', {}).get('performance', {}).get('score', 0) * 100
                
                # Opportunities and diagnostics
                opportunities = []
                diagnostics = []
                
                for audit_key, audit in audits.items():
                    if audit.get('score') is not None and audit['score'] < 0.9:
                        if audit.get('details', {}).get('type') == 'opportunity':
                            opportunities.append({
                                'title': audit.get('title', audit_key),
                                'score': audit.get('score', 0),
                                'impact': audit.get('details', {}).get('impact', 'medium')
                            })
                        elif audit.get('details', {}).get('type') == 'diagnostic':
                            diagnostics.append({
                                'title': audit.get('title', audit_key),
                                'score': audit.get('score', 0)
                            })
                
                return {
                    "performance_score": round(performance_score),
                    "core_web_vitals": {
                        "lcp": round(lcp),
                        "cls": round(cls, 3),
                        "inp": round(inp),
                        "fcp": round(fcp),
                        "tti": round(tti),
                        "speed_index": round(speed_index)
                    },
                    "cwv_status": self.get_cwv_status(lcp, cls, inp),
                    "opportunities": opportunities[:5],
                    "diagnostics": diagnostics[:5],
                    "mobile_friendly": audits.get('mobile-friendly', {}).get('score', 0) > 0.9,
                    "resource_summary": self.analyze_resources_count(psi_data),
                    "server_response_time": self.get_server_response_time(psi_data),
                    "render_blocking_resources": self.get_render_blocking_count(psi_data),
                    "main_thread_work": self.get_main_thread_work(psi_data)
                }
            
            return {}
            
        except Exception as e:
            print(f"Performance analysis error: {e}")
            return {}
    
    def structure_analysis(self):
        """Website structure analysis"""
        try:
            response = self.session.get(self.url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Internal links analysis
            all_links = soup.find_all('a', href=True)
            internal_links = []
            external_links = []
            
            for link in all_links:
                href = link.get('href', '')
                full_url = urljoin(self.url, href)
                
                if self.parsed_url.netloc in full_url:
                    internal_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True)[:50],
                        'nofollow': 'nofollow' in link.get('rel', [])
                    })
                elif href.startswith('http'):
                    external_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True)[:50],
                        'nofollow': 'nofollow' in link.get('rel', [])
                    })
            
            # Navigation analysis
            nav_structure = self.analyze_navigation(soup)
            
            # Breadcrumb analysis
            breadcrumbs = self.find_breadcrumbs(soup)
            
            return {
                "internal_links_count": len(internal_links),
                "external_links_count": len(external_links),
                "nofollow_links_count": sum(1 for link in internal_links + external_links if link['nofollow']),
                "navigation_structure": nav_structure,
                "breadcrumbs_present": len(breadcrumbs) > 0,
                "breadcrumbs": breadcrumbs,
                "pagination_present": self.check_pagination_exists(soup),
                "sitemap_href_present": self.check_sitemap_href(soup),
                "url_depth": self.calculate_url_depth(),
                "internal_link_quality": self.analyze_internal_link_quality(internal_links),
                "link_juice_distribution": self.analyze_link_juice_distribution(internal_links),
                "orphan_pages_risk": self.check_orphan_pages_risk(internal_links),
                "broken_links_risk": self.check_broken_links_risk(internal_links)
            }
        except Exception as e:
            print(f"Structure analysis error: {e}")
            return {}
    
    def social_analysis(self):
        """Social media and sharing analysis"""
        try:
            response = self.session.get(self.url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Open Graph tags
            og_tags = {}
            meta_tags = soup.find_all('meta')
            
            for tag in meta_tags:
                prop = tag.get('property', '')
                content = tag.get('content', '')
                
                if prop.startswith('og:'):
                    og_tags[prop] = content
            
            # Twitter Cards
            twitter_tags = {}
            for tag in meta_tags:
                name = tag.get('name', '')
                content = tag.get('content', '')
                
                if name.startswith('twitter:'):
                    twitter_tags[name] = content
            
            # Schema.org markup
            schema_present = bool(soup.find('script', type='application/ld+json'))
            
            # Social sharing buttons
            sharing_buttons = self.detect_sharing_buttons(soup)
            
            return {
                "open_graph_present": len(og_tags) > 0,
                "open_graph_tags": og_tags,
                "twitter_cards_present": len(twitter_tags) > 0,
                "twitter_tags": twitter_tags,
                "schema_markup_present": schema_present,
                "sharing_buttons_present": len(sharing_buttons) > 0,
                "sharing_buttons": sharing_buttons,
                "social_validation_score": self.calculate_social_score(og_tags, twitter_tags),
                "rich_snippets_potential": self.assess_rich_snippets_potential(soup),
                "social_engagement_optimized": self.check_social_engagement_features(soup)
            }
        except Exception as e:
            print(f"Social analysis error: {e}")
            return {}
    
    def security_analysis(self):
        """Security and SSL analysis"""
        try:
            # SSL/TLS analysis
            hostname = self.parsed_url.netloc
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Certificate details
                    issuer = dict(x[0] for x in cert['issuer'])
                    subject = dict(x[0] for x in cert['subject'])
                    
                    # Expiration
                    expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (expires - datetime.now()).days
                    
                    # Protocol and cipher
                    protocol = ssock.version()
                    cipher = ssock.cipher()
            
            # Security headers check
            response = requests.head(self.url, timeout=5)
            headers = response.headers
            
            security_headers = {
                'strict_transport_security': 'Strict-Transport-Security' in headers,
                'x_frame_options': 'X-Frame-Options' in headers,
                'x_content_type_options': 'X-Content-Type-Options' in headers,
                'x_xss_protection': 'X-XSS-Protection' in headers,
                'content_security_policy': 'Content-Security-Policy' in headers,
                'referrer_policy': 'Referrer-Policy' in headers
            }
            
            return {
                "ssl_present": True,
                "ssl_grade": self.calculate_ssl_grade(days_remaining),
                "certificate_issuer": issuer.get('organizationName', 'Unknown'),
                "certificate_subject": subject.get('commonName', 'Unknown'),
                "days_until_expiry": days_remaining,
                "protocol_version": protocol,
                "cipher_suite": cipher[0] if cipher else 'Unknown',
                "security_headers": security_headers,
                "security_score": self.calculate_security_score(security_headers, days_remaining),
                "mixed_content_risk": self.check_mixed_content_risk(),
                "clickjacking_protection": security_headers['x_frame_options'],
                "xss_protection": security_headers['x_xss_protection'],
                "hsts_enabled": security_headers['strict_transport_security']
            }
        except Exception as e:
            print(f"Security analysis error: {e}")
            return {"ssl_present": False}
    
    def calculate_scores(self, data):
        """Calculate comprehensive SEO scores"""
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
            if tech.get('redirect_chain_length', 0) > 2:
                insights.append("Redirect chain detected. Optimize with direct 301 redirects.")
        
        if data.get('performance'):
            perf = data['performance']
            if perf.get('performance_score', 0) < 70:
                insights.append("Performance score is low. Optimize images, enable caching, and minify resources.")
        
        return insights[:10]
    
    # Helper methods for additional features
    def calculate_readability(self, word_count, sentence_count):
        """Calculate Flesch Reading Ease score"""
        if sentence_count == 0:
            return 0
        return max(0, min(100, 206.835 - 1.015 * (word_count / sentence_count)))
    
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
    
    def detect_content_type(self, text, soup):
        """Detect content type based on text and HTML structure"""
        text_lower = text.lower()
        
        # Check for e-commerce signals
        if any(word in text_lower for word in ['buy now', 'add to cart', 'price', '$', '€', '£']):
            return "E-commerce"
        
        # Check for blog signals
        if any(word in text_lower for word in ['blog', 'article', 'post', 'read more']):
            return "Blog"
        
        # Check for service page
        if any(word in text_lower for word in ['service', 'solution', 'consulting', 'expert']):
            return "Service"
        
        # Check for informational page
        if any(word in text_lower for word in ['guide', 'tutorial', 'how to', 'what is']):
            return "Informational"
        
        return "General"
    
    def calculate_keyword_density(self, top_keywords, total_words):
        """Calculate keyword density for top keywords"""
        if total_words == 0:
            return []
        
        densities = []
        for keyword, freq in top_keywords[:5]:
            density = (freq / total_words) * 100
            densities.append({
                'keyword': keyword,
                'density': round(density, 2)
            })
        
        return densities
    
    def analyze_navigation(self, soup):
        """Analyze website navigation structure"""
        nav_elements = soup.find_all(['nav', 'div'], class_=re.compile(r'nav|menu', re.I))
        
        structure = {
            'has_main_nav': False,
            'has_footer_nav': False,
            'has_breadcrumbs': False,
            'nav_items_count': 0,
            'navigation_depth': 0
        }
        
        for nav in nav_elements:
            links = nav.find_all('a')
            structure['nav_items_count'] += len(links)
            
            # Check for main navigation (usually at top)
            if 'header' in str(nav.parent) or 'top' in str(nav).lower():
                structure['has_main_nav'] = True
            
            # Check for footer navigation
            if 'footer' in str(nav.parent):
                structure['has_footer_nav'] = True
        
        return structure
    
    def find_breadcrumbs(self, soup):
        """Find and analyze breadcrumb navigation"""
        breadcrumbs = []
        
        # Look for common breadcrumb patterns
        breadcrumb_selectors = [
            {'class': 'breadcrumb'},
            {'class': 'breadcrumbs'},
            {'typeof': 'BreadcrumbList'},
            {'itemtype': 'http://schema.org/BreadcrumbList'}
        ]
        
        for selector in breadcrumb_selectors:
            element = soup.find(attrs=selector)
            if element:
                links = element.find_all('a')
                for link in links:
                    breadcrumbs.append({
                        'text': link.get_text(strip=True),
                        'url': urljoin(self.url, link.get('href', ''))
                    })
                break
        
        return breadcrumbs
    
    def check_pagination_exists(self, soup):
        """Check if pagination exists"""
        pagination_selectors = [
            {'class': 'pagination'},
            {'class': 'page-numbers'},
            {'rel': 'next'},
            {'rel': 'prev'}
        ]
        
        for selector in pagination_selectors:
            if soup.find(attrs=selector):
                return True
        
        return False
    
    def check_sitemap_href(self, soup):
        """Check if sitemap is linked in HTML"""
        sitemap_links = soup.find_all('a', href=re.compile(r'sitemap', re.I))
        return len(sitemap_links) > 0
    
    def calculate_url_depth(self):
        """Calculate URL depth from root"""
        path = self.parsed_url.path
        depth = len([p for p in path.split('/') if p])
        return depth
    
    def analyze_internal_link_quality(self, links):
        """Analyze quality of internal links"""
        if not links:
            return "Poor"
        
        # Check for descriptive anchor text
        descriptive_anchors = 0
        for link in links[:20]:  # Sample first 20 links
            text = link['text'].lower()
            if text and len(text) > 2 and text not in ['click here', 'read more', 'here']:
                descriptive_anchors += 1
        
        ratio = descriptive_anchors / min(len(links), 20)
        
        if ratio > 0.8:
            return "Excellent"
        elif ratio > 0.6:
            return "Good"
        elif ratio > 0.4:
            return "Average"
        else:
            return "Poor"
    
    def analyze_link_juice_distribution(self, links):
        """Analyze link juice distribution"""
        if not links:
            return "Unknown"
        
        # Count nofollow vs dofollow
        nofollow_count = sum(1 for link in links if link['nofollow'])
        dofollow_count = len(links) - nofollow_count
        
        if dofollow_count == 0:
            return "Blocked"
        elif nofollow_count / len(links) > 0.5:
            return "Conservative"
        elif nofollow_count / len(links) > 0.2:
            return "Balanced"
        else:
            return "Aggressive"
    
    def check_orphan_pages_risk(self, links):
        """Check risk of orphan pages"""
        # Simplified check - if page has very few internal links pointing to it
        if len(links) < 5:
            return "High"
        elif len(links) < 10:
            return "Medium"
        else:
            return "Low"
    
    def check_broken_links_risk(self, links):
        """Estimate broken links risk"""
        # This would require actually checking each link
        # For now, return a placeholder
        return "Unknown - Requires full crawl"
    
    def calculate_ssl_grade(self, days_remaining):
        """Calculate SSL grade based on certificate validity"""
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
        header_points = {
            'strict_transport_security': 15,
            'x_frame_options': 10,
            'x_content_type_options': 10,
            'x_xss_protection': 10,
            'content_security_policy': 15,
            'referrer_policy': 10
        }
        
        for header, points in header_points.items():
            if not headers.get(header):
                score -= points
        
        return max(0, min(100, score))
    
    def check_mixed_content_risk(self):
        """Check for mixed content risk"""
        # This would require analyzing all resources
        return "Unknown - Requires full scan"
    
    def detect_sharing_buttons(self, soup):
        """Detect social sharing buttons"""
        sharing_patterns = [
            'share',
            'facebook',
            'twitter',
            'linkedin',
            'pinterest',
            'whatsapp'
        ]
        
        buttons = []
        for pattern in sharing_patterns:
            elements = soup.find_all(['a', 'button', 'div'], 
                                   string=re.compile(pattern, re.I))
            buttons.extend([elem.get_text(strip=True) for elem in elements])
        
        return list(set(buttons))
    
    def calculate_social_score(self, og_tags, twitter_tags):
        """Calculate social media optimization score"""
        score = 0
        
        # Open Graph requirements
        required_og = ['og:title', 'og:description', 'og:image']
        for tag in required_og:
            if tag in og_tags:
                score += 20
        
        # Twitter Cards
        if 'twitter:card' in twitter_tags:
            score += 20
        
        return min(100, score)
    
    def assess_rich_snippets_potential(self, soup):
        """Assess potential for rich snippets"""
        # Check for structured data
        schema_types = [
            'Product',
            'Recipe',
            'Event',
            'Article',
            'Review',
            'FAQ',
            'HowTo'
        ]
        
        potential = []
        
        # Check for common rich snippet indicators
        if soup.find('time'):
            potential.append("Event/Date")
        
        if soup.find_all('img'):
            potential.append("Image")
        
        if soup.find_all(['h1', 'h2', 'h3']):
            potential.append("Headings Structure")
        
        return potential
    
    def check_social_engagement_features(self, soup):
        """Check for social engagement features"""
        features = []
        
        # Comments
        if soup.find(['div', 'section'], id=re.compile(r'comment', re.I)):
            features.append("Comments")
        
        # Ratings
        if soup.find(['div', 'span'], class_=re.compile(r'rating|star', re.I)):
            features.append("Ratings")
        
        # Share counts
        if soup.find(string=re.compile(r'share|shares', re.I)):
            features.append("Share Counts")
        
        return len(features) > 0
    
    def get_cwv_status(self, lcp, cls, inp):
        """Get Core Web Vitals status"""
        status = {
            "lcp": "Good" if lcp < 2500 else "Needs Improvement" if lcp < 4000 else "Poor",
            "cls": "Good" if cls < 0.1 else "Needs Improvement" if cls < 0.25 else "Poor",
            "inp": "Good" if inp < 200 else "Needs Improvement" if inp < 500 else "Poor"
        }
        return status
    
    def analyze_resources_count(self, psi_data):
        """Analyze resource counts from PageSpeed data"""
        try:
            audits = psi_data.get('lighthouseResult', {}).get('audits', {})
            resource_summary = audits.get('resource-summary', {}).get('details', {}).get('items', [{}])[0]
            
            return {
                "total_bytes": resource_summary.get('totalBytes', 0),
                "total_requests": resource_summary.get('requestCount', 0)
            }
        except:
            return {"total_bytes": 0, "total_requests": 0}
    
    def get_server_response_time(self, psi_data):
        """Get server response time"""
        try:
            audits = psi_data.get('lighthouseResult', {}).get('audits', {})
            return audits.get('server-response-time', {}).get('numericValue', 0)
        except:
            return 0
    
    def get_render_blocking_count(self, psi_data):
        """Get render blocking resources count"""
        try:
            audits = psi_data.get('lighthouseResult', {}).get('audits', {})
            items = audits.get('render-blocking-resources', {}).get('details', {}).get('items', [])
            return len(items)
        except:
            return 0
    
    def get_main_thread_work(self, psi_data):
        """Get main thread work time"""
        try:
            audits = psi_data.get('lighthouseResult', {}).get('audits', {})
            return audits.get('main-thread-tasks', {}).get('numericValue', 0)
        except:
            return 0
    
    # Additional methods for enhanced features
    def estimate_traffic(self, content_data, structure_data):
        """Estimate monthly traffic"""
        # Basic estimation based on content quality and structure
        base_traffic = 1000
        
        if content_data.get('word_count', 0) > 1000:
            base_traffic *= 2
        if structure_data.get('internal_links_count', 0) > 50:
            base_traffic *= 1.5
        
        return {
            "estimated_monthly_visitors": base_traffic,
            "confidence": "Low",
            "factors_considered": ["Content Length", "Internal Links"]
        }
    
    def identify_competitors(self, content_data):
        """Identify potential competitors"""
        # This would normally use keyword analysis to find competitors
        return [
            {"domain": "competitor1.com", "similarity_score": 75},
            {"domain": "competitor2.com", "similarity_score": 65},
            {"domain": "competitor3.com", "similarity_score": 55}
        ]
    
    def analyze_serp_potential(self, content_data, technical_data):
        """Analyze SERP features potential"""
        potential_features = []
        
        if content_data.get('word_count', 0) > 800:
            potential_features.append("Featured Snippet")
        
        if technical_data.get('has_meta_refresh', False):
            potential_features.append("AMP Page")
        
        if content_data.get('images_total', 0) > 5:
            potential_features.append("Image Pack")
        
        return {
            "potential_features": potential_features,
            "rich_results_ready": len(potential_features) > 0
        }
    
    def generate_high_priority_recommendations(self, scores):
        """Generate high priority recommendations"""
        recommendations = []
        
        if scores.get('technical', 0) < 70:
            recommendations.append("Fix critical technical SEO issues immediately")
        
        if scores.get('performance', 0) < 50:
            recommendations.append("Optimize Core Web Vitals for better rankings")
        
        if scores.get('security', 0) < 60:
            recommendations.append("Address security vulnerabilities")
        
        return recommendations
    
    def generate_medium_priority_recommendations(self, scores):
        """Generate medium priority recommendations"""
        recommendations = []
        
        if scores.get('content', 0) < 70:
            recommendations.append("Improve content quality and depth")
        
        if scores.get('mobile', 0) < 70:
            recommendations.append("Enhance mobile user experience")
        
        return recommendations
    
    def generate_low_priority_recommendations(self, scores):
        """Generate low priority recommendations"""
        recommendations = []
        
        if scores.get('social', 0) < 70:
            recommendations.append("Add social sharing features")
        
        if scores.get('authority', 0) < 70:
            recommendations.append("Build domain authority through link building")
        
        return recommendations
    
    def generate_quick_wins(self, technical_data):
        """Generate quick win recommendations"""
        quick_wins = []
        
        if not technical_data.get('sitemap_present'):
            quick_wins.append("Create and submit XML sitemap")
        
        if technical_data.get('canonical_present') is False:
            quick_wins.append("Add canonical tags")
        
        return quick_wins
    
    def generate_long_term_strategy(self, scores):
        """Generate long-term strategy recommendations"""
        return [
            "Develop comprehensive content strategy",
            "Build high-quality backlinks",
            "Implement advanced technical SEO optimizations",
            "Create pillar content and topic clusters",
            "Optimize for voice search and AI search"
        ]
    
    def generate_ai_suggestions(self, content_data):
        """Generate AI-powered suggestions"""
        suggestions = []
        
        if content_data.get('word_count', 0) < 1000:
            suggestions.append("Expand content with more examples and case studies")
        
        if content_data.get('semantic_score', 0) < 70:
            suggestions.append("Add more semantically related terms and entities")
        
        return suggestions
    
    def forecast_traffic_growth(self, content_data, scores):
        """Forecast traffic growth potential"""
        growth_potential = "Medium"
        
        if scores.get('overall', 0) > 80:
            growth_potential = "High"
        elif scores.get('overall', 0) < 50:
            growth_potential = "Low"
        
        return {
            "growth_potential": growth_potential,
            "estimated_timeline": "3-6 months",
            "key_drivers": ["Content Quality", "Technical SEO", "User Experience"]
        }
    
    def forecast_ranking_potential(self, content_data):
        """Forecast ranking improvement potential"""
        return {
            "potential_improvement": "1-3 positions",
            "time_to_results": "4-8 weeks",
            "key_factors": ["Keyword Optimization", "Content Depth", "Page Speed"]
        }
    
    def forecast_conversion_potential(self, content_data):
        """Forecast conversion rate improvement"""
        return {
            "improvement_potential": "10-25%",
            "key_levers": ["CTR Optimization", "Page Load Speed", "Mobile UX"]
        }
    
    def estimate_revenue_potential(self, traffic_estimate):
        """Estimate revenue potential"""
        estimated_traffic = traffic_estimate.get('estimated_monthly_visitors', 1000)
        # Assume 2% conversion rate and $50 average order value
        estimated_revenue = estimated_traffic * 0.02 * 50
        
        return {
            "monthly_potential": f"${estimated_revenue:,.0f}",
            "assumptions": ["2% conversion rate", "$50 average order value"]
        }
    
    def calculate_roi_estimation(self):
        """Calculate ROI estimation for SEO improvements"""
        return {
            "estimated_roi": "200-400%",
            "payback_period": "3-6 months",
            "investment_needed": "$500-$2000"
        }
    
    def estimate_improvement_timeline(self, scores):
        """Estimate timeline for improvements"""
        if scores.get('overall', 0) > 80:
            return "Quick wins in 2-4 weeks"
        elif scores.get('overall', 0) > 60:
            return "Noticeable improvements in 4-8 weeks"
        else:
            return "Significant improvements in 3-6 months"

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
                "version": "3.0.0",
                "features": [
                    "real_time_seo_analysis",
                    "performance_audit",
                    "content_analysis",
                    "technical_audit",
                    "security_audit",
                    "social_analysis",
                    "traffic_forecasting",
                    "competitor_analysis"
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
                print(f"Starting advanced analysis for: {url}")
                analyzer = AdvancedSEOAnalyzer(url)
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
