class SEOVisionPro {
    constructor() {
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        console.log('SEO Vision Pro Initialized');
        this.bindEvents();
        this.setupDemo();
    }

    bindEvents() {
        // Audit button
        document.getElementById('auditButton').addEventListener('click', () => this.startAudit());
        
        // Enter key on input
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startAudit();
        });
        
        // Other buttons
        document.getElementById('newAudit').addEventListener('click', () => this.resetAudit());
        document.getElementById('exportPDF').addEventListener('click', () => this.exportPDF());
    }

    setupDemo() {
        // Pre-fill with demo URL for testing
        const demoUrls = [
            'https://example.com',
            'https://google.com',
            'https://github.com'
        ];
        const urlInput = document.getElementById('urlInput');
        urlInput.placeholder = `Try: ${demoUrls[Math.floor(Math.random() * demoUrls.length)]}`;
    }

    isValidURL(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
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
        
        // Show loading
        this.showLoading();
        
        try {
            console.log('Starting audit for:', url);
            
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
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Audit failed');
            }
            
            const data = await response.json();
            console.log('Audit completed:', data);
            
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
        
        // Disable button
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SCANNING...';
        
        // Show loading
        loading.style.display = 'block';
        
        // Animate progress
        let progress = 0;
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        
        const interval = setInterval(() => {
            progress += Math.random() * 5 + 1;
            if (progress > 90) progress = 90; // Stop at 90% until API returns
            
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${Math.floor(progress)}%`;
            
            this.progressInterval = interval;
        }, 200);
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('auditButton');
        
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // Complete progress bar
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        
        // Hide loading after delay
        setTimeout(() => {
            loading.style.display = 'none';
            
            // Reset button
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-satellite-dish"></i><span>INITIATE SCAN</span><div class="btn-pulse"></div>';
        }, 500);
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
        const timestamp = new Date().toLocaleString();
        document.getElementById('timestamp').textContent = timestamp;
        
        // Display scores
        if (data.scores) {
            document.getElementById('techScore').textContent = data.scores.technical;
            document.getElementById('contentScore').textContent = data.scores.content;
            document.getElementById('authorityScore').textContent = data.scores.authority;
            document.getElementById('overallScore').textContent = data.scores.overall;
            
            // Color code scores
            this.applyScoreColor('techScore', data.scores.technical);
            this.applyScoreColor('contentScore', data.scores.content);
            this.applyScoreColor('authorityScore', data.scores.authority);
            this.applyScoreColor('overallScore', data.scores.overall);
        }
        
        // Display metrics
        if (data.metrics) {
            // Technical metrics
            document.getElementById('wordCount').textContent = `${data.metrics.word_count} words`;
            document.getElementById('pageTitle').textContent = data.metrics.page_title;
            document.getElementById('metaDescription').textContent = data.metrics.meta_description;
            
            // Structure metrics
            document.getElementById('h1Count').textContent = data.metrics.h1_count;
            document.getElementById('h2Count').textContent = data.metrics.h2_count;
            document.getElementById('imagesTotal').textContent = data.metrics.images_total;
            document.getElementById('imagesWithAlt').textContent = data.metrics.images_with_alt;
            document.getElementById('internalLinks').textContent = data.metrics.internal_links;
            document.getElementById('externalLinks').textContent = data.metrics.external_links;
            
            // Page size
            document.getElementById('pageSize').textContent = `${Math.round(data.metrics.page_size_kb)} KB`;
        }
        
        // Display issues
        const issuesList = document.getElementById('issuesList');
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
        
        // Display recommendations
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';
        
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.innerHTML = `<i class="fas fa-lightbulb"></i> ${rec}`;
                recommendationsList.appendChild(li);
            });
        }
        
        // Show success notification
        this.showNotification('SEO audit completed successfully!', 'success');
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

    resetAudit() {
        // Reset form
        document.getElementById('urlInput').value = '';
        
        // Hide dashboard
        document.getElementById('dashboard').style.display = 'none';
        
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
        this.showNotification('Export feature coming soon!', 'info');
        
        // Demo effect
        const element = document.getElementById('dashboard');
        element.style.boxShadow = '0 0 0 2px #00f3ff';
        setTimeout(() => element.style.boxShadow = '', 1000);
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'info': 'info-circle',
            'warning': 'exclamation-triangle'
        };
        
        notification.innerHTML = `
            <i class="fas fa-${icons[type] || 'info-circle'}"></i>
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
    window.seoVisionPro = new SEOVisionPro();
    console.log('SEO Vision Pro Ready!');
});
