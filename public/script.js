class SEOVisionPro {
    constructor() {
        this.currentAudit = null;
        this.aiStream = null;
        this.aiStreamComplete = false;
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        console.log('SEO Vision Pro Initialized');
        this.bindEvents();
        this.checkHealth();
        this.setupURLValidation();
    }

    bindEvents() {
        // Button click events
        document.getElementById('auditButton').addEventListener('click', () => this.startAudit());
        document.getElementById('newAudit').addEventListener('click', () => this.resetAudit());
        document.getElementById('exportPDF').addEventListener('click', () => this.exportPDF());
        document.getElementById('shareReport').addEventListener('click', () => this.shareReport());
        document.getElementById('runBenchmark').addEventListener('click', () => this.runBenchmark());
        
        // Enter key on input
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startAudit();
        });
        
        // Input validation
        document.getElementById('urlInput').addEventListener('input', (e) => {
            this.validateInput(e.target);
        });
    }

    setupURLValidation() {
        const urlInput = document.getElementById('urlInput');
        const inputGroup = urlInput.closest('.input-group');
        
        urlInput.addEventListener('focus', () => {
            inputGroup.classList.add('focused');
        });
        
        urlInput.addEventListener('blur', () => {
            inputGroup.classList.remove('focused');
        });
    }

    validateInput(input) {
        const value = input.value.trim();
        const btn = document.getElementById('auditButton');
        
        if (this.isValidURL(value)) {
            input.classList.remove('error');
            input.classList.add('valid');
            btn.disabled = false;
            btn.style.opacity = '1';
        } else if (value.length > 0) {
            input.classList.add('error');
            input.classList.remove('valid');
            btn.disabled = true;
            btn.style.opacity = '0.6';
        } else {
            input.classList.remove('error', 'valid');
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    }

    isValidURL(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (!response.ok) throw new Error('Health check failed');
            const data = await response.json();
            console.log('System Status:', data);
            this.updateSystemStatus(data);
        } catch (error) {
            console.warn('Health check failed:', error);
            this.showNotification('System is initializing...', 'warning');
        }
    }

    updateSystemStatus(data) {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        
        if (data.status === 'operational') {
            statusIndicator.innerHTML = `<i class="fas fa-circle" style="color: #00ff9d"></i> System Online`;
        } else {
            statusIndicator.innerHTML = `<i class="fas fa-circle" style="color: #ff4444"></i> System Degraded`;
        }
        
        // Add to header
        document.querySelector('.header-stats').appendChild(statusIndicator);
    }

    async startAudit() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();
        
        // Validate URL
        if (!this.isValidURL(url)) {
            this.showNotification('Please enter a valid URL starting with http:// or https://', 'error');
            urlInput.classList.add('shake');
            setTimeout(() => urlInput.classList.remove('shake'), 500);
            return;
        }
        
        // Show loading state
        this.showLoading();
        
        // Hide dashboard if visible
        document.getElementById('dashboard').style.display = 'none';
        
        try {
            console.log('Starting audit for:', url);
            
            // Start audit
            const response = await fetch(`${this.baseURL}/api/audit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    plan: 'free'
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Audit failed');
            }
            
            const data = await response.json();
            console.log('Audit completed:', data);
            
            this.currentAudit = data;
            this.displayResults(data);
            
            // Start AI stream
            if (data.technical && data.content && data.authority) {
                this.startAIStream(data);
            }
            
        } catch (error) {
            console.error('Audit error:', error);
            this.showNotification(`Audit failed: ${error.message}`, 'error');
            this.hideLoading();
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        // Disable button
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SCANNING...';
        
        // Show loading
        loading.style.display = 'block';
        
        // Animate progress
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const progressPercent = document.getElementById('progressPercent');
        const stages = document.querySelectorAll('.stage');
        
        let progress = 0;
        const stagesText = [
            'Crawling target website...',
            'Analyzing technical metrics...',
            'Processing content data...',
            'Running AI analysis...',
            'Generating report...'
        ];
        
        const interval = setInterval(() => {
            if (progress >= 100) {
                clearInterval(interval);
                return;
            }
            
            // Increment progress
            progress += Math.random() * 4 + 1;
            if (progress > 100) progress = 100;
            
            // Update progress bar
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${Math.floor(progress)}%`;
            
            // Update stage
            const stageIndex = Math.floor(progress / 25);
            stages.forEach((stage, idx) => {
                stage.classList.toggle('active', idx <= stageIndex);
            });
            
            // Update text
            if (stageIndex < stagesText.length) {
                progressText.textContent = stagesText[stageIndex];
            }
            
            // When progress reaches 85%, simulate AI processing
            if (progress >= 85 && !this.aiStreamComplete) {
                progressText.textContent = 'Running AI Strategic Advisor...';
            }
            
        }, 200);
        
        // Store interval ID to clear later
        this.progressInterval = interval;
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // Hide loading
        loading.style.display = 'none';
        
        // Reset button
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-satellite-dish"></i><span>INITIATE SCAN</span><div class="btn-pulse"></div>';
    }

    displayResults(data) {
        console.log('Displaying results:', data);
        
        // Hide loading
        this.hideLoading();
        
        // Show dashboard
        const dashboard = document.getElementById('dashboard');
        dashboard.style.display = 'block';
        
        // Scroll to dashboard
        dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Set timestamp
        const timestamp = new Date().toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('timestamp').textContent = timestamp;
        
        // Calculate and display scores
        this.displayScores(data);
        
        // Display technical metrics
        this.displayTechnicalMetrics(data.technical || {});
        
        // Display content metrics
        this.displayContentMetrics(data.content || {});
        
        // Display authority metrics
        this.displayAuthorityMetrics(data.authority || {}, data.forecasting || {});
        
        // Display internal structure
        this.displayInternalMetrics(data.internal || {});
        
        // Show success notification
        this.showNotification('SEO audit completed successfully!', 'success');
    }

    displayScores(data) {
        // Calculate scores (simplified for demo)
        const tech = this.calculateTechnicalScore(data.technical || {});
        const content = this.calculateContentScore(data.content || {});
        const authority = this.calculateAuthorityScore(data.authority || {});
        const overall = Math.round((tech + content + authority) / 3);
        
        // Update score cards with animation
        this.animateCounter('techScore', tech, 0);
        this.animateCounter('contentScore', content, 0);
        this.animateCounter('authorityScore', authority, 0);
        this.animateCounter('overallScore', overall, 0);
        
        // Color code based on score
        this.applyScoreColor('techScore', tech);
        this.applyScoreColor('contentScore', content);
        this.applyScoreColor('authorityScore', authority);
        this.applyScoreColor('overallScore', overall);
    }

    animateCounter(elementId, target, current, duration = 1000) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const increment = target / (duration / 16); // 60fps
        const updateCounter = () => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                return;
            }
            
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        };
        
        updateCounter();
    }

    applyScoreColor(elementId, score) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (score >= 80) {
            element.style.color = '#00ff9d'; // Green
        } else if (score >= 60) {
            element.style.color = '#ffd700'; // Gold/Yellow
        } else {
            element.style.color = '#ff4444'; // Red
        }
    }

    calculateTechnicalScore(tech) {
        let score = 50; // Base score
        
        // Core Web Vitals (50 points)
        const vitals = tech.core_web_vitals || {};
        if (vitals.lcp && vitals.lcp <= 2500) score += 15;
        if (vitals.cls && vitals.cls <= 0.1) score += 15;
        if (vitals.inp && vitals.inp <= 200) score += 10;
        
        // Mobile friendly (10 points)
        if (tech.mobile_friendly) score += 10;
        
        // SSL grade (10 points)
        if (tech.ssl_grade === 'A') score += 10;
        
        // Canonical issues (negative)
        if (tech.canonical_issues && tech.canonical_issues.length > 0) {
            score -= tech.canonical_issues.length * 5;
        }
        
        return Math.max(0, Math.min(100, score));
    }

    calculateContentScore(content) {
        let score = 50; // Base score
        
        // Word count (20 points)
        const wordCount = content.word_count || 0;
        if (wordCount >= 1000) score += 20;
        else if (wordCount >= 500) score += 15;
        else if (wordCount >= 300) score += 10;
        else if (wordCount >= 150) score += 5;
        
        // Readability (15 points)
        const readability = content.readability_score || 0;
        if (readability >= 60) score += 15;
        else if (readability >= 40) score += 10;
        
        // Entity diversity (15 points)
        const entities = content.entity_salience || {};
        const entityCount = Object.keys(entities).length;
        if (entityCount >= 10) score += 15;
        else if (entityCount >= 5) score += 10;
        else if (entityCount >= 3) score += 5;
        
        // Thin content penalty
        if (content.thin_content_risk) score -= 20;
        
        return Math.max(0, Math.min(100, score));
    }

    calculateAuthorityScore(authority) {
        let score = 50; // Base score
        
        // Authority score (30 points)
        const authScore = authority.authority_score || 0;
        score += Math.min(30, authScore * 3);
        
        // Backlinks (20 points)
        const backlinks = authority.backlinks || 0;
        if (backlinks >= 100) score += 20;
        else if (backlinks >= 50) score += 15;
        else if (backlinks >= 20) score += 10;
        else if (backlinks >= 10) score += 5;
        
        // E-E-A-T score
        const eeat = authority.e_e_a_t_score || 0;
        score += eeat * 5;
        
        // Toxicity penalty
        if (authority.link_toxicity_risk === 'high') score -= 20;
        else if (authority.link_toxicity_risk === 'medium') score -= 10;
        
        return Math.max(0, Math.min(100, score));
    }

    displayTechnicalMetrics(tech) {
        // Core Web Vitals
        const vitals = tech.core_web_vitals || {};
        this.updateVital('lcp', vitals.lcp, 2500);
        this.updateVital('cls', vitals.cls, 0.1);
        this.updateVital('inp', vitals.inp, 200);
        
        // Mobile score
        const mobileScore = document.getElementById('mobileScore');
        if (tech.mobile_friendly) {
            mobileScore.textContent = '✓ Mobile-Friendly';
            mobileScore.style.color = '#00ff9d';
        } else {
            mobileScore.textContent = '✗ Needs Improvement';
            mobileScore.style.color = '#ff4444';
        }
        
        // SSL Grade
        const sslGrade = document.getElementById('sslGrade');
        const sslDetails = document.getElementById('sslDetails');
        const grade = tech.ssl_grade || 'F';
        
        sslGrade.textContent = `SSL Grade: ${grade}`;
        
        if (grade === 'A') {
            sslGrade.style.color = '#00ff9d';
            sslDetails.textContent = 'Excellent SSL/TLS configuration';
        } else if (grade === 'B' || grade === 'C') {
            sslGrade.style.color = '#ffd700';
            sslDetails.textContent = 'SSL needs improvement';
        } else {
            sslGrade.style.color = '#ff4444';
            sslDetails.textContent = 'Critical SSL issue detected';
        }
    }

    updateVital(elementId, value, threshold) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const valueEl = element.querySelector('.vital-value');
        const statusEl = element.querySelector('.vital-status');
        
        if (!value || value === 0) {
            valueEl.textContent = '--';
            statusEl.textContent = 'No Data';
            statusEl.className = 'vital-status';
            return;
        }
        
        // Format value
        if (elementId === 'cls') {
            valueEl.textContent = value.toFixed(3);
        } else {
            valueEl.textContent = `${Math.round(value)}ms`;
        }
        
        // Determine status
        if (value <= threshold) {
            statusEl.textContent = 'Good';
            statusEl.className = 'vital-status good';
            valueEl.style.color = '#00ff9d';
        } else if (value <= threshold * 1.5) {
            statusEl.textContent = 'Needs Improvement';
            statusEl.className = 'vital-status needs-improvement';
            valueEl.style.color = '#ffd700';
        } else {
            statusEl.textContent = 'Poor';
            statusEl.className = 'vital-status poor';
            valueEl.style.color = '#ff4444';
        }
    }

    displayContentMetrics(content) {
        // Word count
        const wordCount = document.getElementById('wordCount');
        const count = content.word_count || 0;
        wordCount.textContent = `${count.toLocaleString()} words`;
        
        // Readability
        const readability = document.getElementById('readability');
        const score = content.readability_score || 0;
        readability.textContent = `Readability: ${Math.round(score)}/100`;
        readability.style.color = score >= 60 ? '#00ff9d' : score >= 40 ? '#ffd700' : '#ff4444';
        
        // Thin content warning
        const thinWarning = document.getElementById('thinWarning');
        if (content.thin_content_risk) {
            thinWarning.style.display = 'flex';
        } else {
            thinWarning.style.display = 'none';
        }
        
        // Intent
        const intent = document.getElementById('intent');
        const intentDesc = document.getElementById('intentDesc');
        const intentType = content.intent_classification || 'unknown';
        
        intent.textContent = intentType.toUpperCase();
        
        const intentDescriptions = {
            'informational': 'Content focuses on providing information and answering questions',
            'transactional': 'Content aims to drive purchases or conversions',
            'navigational': 'Content helps users navigate or find specific resources',
            'commercial': 'Content compares products or services for purchase decisions'
        };
        
        intentDesc.textContent = intentDescriptions[intentType] || 'Intent classification unavailable';
        
        // Keywords
        const keywords = document.getElementById('keywords');
        const topKeywords = content.top_keywords || [];
        
        keywords.innerHTML = '';
        topKeywords.slice(0, 5).forEach(([keyword, count]) => {
            const span = document.createElement('span');
            span.textContent = `${keyword} (${count})`;
            span.className = 'keyword-tag';
            keywords.appendChild(span);
        });
    }

    displayAuthorityMetrics(authority, forecast) {
        // Authority score
        const daScore = document.getElementById('daScore');
        const daDesc = document.getElementById('daDesc');
        const authScore = authority.authority_score || 0;
        const displayScore = Math.round(authScore * 10);
        
        daScore.textContent = `${displayScore}/100`;
        daScore.style.color = displayScore >= 60 ? '#00ff9d' : displayScore >= 40 ? '#ffd700' : '#ff4444';
        daDesc.textContent = displayScore >= 60 ? 'Strong domain authority' : 
                            displayScore >= 40 ? 'Moderate authority' : 'Low authority - Needs building';
        
        // Backlinks
        const backlinks = document.getElementById('backlinks');
        const toxicity = document.getElementById('toxicity');
        const linkCount = authority.backlinks || 0;
        
        backlinks.textContent = `${linkCount.toLocaleString()} estimated backlinks`;
        backlinks.style.color = linkCount >= 100 ? '#00ff9d' : linkCount >= 50 ? '#ffd700' : '#ff4444';
        
        const toxicityLevel = authority.link_toxicity_risk || 'low';
        toxicity.textContent = `Toxicity Risk: ${toxicityLevel.toUpperCase()}`;
        toxicity.style.color = toxicityLevel === 'high' ? '#ff4444' : 
                              toxicityLevel === 'medium' ? '#ffd700' : '#00ff9d';
        
        // Traffic forecast
        const trafficLow = document.getElementById('trafficLow');
        const trafficMid = document.getElementById('trafficMid');
        const trafficHigh = document.getElementById('trafficHigh');
        
        if (forecast) {
            trafficLow.textContent = forecast.pessimistic?.toLocaleString() || '--';
            trafficMid.textContent = forecast.expected?.toLocaleString() || '--';
            trafficHigh.textContent = forecast.optimistic?.toLocaleString() || '--';
        } else {
            trafficLow.textContent = '--';
            trafficMid.textContent = '--';
            trafficHigh.textContent = '--';
        }
    }

    displayInternalMetrics(internal) {
        // Crawl stats
        const pagesCrawled = document.getElementById('pagesCrawled');
        const internalLinks = document.getElementById('internalLinks');
        const externalLinks = document.getElementById('externalLinks');
        
        pagesCrawled.textContent = internal.pages_crawled || '--';
        internalLinks.textContent = internal.internal_links_found || '--';
        externalLinks.textContent = internal.external_links_found || '--';
        
        // Structure health
        const structureHealth = document.getElementById('structureHealth');
        const structureDesc = document.getElementById('structureDesc');
        const healthScore = internal.site_structure_health || 0;
        
        structureHealth.textContent = `${Math.round(healthScore)}/100`;
        structureHealth.style.color = healthScore >= 80 ? '#00ff9d' : 
                                     healthScore >= 60 ? '#ffd700' : '#ff4444';
        
        structureDesc.textContent = healthScore >= 80 ? 'Excellent site structure' :
                                   healthScore >= 60 ? 'Good structure' : 'Needs improvement';
        
        // Warnings
        const warningsList = document.getElementById('structureWarnings');
        const warnings = internal.crawl_warnings || [];
        
        warningsList.innerHTML = '';
        if (warnings.length === 0) {
            warningsList.innerHTML = '<li style="color:#00ff9d"><i class="fas fa-check-circle"></i> No critical issues found</li>';
        } else {
            warnings.forEach(warning => {
                const li = document.createElement('li');
                li.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${warning}`;
                warningsList.appendChild(li);
            });
        }
    }

    async startAIStream(data) {
        const aiStream = document.getElementById('aiStream');
        const techFixes = document.getElementById('techFixes');
        const contentOpps = document.getElementById('contentOpps');
        const quickWins = document.getElementById('quickWins');
        
        // Clear previous content
        aiStream.innerHTML = '';
        techFixes.innerHTML = '';
        contentOpps.innerHTML = '';
        quickWins.innerHTML = '';
        
        // Create initial message
        const initialMsg = document.createElement('div');
        initialMsg.className = 'ai-message';
        initialMsg.innerHTML = `
            <i class="fas fa-brain"></i>
            <div>
                <p><strong>AI Strategic Advisor Initialized</strong></p>
                <p>Analyzing SEO metrics based on "The Art of SEO" 4th Edition principles...</p>
            </div>
        `;
        aiStream.appendChild(initialMsg);
        
        // Simulate AI thinking for demo (in production, this would connect to real AI)
        setTimeout(() => {
            this.simulateAIResponse(data);
        }, 1500);
    }

    simulateAIResponse(data) {
        const aiStream = document.getElementById('aiStream');
        const techFixes = document.getElementById('techFixes');
        const contentOpps = document.getElementById('contentOpps');
        const quickWins = document.getElementById('quickWins');
        
        // Add streaming effect
        const streamingMsg = document.createElement('div');
        streamingMsg.className = 'ai-message';
        streamingMsg.innerHTML = `
            <i class="fas fa-robot"></i>
            <div>
                <p><strong>Analysis Complete</strong></p>
                <p id="streamingText"></p>
            </div>
        `;
        aiStream.appendChild(streamingMsg);
        
        const textElement = streamingMsg.querySelector('#streamingText');
        const analysisText = this.generateAIAnalysis(data);
        
        // Stream the text
        this.typeWriter(textElement, analysisText, 0, () => {
            // After streaming, populate the categories
            this.populateAICategories(data);
            this.aiStreamComplete = true;
        });
    }

    typeWriter(element, text, i, callback) {
        if (i < text.length) {
            element.innerHTML = text.substring(0, i + 1) + '<span class="cursor">|</span>';
            setTimeout(() => this.typeWriter(element, text, i + 1, callback), 30);
        } else {
            element.innerHTML = text;
            if (callback) callback();
        }
    }

    generateAIAnalysis(data) {
        const tech = data.technical || {};
        const content = data.content || {};
        const authority = data.authority || {};
        
        let analysis = "Based on my analysis, here are the key findings:\n\n";
        
        // Technical issues
        const vitals = tech.core_web_vitals || {};
        if (vitals.lcp > 2500) {
            analysis += "• LCP needs improvement (>2.5s). Optimize largest contentful paint.\n";
        }
        if (vitals.cls > 0.1) {
            analysis += "• Layout shifts detected. Fix CLS issues for better UX.\n";
        }
        if (!tech.mobile_friendly) {
            analysis += "• Mobile responsiveness needs improvement.\n";
        }
        
        // Content issues
        if (content.thin_content_risk) {
            analysis += "• Content depth is insufficient. Expand topic coverage.\n";
        }
        if (content.word_count < 300) {
            analysis += "• Consider expanding content for better topical authority.\n";
        }
        
        // Authority issues
        if ((authority.authority_score || 0) < 4) {
            analysis += "• Domain authority is low. Focus on link building.\n";
        }
        
        analysis += "\nPriority Recommendations: Technical fixes first, then content expansion, followed by authority building.";
        
        return analysis;
    }

    populateAICategories(data) {
        const tech = data.technical || {};
        const content = data.content || {};
        const authority = data.authority || {};
        
        // Technical Fixes
        const techFixes = document.getElementById('techFixes');
        const fixes = [];
        
        const vitals = tech.core_web_vitals || {};
        if (vitals.lcp > 2500) {
            fixes.push('Optimize images and defer non-critical JavaScript to improve LCP');
        }
        if (vitals.cls > 0.1) {
            fixes.push('Add size attributes to images and ads to prevent layout shifts');
        }
        if (!tech.mobile_friendly) {
            fixes.push('Implement responsive design and test on mobile devices');
        }
        if (tech.ssl_grade !== 'A') {
            fixes.push('Upgrade SSL/TLS configuration for better security');
        }
        
        if (fixes.length === 0) {
            fixes.push('No critical technical issues detected');
        }
        
        fixes.forEach(fix => {
            const li = document.createElement('li');
            li.textContent = fix;
            techFixes.appendChild(li);
        });
        
        // Content Opportunities
        const contentOpps = document.getElementById('contentOpps');
        const opportunities = [];
        
        if (content.thin_content_risk) {
            opportunities.push('Expand content with comprehensive topic coverage');
        }
        if ((content.word_count || 0) < 500) {
            opportunities.push('Increase content depth for better topical authority');
        }
        if (!content.entity_salience || Object.keys(content.entity_salience).length < 5) {
            opportunities.push('Add more entity mentions for semantic relevance');
        }
        
        if (opportunities.length === 0) {
            opportunities.push('Content quality is good - focus on optimization');
        }
        
        opportunities.forEach(opp => {
            const li = document.createElement('li');
            li.textContent = opp;
            contentOpps.appendChild(li);
        });
        
        // Quick Wins
        const quickWins = document.getElementById('quickWins');
        const wins = [];
        
        wins.push('Fix meta title and description if missing or duplicated');
        wins.push('Ensure all images have descriptive alt text');
        wins.push('Check and fix any broken internal links');
        wins.push('Submit updated sitemap to Google Search Console');
        
        wins.forEach(win => {
            const li = document.createElement('li');
            li.textContent = win;
            quickWins.appendChild(li);
        });
    }

    resetAudit() {
        // Reset form
        document.getElementById('urlInput').value = '';
        document.getElementById('urlInput').classList.remove('valid', 'error');
        
        // Hide dashboard
        document.getElementById('dashboard').style.display = 'none';
        
        // Reset AI stream
        this.aiStreamComplete = false;
        
        // Enable button
        const btn = document.getElementById('auditButton');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-satellite-dish"></i><span>INITIATE SCAN</span><div class="btn-pulse"></div>';
        
        // Show notification
        this.showNotification('Ready for new audit', 'info');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    exportPDF() {
        this.showNotification('PDF export will be available in Pro version', 'info');
        
        // Demo PDF generation
        const element = document.getElementById('dashboard');
        element.style.boxShadow = '0 0 0 2px #00f3ff';
        setTimeout(() => element.style.boxShadow = '', 1000);
    }

    shareReport() {
        if (!this.currentAudit) {
            this.showNotification('No report to share', 'error');
            return;
        }
        
        // Create shareable URL
        const url = this.currentAudit.url || '';
        const shareText = `SEO Audit for ${url}\n\nOverall Score: ${document.getElementById('overallScore').textContent}\nTechnical: ${document.getElementById('techScore').textContent}\nContent: ${document.getElementById('contentScore').textContent}\nAuthority: ${document.getElementById('authorityScore').textContent}`;
        
        // Copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            this.showNotification('Report summary copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy to clipboard', 'error');
        });
    }

    runBenchmark() {
        this.showNotification('Competitor benchmarking is a Pro feature', 'info');
        
        // Demo animation
        const benchmarkBtn = document.getElementById('runBenchmark');
        benchmarkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Benchmarking...';
        benchmarkBtn.disabled = true;
        
        setTimeout(() => {
            benchmarkBtn.innerHTML = '<i class="fas fa-chart-bar"></i> Benchmark Competitors';
            benchmarkBtn.disabled = false;
        }, 2000);
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        // Add to body
        document.body.appendChild(notification);
        
        // Show with animation
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    }
}

// Add notification styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        z-index: 10000;
        transform: translateX(150%);
        transition: transform 0.3s ease;
        min-width: 300px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.success {
        border-left: 4px solid #00ff9d;
    }
    
    .notification.error {
        border-left: 4px solid #ff4444;
    }
    
    .notification.info {
        border-left: 4px solid #00f3ff;
    }
    
    .notification.warning {
        border-left: 4px solid #ffd700;
    }
    
    .notification i:first-child {
        font-size: 1.2rem;
    }
    
    .notification.success i:first-child {
        color: #00ff9d;
    }
    
    .notification.error i:first-child {
        color: #ff4444;
    }
    
    .notification.info i:first-child {
        color: #00f3ff;
    }
    
    .notification.warning i:first-child {
        color: #ffd700;
    }
    
    .notification span {
        flex: 1;
        font-size: 0.9rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        padding: 5px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    
    .notification-close:hover {
        color: white;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .shake {
        animation: shake 0.5s ease;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .cursor {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    .keyword-tag {
        display: inline-block;
        padding: 4px 8px;
        background: rgba(157, 0, 255, 0.1);
        color: #9d00ff;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 2px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
    }
`;
document.head.appendChild(notificationStyles);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.seoVisionPro = new SEOVisionPro();
    console.log('SEO Vision Pro Ready!');
});

// Demo data for testing (remove in production)
window.demoAudit = {
    url: 'https://example.com',
    technical: {
        status_code: 200,
        core_web_vitals: {
            lcp: 1800,
            cls: 0.05,
            inp: 150,
            fcp: 1200,
            performance_score: 85
        },
        mobile_friendly: true,
        ssl_grade: 'A',
        canonical_issues: [],
        page_size_kb: 450
    },
    content: {
        word_count: 1250,
        top_keywords: [['seo', 15], ['optimization', 12], ['search', 10], ['google', 8], ['content', 7]],
        readability_score: 72,
        entity_salience: { 'SEO': 5, 'Google': 4, 'Content': 3, 'Marketing': 2 },
        intent_classification: 'informational',
        thin_content_risk: false
    },
    authority: {
        authority_score: 6.5,
        backlinks: 850,
        e_e_a_t_score: 7,
        link_toxicity_risk: 'low',
        ymyl_category: null
    },
    internal: {
        pages_crawled: 42,
        internal_links_found: 125,
        external_links_found: 68,
        site_structure_health: 82,
        crawl_warnings: ['3 pages with no internal links detected']
    },
    forecasting: {
        pessimistic: 12500,
        expected: 18500,
        optimistic: 24500
    }
};
