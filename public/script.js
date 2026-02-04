class SEOVisionPro {
    constructor() {
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        console.log('SEO Vision Pro - REAL Analysis');
        this.bindEvents();
        this.testConnection();
    }

    async testConnection() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (response.ok) {
                const data = await response.json();
                console.log('✅ API Connected:', data);
                this.showNotification('✅ Connected to Real SEO Analyzer', 'success');
            }
        } catch (error) {
            console.warn('⚠️ API test failed:', error);
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
        
        const exportBtn = document.getElementById('exportPDF');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportReport());
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
            this.showNotification('Please enter a URL to analyze', 'error');
            return;
        }
        
        if (!this.isValidURL(url)) {
            this.showNotification('Please enter a valid URL (include http:// or https://)', 'error');
            if (urlInput) {
                urlInput.classList.add('shake');
                setTimeout(() => urlInput.classList.remove('shake'), 500);
            }
            return;
        }
        
        this.showLoading();
        
        try {
            console.log('Starting REAL analysis for:', url);
            
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
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('REAL Analysis completed:', data);
            
            if (data.error) {
                throw new Error(data.message || data.error);
            }
            
            // Verify it's real analysis
            if (!data.real_analysis && data.error) {
                throw new Error(data.message || 'Analysis failed');
            }
            
            this.displayRealResults(data);
            
        } catch (error) {
            console.error('Audit error:', error);
            this.showNotification(`❌ ${error.message}`, 'error');
            this.hideLoading();
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        const progressText = document.getElementById('progressText');
        
        if (loading) {
            loading.style.display = 'block';
            if (progressText) {
                progressText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing real website data...';
            }
        }
        
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ANALYZING...';
        }
        
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        
        if (!progressFill) return;
        
        let progress = 0;
        const stages = [
            'Fetching website...',
            'Analyzing content...',
            'Checking technical SEO...',
            'Calculating scores...',
            'Generating report...'
        ];
        
        const interval = setInterval(() => {
            progress += Math.random() * 8 + 2;
            if (progress > 95) progress = 95; // Keep at 95% until API returns
            
            if (progressFill) progressFill.style.width = `${progress}%`;
            if (progressPercent) progressPercent.textContent = `${Math.floor(progress)}%`;
            
            const stageIndex = Math.min(Math.floor(progress / 20), stages.length - 1);
            const progressText = document.getElementById('progressText');
            if (progressText && stages[stageIndex]) {
                progressText.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${stages[stageIndex]}`;
            }
            
            this.progressInterval = interval;
        }, 300);
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // Complete progress bar
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        if (progressFill) progressFill.style.width = '100%';
        if (progressPercent) progressPercent.textContent = '100%';
        
        setTimeout(() => {
            if (loading) loading.style.display = 'none';
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-satellite-dish"></i> INITIATE SCAN';
            }
        }, 500);
    }

    displayRealResults(data) {
        console.log('Displaying REAL results:', data);
        
        this.hideLoading();
        
        const dashboard = document.getElementById('dashboard');
        if (dashboard) {
            dashboard.style.display = 'block';
            setTimeout(() => {
                dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
        
        // Update timestamp
        const timestamp = new Date().toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        this.updateElement('timestamp', timestamp);
        
        // Show real analysis badge
        const realBadge = document.getElementById('realBadge') || this.createRealBadge();
        
        // Update scores with animation
        if (data.scores) {
            this.animateCounter('techScore', data.scores.technical, 0, 1000);
            this.animateCounter('contentScore', data.scores.content, 0, 1000);
            this.animateCounter('authorityScore', data.scores.authority, 0, 1000);
            this.animateCounter('overallScore', data.scores.overall, 0, 1000);
            
            this.applyScoreColor('techScore', data.scores.technical);
            this.applyScoreColor('contentScore', data.scores.content);
            this.applyScoreColor('authorityScore', data.scores.authority);
            this.applyScoreColor('overallScore', data.scores.overall);
        }
        
        // Update metrics
        if (data.metrics) {
            this.updateElement('wordCount', `${data.metrics.word_count.toLocaleString()} words`);
            this.updateElement('sentenceCount', `${data.metrics.sentence_count} sentences`);
            this.updateElement('pageTitle', data.metrics.title);
            this.updateElement('titleLength', `${data.metrics.title_length} chars`);
            this.updateElement('metaDescription', data.metrics.meta_description);
            this.updateElement('metaDescLength', `${data.metrics.meta_description_length} chars`);
            this.updateElement('h1Count', data.metrics.h1_count);
            this.updateElement('h2Count', data.metrics.h2_count);
            this.updateElement('imagesTotal', `${data.metrics.images_total} images`);
            this.updateElement('imagesWithAlt', `${data.metrics.images_with_alt} with alt text`);
            this.updateElement('imagesWithoutAlt', `${data.metrics.images_without_alt} missing alt`);
            this.updateElement('internalLinks', data.metrics.internal_links);
            this.updateElement('externalLinks', data.metrics.external_links);
            this.updateElement('pageSize', `${data.metrics.page_size_kb} KB`);
            this.updateElement('loadTime', `${data.metrics.load_time_seconds}s`);
            this.updateElement('responseCode', data.metrics.response_code);
            
            // Update boolean indicators
            this.updateBoolean('hasViewport', data.metrics.has_viewport);
            this.updateBoolean('hasCanonical', data.metrics.has_canonical);
            this.updateBoolean('hasOgTags', data.metrics.has_og_tags);
            this.updateBoolean('hasTwitterCard', data.metrics.has_twitter_card);
            this.updateBoolean('hasSchema', data.metrics.has_schema_markup);
        }
        
        // Display top keywords
        if (data.top_keywords && data.top_keywords.length > 0) {
            const keywordsContainer = document.getElementById('topKeywords');
            if (keywordsContainer) {
                keywordsContainer.innerHTML = '';
                data.top_keywords.slice(0, 8).forEach(kw => {
                    const badge = document.createElement('span');
                    badge.className = 'keyword-badge';
                    badge.textContent = `${kw.keyword} (${kw.frequency})`;
                    keywordsContainer.appendChild(badge);
                });
            }
        }
        
        // Display issues
        if (data.issues && data.issues.length > 0) {
            const issuesList = document.getElementById('issuesList');
            if (issuesList) {
                issuesList.innerHTML = '';
                data.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${issue}`;
                    issuesList.appendChild(li);
                });
            }
        } else {
            this.updateElement('issuesList', '<li style="color:#00ff9d"><i class="fas fa-check-circle"></i> No critical issues found!</li>');
        }
        
        // Display recommendations
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
        
        // Show technical details if available
        if (data.technical_details) {
            this.updateElement('finalUrl', data.technical_details.final_url);
            this.updateElement('redirectCount', data.technical_details.redirect_count);
        }
        
        // Show success notification
        const analysisTime = data.analysis_time ? `in ${data.analysis_time}s` : '';
        this.showNotification(`✅ Real SEO analysis complete ${analysisTime}!`, 'success');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    updateBoolean(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = value ? 
                '<i class="fas fa-check-circle" style="color:#00ff9d"></i> Yes' : 
                '<i class="fas fa-times-circle" style="color:#ff4444"></i> No';
        }
    }

    animateCounter(elementId, target, current, duration) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const increment = target / (duration / 16);
        const update = () => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                return;
            }
            element.textContent = Math.floor(current);
            requestAnimationFrame(update);
        };
        update();
    }

    applyScoreColor(elementId, score) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (score >= 80) element.style.color = '#00ff9d';
        else if (score >= 60) element.style.color = '#ffd700';
        else element.style.color = '#ff4444';
    }

    createRealBadge() {
        const badge = document.createElement('div');
        badge.id = 'realBadge';
        badge.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #00ff9d, #00f3ff);
            color: #000;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 100;
        `;
        badge.textContent = 'REAL ANALYSIS';
        
        const dashboard = document.getElementById('dashboard');
        if (dashboard) {
            dashboard.style.position = 'relative';
            dashboard.appendChild(badge);
        }
        
        return badge;
    }

    resetAudit() {
        const urlInput = document.getElementById('urlInput');
        if (urlInput) urlInput.value = '';
        
        const dashboard = document.getElementById('dashboard');
        if (dashboard) dashboard.style.display = 'none';
        
        const btn = document.getElementById('auditButton');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-satellite-dish"></i> INITIATE SCAN';
        }
        
        this.showNotification('Ready for new analysis', 'info');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    exportReport() {
        this.showNotification('Export feature coming soon!', 'info');
    }

    showNotification(message, type = 'info') {
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();
        
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'info': 'info-circle',
            'warning': 'exclamation-triangle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${icons[type] || 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    }
}

// Add styles for real analysis
const realAnalysisStyles = document.createElement('style');
realAnalysisStyles.textContent = `
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
        border
