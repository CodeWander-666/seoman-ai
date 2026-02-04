class SEOVisionPro {
    constructor() {
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        console.log('SEO Vision Pro - Real Analysis');
        this.bindEvents();
        this.testAPI();
    }

    async testAPI() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (response.ok) {
                console.log('✅ API connected successfully');
            }
        } catch (error) {
            console.warn('⚠️ API connection test failed');
        }
    }

    bindEvents() {
        const auditBtn = document.getElementById('auditButton');
        if (auditBtn) {
            auditBtn.addEventListener('click', () => this.startAudit());
        }
        
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.startAudit();
            });
        }
        
        const newAuditBtn = document.getElementById('newAudit');
        if (newAuditBtn) {
            newAuditBtn.addEventListener('click', () => this.resetAudit());
        }
    }

    isValidURL(string) {
        try {
            new URL(string);
            return string.startsWith('http://') || string.startsWith('https://');
        } catch {
            return false;
        }
    }

    async startAudit() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput ? urlInput.value.trim() : '';
        
        if (!url) {
            alert('Please enter a URL to analyze');
            return;
        }
        
        if (!this.isValidURL(url)) {
            alert('Please enter a valid URL starting with http:// or https://');
            return;
        }
        
        // Show loading
        this.showLoading();
        
        try {
            console.log('Starting REAL analysis for:', url);
            
            const response = await fetch(`${this.baseURL}/api/audit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    plan: 'free'
                })
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Analysis completed:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display results
            this.displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Analysis failed: ' + error.message);
            this.hideLoading();
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const dashboard = document.getElementById('dashboard');
        const btn = document.getElementById('auditButton');
        
        if (loading) loading.style.display = 'block';
        if (dashboard) dashboard.style.display = 'none';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
        
        // Animate progress bar
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        
        if (!progressFill) return;
        
        let progress = 0;
        const stages = [
            'Fetching website...',
            'Analyzing content...',
            'Checking technical SEO...',
            'Calculating scores...'
        ];
        
        const interval = setInterval(() => {
            progress += Math.random() * 5 + 1;
            if (progress > 90) progress = 90;
            
            if (progressFill) progressFill.style.width = `${progress}%`;
            if (progressPercent) progressPercent.textContent = `${Math.floor(progress)}%`;
            
            const stageIndex = Math.min(Math.floor(progress / 25), stages.length - 1);
            if (progressText && stages[stageIndex]) {
                progressText.textContent = stages[stageIndex];
            }
            
            this.progressInterval = interval;
        }, 200);
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        setTimeout(() => {
            if (loading) loading.style.display = 'none';
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-play"></i> Start SEO Analysis';
            }
        }, 500);
    }

    displayResults(data) {
        console.log('Displaying results:', data);
        
        this.hideLoading();
        
        const dashboard = document.getElementById('dashboard');
        if (dashboard) {
            dashboard.style.display = 'block';
            dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Update scores with color coding
        if (data.scores) {
            this.updateScore('techScore', data.scores.technical);
            this.updateScore('contentScore', data.scores.content);
            this.updateScore('authorityScore', data.scores.authority);
            this.updateScore('overallScore', data.scores.overall);
        }
        
        // Update metrics
        if (data.metrics) {
            this.updateElement('wordCount', data.metrics.word_count.toLocaleString());
            this.updateElement('pageTitle', data.metrics.title);
            this.updateElement('metaDescription', data.metrics.meta_description);
            this.updateElement('h1Count', data.metrics.h1_count);
            this.updateElement('h2Count', data.metrics.h2_count);
            this.updateElement('imagesWithAlt', `${data.metrics.images_with_alt}/${data.metrics.images_total}`);
            this.updateElement('internalLinks', data.metrics.internal_links);
            this.updateElement('externalLinks', data.metrics.external_links);
            this.updateElement('pageSize', `${data.metrics.page_size_kb} KB`);
        }
        
        // Update issues
        if (data.issues && data.issues.length > 0) {
            const issuesList = document.getElementById('issuesList');
            if (issuesList) {
                issuesList.innerHTML = '';
                data.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${issue}`;
                    issuesList.appendChild(li);
                });
            }
        } else {
            const issuesList = document.getElementById('issuesList');
            if (issuesList) {
                issuesList.innerHTML = '<li><i class="fas fa-check-circle"></i> No critical issues found!</li>';
            }
        }
        
        // Update recommendations
        if (data.recommendations && data.recommendations.length > 0) {
            const recList = document.getElementById('recommendationsList');
            if (recList) {
                recList.innerHTML = '';
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-lightbulb"></i> ${rec}`;
                    recList.appendChild(li);
                });
            }
        }
        
        // Show success alert
        alert('✅ SEO analysis completed successfully!');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    updateScore(id, score) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = score;
            
            // Color code based on score
            if (score >= 80) {
                element.style.color = '#10b981'; // Green
            } else if (score >= 60) {
                element.style.color = '#f59e0b'; // Yellow
            } else {
                element.style.color = '#ef4444'; // Red
            }
        }
    }

    resetAudit() {
        const urlInput = document.getElementById('urlInput');
        const dashboard = document.getElementById('dashboard');
        const btn = document.getElementById('auditButton');
        
        if (urlInput) urlInput.value = '';
        if (dashboard) dashboard.style.display = 'none';
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-play"></i> Start SEO Analysis';
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.seoVisionPro = new SEOVisionPro();
    console.log('✅ SEO Vision Pro initialized');
});
