class SEOVisionPro {
    constructor() {
        this.currentAudit = null;
        this.aiStream = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkHealth();
    }

    bindEvents() {
        document.getElementById('auditButton').addEventListener('click', () => this.startAudit());
        document.getElementById('newAudit').addEventListener('click', () => this.resetAudit());
        document.getElementById('exportPDF').addEventListener('click', () => this.exportPDF());
        document.getElementById('shareReport').addEventListener('click', () => this.shareReport());
        document.getElementById('runBenchmark').addEventListener('click', () => this.runBenchmark());
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('System health:', data);
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }

    async startAudit() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();

        if (!this.validateURL(url)) {
            this.showNotification('Please enter a valid URL starting with http:// or https://', 'error');
            return;
        }

        // Show loading, hide dashboard
        this.showLoading();
        document.getElementById('dashboard').style.display = 'none';

        try {
            const response = await fetch('/api/audit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    plan: 'free'
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Audit failed');
            }

            this.currentAudit = data;
            this.displayResults(data);
            this.startAIStream(data);

        } catch (error) {
            this.showNotification(`Audit failed: ${error.message}`, 'error');
            this.hideLoading();
        }
    }

    validateURL(url) {
        try {
            new URL(url);
            return url.startsWith('http://') || url.startsWith('https://');
        } catch {
            return false;
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        loading.style.display = 'block';

        // Animate progress bar
        let progress = 0;
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const progressPercent = document.getElementById('progressPercent');
        const stages = document.querySelectorAll('.stage');

        const stagesText = [
            'Crawling target website...',
            'Analyzing technical metrics...',
            'Processing content data...',
            'Running AI analysis...'
        ];

        const interval = setInterval(() => {
            if (progress >= 100) {
                clearInterval(interval);
                return;
            }

            progress += Math.random() * 5 + 1;
            if (progress > 100) progress = 100;

            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${Math.floor(progress)}%`;

            // Update stage
            const stageIndex = Math.floor(progress / 25);
            stages.forEach((stage, idx) => {
                stage.classList.toggle('active', idx <= stageIndex);
            });

            if (stageIndex < stagesText.length) {
                progressText.textContent = stagesText[stageIndex];
            }

        }, 200);
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    displayResults(data) {
        this.hideLoading();
        
        // Set timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        
        // Calculate scores
        const techScore = this.calculateTechnicalScore(data.technical);
        const contentScore = this.calculateContentScore(data.content);
        const authorityScore = this.calculateAuthorityScore(data.authority);
        const overallScore = Math.round((techScore + contentScore + authorityScore) / 3);
        
        // Update scores
        document.getElementById('techScore').textContent = techScore;
        document.getElementById('contentScore').textContent = contentScore;
        document.getElementById('authorityScore').textContent = authorityScore;
        document.getElementById('overallScore').textContent = overallScore;
        
        // Technical metrics
        const vitals = data.technical.core_web_vitals || {};
        this.updateVital('lcp', vitals.lcp, 2500, 'Largest Contentful Paint');
        this.updateVital('cls', vitals.cls, 0.1, 'Cumulative Layout Shift');
        this.updateVital('inp', vitals.inp, 200, 'Interaction to Next Paint');
        
        // Mobile score
        document.getElementById('mobileScore').textContent = 
            data.technical.mobile_friendly ? '✓ Mobile-Friendly' : '✗ Not Mobile-Friendly';
        
        // SSL grade
        const sslGrade = data.technical.ssl_grade || 'F';
        document.getElementById('sslGrade').textContent = `SSL Grade: ${sslGrade}`;
        document.getElementById('sslDetails').textContent = 
            sslGrade === 'A' ? 'Excellent SSL configuration' : 'SSL needs improvement';
        
        // Content metrics
        document.getElementById('wordCount').textContent = `${data.content.word_count || 0} words`;
        document.getElementById('readability').textContent = 
            `Readability: ${Math.round(data.content.readability_score || 0)}/100`;
        
        if (data.content.thin_content_risk) {
            document.getElementById('thinWarning').style.display = 'block';
        }
        
        // Intent
        const intent = data.content.intent_classification || 'unknown';
        document.getElementById('intent').textContent = intent.toUpperCase();
        document.getElementById('intentDesc').textContent = 
            intent === 'informational' ? 'Content focuses on providing information' :
            intent === 'transactional' ? 'Content aims to drive purchases' :
            intent === 'navigational' ? 'Content helps users navigate' : 'Intent unclear';
        
        // Keywords
        const keywords = data.content.top_keywords || [];
        const keywordsHtml = keywords.slice(0, 5).map(k => 
            `<span>${k[0]} (${k[1]})</span>`
        ).join('');
        document.getElementById('keywords').innerHTML = keywordsHtml;
        
        // Authority metrics
        document.getElementById('daScore').textContent = 
            `${Math.round((data.authority.authority_score || 0) * 10)}/100`;
        document.getElementById('daDesc').textContent = 
            data.authority.authority_score > 4 ? 'Strong authority' : 'Building authority';
        
        document.getElementById('backlinks').textContent = 
            `${data.authority.backlinks || 0} estimated backlinks`;
        
        // Traffic forecast
        const forecast = data.forecasting || {};
        document.getElementById('trafficLow').textContent = forecast.pessimistic || '--';
        document.getElementById('trafficMid').textContent = forecast.expected || '--';
        document.getElementById('trafficHigh').textContent = forecast.optimistic || '--';
        
        // Internal structure
        const internal = data.internal || {};
        document.getElementById('pagesCrawled').textContent = internal.pages_crawled || '--';
        document.getElementById('internalLinks').text
