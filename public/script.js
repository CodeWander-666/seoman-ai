class SEOVisionPro {
    constructor() {
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        console.log('SEO Vision Pro Initialized');
        this.bindEvents();
        this.setupDemo();
        this.testConnection();
    }

    async testConnection() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (response.ok) {
                console.log('✅ API is connected');
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

    setupDemo() {
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            const demoUrls = [
                'https://example.com',
                'https://google.com',
                'https://github.com',
                'https://stackoverflow.com'
            ];
            urlInput.placeholder = `Try: ${demoUrls[Math.floor(Math.random() * demoUrls.length)]}`;
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
            this.showNotification('Please enter a URL', 'error');
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
            const response = await fetch(`${this.baseURL}/api/audit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    plan: 'free'
                })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Network error' }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.message || data.error);
            }
            
            this.displayResults(data);
            
        } catch (error) {
            console.error('Audit error:', error);
            this.showNotification(`Audit failed: ${error.message}`, 'error');
            this.hideLoading();
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        if (loading) loading.style.display = 'block';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SCANNING...';
        }
        
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        
        if (!progressFill) return;
        
        let progress = 0;
        const stages = [
            'Fetching URL...',
            'Analyzing content...',
            'Checking structure...',
            'Generating report...'
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
                btn.innerHTML = '<i class="fas fa-satellite-dish"></i><span>INITIATE SCAN</span><div class="btn-pulse"></div>';
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
        
        // Update timestamp
        const timestamp = new Date().toLocaleString();
        const timestampEl = document.getElementById('timestamp');
        if (timestampEl) timestampEl.textContent = timestamp;
        
        // Update scores
        if (data.scores) {
            this.updateElement('techScore', data.scores.technical);
            this.updateElement('contentScore', data.scores.content);
            this.updateElement('authorityScore', data.scores.authority);
            this.updateElement('overallScore', data.scores.overall);
            
            this.applyScoreColor('techScore', data.scores.technical);
            this.applyScoreColor('contentScore', data.scores.content);
            this.applyScoreColor('authorityScore', data.scores.authority);
            this.applyScoreColor('overallScore', data.scores.overall);
        }
        
        // Update metrics
        if (data.metrics) {
            this.updateElement('wordCount', `${data.metrics.word_count} words`);
            this.updateElement('pageTitle', data.metrics.title || 'No title');
            this.updateElement('metaDescription', data.metrics.meta_description || 'No description');
            this.updateElement('h1Count', data.metrics.h1_count);
            this.updateElement('h2Count', data.metrics.h2_count);
            this.updateElement('imagesTotal', data.metrics.images_total);
            this.updateElement('imagesWithAlt', data.metrics.images_with_alt);
            this.updateElement('internalLinks', data.metrics.internal_links);
            this.updateElement('externalLinks', data.metrics.external_links);
            this.updateElement('pageSize', `${data.metrics.page_size_kb} KB`);
        }
        
        // Update issues
        const issuesList = document.getElementById('issuesList');
        if (issuesList) {
            issuesList.innerHTML = '';
            
            if (data.issues && data.issues.length > 0) {
                data.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${issue}`;
                    issuesList.appendChild(li);
                });
            } else {
                issuesList.innerHTML = '<li style="color:#00ff9d"><i class="fas fa-check-circle"></i> No critical issues found</li>';
            }
        }
        
        // Update recommendations
        const recommendationsList = document.getElementById('recommendationsList');
        if (recommendationsList) {
            recommendationsList.innerHTML = '';
            
            if (data.recommendations && data.recommendations.length > 0) {
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-lightbulb"></i> ${rec}`;
                    recommendationsList.appendChild(li);
                });
            }
        }
        
        this.showNotification('✅ SEO audit completed!', 'success');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    applyScoreColor(elementId, score) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (score >= 80) {
            element.style.color = '#00ff9d';
        } else if (score >= 60) {
            element.style.color = '#ffd700';
        } else {
            element.style.color = '#ff4444';
        }
    }

    resetAudit() {
        const urlInput = document.getElementById('urlInput');
        if (urlInput) urlInput.value = '';
        
        const dashboard = document.getElementById('dashboard');
        if (dashboard) dashboard.style.display = 'none';
        
        const btn = document.getElementById('auditButton');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-satellite-dish"></i><span>INITIATE SCAN</span><div class="btn-pulse"></div>';
        }
        
        this.showNotification('Ready for new audit', 'info');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showNotification(message, type = 'info') {
        // Remove existing
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

// Add notification styles
const style = document.createElement('style');
style.textContent = `
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
`;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.seoVisionPro = new SEOVisionPro();
        console.log('✅ SEO Vision Pro Ready!');
    } catch (error) {
        console.error('❌ Failed to initialize:', error);
    }
});
