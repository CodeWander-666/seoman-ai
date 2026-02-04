class AdvancedSEOAnalyzer {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentAnalysis = null;
        this.charts = {};
        this.init();
    }

    init() {
        console.log('Advanced SEO Analyzer Initialized');
        this.bindEvents();
        this.setupTabs();
        this.showNotification('✅ Advanced SEO Analyzer Ready', 'success');
    }

    bindEvents() {
        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => this.startAnalysis());
        
        // URL input enter key
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startAnalysis();
        });
        
        // New analysis button
        document.getElementById('newAnalysisBtn').addEventListener('click', () => this.resetAnalysis());
        
        // Export report button
        document.getElementById('exportReportBtn').addEventListener('click', () => this.exportReport());
        
        // Share results button
        document.getElementById('shareResultsBtn').addEventListener('click', () => this.shareResults());
    }

    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons and contents
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Show corresponding content
                const tabId = btn.getAttribute('data-tab');
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
    }

    isValidURL(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        } catch {
            return false;
        }
    }

    async startAnalysis() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();
        
        if (!url) {
            this.showNotification('Please enter a website URL', 'error');
            return;
        }
        
        if (!this.isValidURL(url)) {
            this.showNotification('Please enter a valid URL starting with http:// or https://', 'error');
            urlInput.classList.add('shake');
            setTimeout(() => urlInput.classList.remove('shake'), 500);
            return;
        }
        
        // Show loading and hide dashboard
        this.showLoading();
        document.getElementById('dashboard').style.display = 'none';
        
        // Show real-time badge
        document.getElementById('realTimeBadge').style.display = 'flex';
        
        try {
            console.log('Starting advanced analysis for:', url);
            
            const response = await fetch(`${this.baseURL}/api/audit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    plan: 'advanced'
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Analysis completed:', data);
            
            if (data.error) {
                throw new Error(data.message || data.error);
            }
            
            this.currentAnalysis = data;
            this.displayAdvancedResults(data);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification(`Analysis failed: ${error.message}`, 'error');
            this.hideLoading();
            document.getElementById('realTimeBadge').style.display = 'none';
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('analyzeBtn');
        
        // Show loading
        loading.style.display = 'block';
        
        // Disable button
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ANALYZING...';
        
        // Animate progress
        this.animateProgress();
    }

    animateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        
        let progress = 0;
        const stages = [
            'Fetching website data...',
            'Analyzing technical SEO...',
            'Evaluating content quality...',
            'Checking performance metrics...',
            'Auditing security...',
            'Analyzing site structure...',
            'Generating insights...',
            'Compiling final report...'
        ];
        
        const interval = setInterval(() => {
            progress += Math.random() * 8 + 2;
            if (progress > 95) progress = 95;
            
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${Math.floor(progress)}%`;
            
            const stageIndex = Math.min(Math.floor(progress / 12.5), stages.length - 1);
            if (progressText) {
                progressText.textContent = stages[stageIndex];
            }
            
            this.progressInterval = interval;
        }, 300);
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('analyzeBtn');
        
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // Complete progress bar
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        
        setTimeout(() => {
            loading.style.display = 'none';
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-play"></i> Start Advanced Analysis';
        }, 500);
    }

    displayAdvancedResults(data) {
        console.log('Displaying advanced results:', data);
        
        // Hide loading and show dashboard
        this.hideLoading();
        document.getElementById('realTimeBadge').style.display = 'none';
        
        const dashboard = document.getElementById('dashboard');
        dashboard.style.display = 'block';
        dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Display scores
        this.displayScores(data.scores);
        
        // Display metrics
        this.displayMetrics(data);
        
        // Display issues and recommendations
        this.displayIssuesAndRecommendations(data);
        
        // Create charts
        this.createCharts(data);
        
        // Show success notification
        const time = data.analysis_time ? `in ${data.analysis_time}s` : '';
        this.showNotification(`✅ Advanced SEO analysis complete ${time}!`, 'success');
    }

    displayScores(scores) {
        const scoresGrid = document.getElementById('scoresGrid');
        scoresGrid.innerHTML = '';
        
        const scoreCategories = [
            { key: 'overall', label: 'Overall Score', icon: 'fas fa-star', weight: 1 },
            { key: 'technical', label: 'Technical SEO', icon: 'fas fa-cogs', weight: 0.2 },
            { key: 'content', label: 'Content Quality', icon: 'fas fa-file-alt', weight: 0.2 },
            { key: 'performance', label: 'Performance', icon: 'fas fa-tachometer-alt', weight: 0.15 },
            { key: 'security', label: 'Security', icon: 'fas fa-shield-alt', weight: 0.1 },
            { key: 'authority', label: 'Authority', icon: 'fas fa-medal', weight: 0.1 },
            { key: 'social', label: 'Social', icon: 'fas fa-share-alt', weight: 0.1 },
            { key: 'structure', label: 'Structure', icon: 'fas fa-sitemap', weight: 0.05 }
        ];
        
        scoreCategories.forEach(category => {
            const score = scores[category.key] || 0;
            const status = this.getScoreStatus(score);
            
            const scoreCard = document.createElement('div');
            scoreCard.className = 'score-card';
            scoreCard.innerHTML = `
                <div class="score-icon">
                    <i class="${category.icon}"></i>
                </div>
                <div class="score-title">${category.label}</div>
                <div class="score-value" style="color: ${this.getScoreColor(score)}">${score}</div>
                <div class="score-status ${status.class}">${status.label}</div>
            `;
            
            scoresGrid.appendChild(scoreCard);
        });
    }

    getScoreStatus(score) {
        if (score >= 90) return { class: 'status-excellent', label: 'Excellent' };
        if (score >= 70) return { class: 'status-good', label: 'Good' };
        if (score >= 50) return { class: 'status-good', label: 'Fair' };
        return { class: 'status-poor', label: 'Needs Work' };
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981'; // Green
        if (score >= 60) return '#f59e0b'; // Yellow
        return '#ef4444'; // Red
    }

    displayMetrics(data) {
        // Basic info
        this.updateElement('domain', data.domain || '--');
        this.updateElement('statusCode', data.technical?.status_code || '--');
        this.updateElement('analysisTime', `${data.analysis_time || '--'}s`);
        this.updateElement('dataFreshness', data.data_freshness || '--');
        
        // Content metrics
        this.updateElement('wordCount', data.content?.word_count?.toLocaleString() || '--');
        this.updateElement('readability', data.content?.readability_score || '--');
        this.updateElement('imagesWithAlt', `${data.content?.images_with_alt || 0}/${data.content?.images_total || 0}`);
        this.updateElement('internalLinks', data.structure?.internal_links_count || '--');
        
        // Performance metrics
        this.updateElement('performanceScore', data.performance?.performance_score || '--');
        this.updateElement('lcp', data.performance?.core_web_vitals?.lcp ? `${data.performance.core_web_vitals.lcp}ms` : '--');
        this.updateElement('cls', data.performance?.core_web_vitals?.cls || '--');
        this.updateElement('mobileFriendly', data.performance?.mobile_friendly ? 'Yes' : 'No');
        
        // Technical metrics
        this.updateElement('robotsTxt', data.technical?.robots_txt_present ? '✅ Present' : '❌ Missing');
        this.updateElement('sitemap', data.technical?.sitemap_present ? '✅ Present' : '❌ Missing');
        this.updateElement('canonicalTags', data.technical?.canonical_present ? '✅ Present' : '❌ Missing');
        this.updateElement('indexability', this.getIndexabilityStatus(data.technical));
        this.updateElement('urlLength', data.technical?.url_length || '--');
        this.updateElement('urlDepth', data.technical?.url_depth || '--');
        this.updateElement('redirectChain', data.technical?.redirect_chain_length || '--');
        this.updateElement('urlParams', this.hasURLParameters(data.technical));
        
        // Content analysis
        this.updateElement('contentType', data.content?.content_type || '--');
        this.updateElement('readingLevel', data.content?.reading_level || '--');
        this.updateElement('semanticScore', data.content?.semantic_score || '--');
        this.updateElement('thinContent', data.content?.thin_content ? '⚠️ Yes' : '✅ No');
        this.updateElement('topKeyword', data.content?.top_keywords?.[0]?.keyword || '--');
        this.updateElement('keywordDensity', data.content?.keyword_density?.[0]?.density ? `${data.content.keyword_density[0].density}%` : '--');
        this.updateElement('uniqueWords', data.content?.unique_words?.toLocaleString() || '--');
        this.updateElement('lsiKeywords', data.content?.lsi_keywords?.length || '0');
    }

    getIndexabilityStatus(technical) {
        if (!technical) return 'Unknown';
        
        const issues = [];
        if (technical.x_robots_tag && technical.x_robots_tag.includes('noindex')) issues.push('noindex');
        if (technical.redirect_chain_length > 3) issues.push('Redirect chain');
        
        return issues.length > 0 ? `⚠️ ${issues.join(', ')}` : '✅ Indexable';
    }

    hasURLParameters(technical) {
        return technical?.url_parameters ? '⚠️ Yes' : '✅ No';
    }

    displayIssuesAndRecommendations(data) {
        // Clear existing lists
        const clearLists = ['technicalIssues', 'criticalIssues', 'contentRecommendations', 'highPriorityRecs'];
        clearLists.forEach(id => {
            const list = document.getElementById(id);
            if (list) list.innerHTML = '';
        });
        
        // Technical issues
        if (data.technical) {
            const issues = this.extractTechnicalIssues(data.technical);
            this.populateList('technicalIssues', issues);
        }
        
        // Critical issues
        if (data.insights && data.insights.length > 0) {
            this.populateList('criticalIssues', data.insights.slice(0, 5));
        }
        
        // Content recommendations
        if (data.recommendations?.priority_high) {
            this.populateList('contentRecommendations', data.recommendations.priority_high.slice(0, 3));
        }
        
        // High priority recommendations
        if (data.recommendations?.priority_high) {
            this.populateList('highPriorityRecs', data.recommendations.priority_high.slice(0, 5));
        }
    }

    extractTechnicalIssues(technical) {
        const issues = [];
        
        if (!technical.robots_txt_present) {
            issues.push('Missing robots.txt file');
        }
        
        if (!technical.sitemap_present) {
            issues.push('No XML sitemap found');
        }
        
        if (!technical.canonical_present) {
            issues.push('Missing canonical tags');
        }
        
        if (technical.redirect_chain_length > 2) {
            issues.push(`Redirect chain too long (${technical.redirect_chain_length} redirects)`);
        }
        
        if (technical.url_length > 100) {
            issues.push('URL is too long');
        }
        
        return issues;
    }

    populateList(elementId, items) {
        const list = document.getElementById(elementId);
        if (!list || !items || items.length === 0) {
            list.innerHTML = '<li>No items found</li>';
            return;
        }
        
        items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fas fa-info-circle"></i> ${item}`;
            list.appendChild(li);
        });
    }

    createCharts(data) {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) chart.destroy();
        });
        this.charts = {};
        
        // Score distribution chart
        this.createScoreChart(data.scores);
        
        // Opportunity chart
        this.createOpportunityChart(data);
    }

    createScoreChart(scores) {
        const ctx = document.getElementById('scoreChart');
        if (!ctx) return;
        
        // Convert canvas to chart
        ctx.innerHTML = '';
        const canvas = document.createElement('canvas');
        ctx.appendChild(canvas);
        
        const categories = ['Technical', 'Content', 'Performance', 'Security', 'Authority', 'Social', 'Structure'];
        const values = categories.map(cat => scores[cat.toLowerCase()] || 0);
        
        this.charts.scoreChart = new Chart(canvas, {
            type: 'radar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'SEO Scores',
                    data: values,
                    backgroundColor: 'rgba(37, 99, 235, 0.2)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(37, 99, 235, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
    }

    createOpportunityChart(data) {
        const ctx = document.getElementById('opportunityChart');
        if (!ctx) return;
        
        ctx.innerHTML = '';
        const canvas = document.createElement('canvas');
        ctx.appendChild(canvas);
        
        // Calculate opportunities by category
        const opportunities = {
            'Technical': data.technical ? this.countTechnicalOpportunities(data.technical) : 0,
            'Content': data.content ? this.countContentOpportunities(data.content) : 0,
            'Performance': data.performance ? this.countPerformanceOpportunities(data.performance) : 0,
            'Security': data.security ? this.countSecurityOpportunities(data.security) : 0
        };
        
        this.charts.opportunityChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: Object.keys(opportunities),
                datasets: [{
                    label: 'Optimization Opportunities',
                    data: Object.values(opportunities),
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(37, 99, 235, 0.7)',
                        'rgba(16, 185, 129, 0.7)'
                    ],
                    borderColor: [
                        'rgb(239, 68, 68)',
                        'rgb(245, 158, 11)',
                        'rgb(37, 99, 235)',
                        'rgb(16, 185, 129)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Issues'
                        }
                    }
                }
            }
        });
    }

    countTechnicalOpportunities(technical) {
        let count = 0;
        if (!technical.robots_txt_present) count++;
        if (!technical.sitemap_present) count++;
        if (!technical.canonical_present) count++;
        if (technical.redirect_chain_length > 2) count++;
        return count;
    }

    countContentOpportunities(content) {
        let count = 0;
        if (content.thin_content) count++;
        if (content.images_without_alt > 0) count++;
        if (content.word_count < 500) count++;
        if (content.readability_score < 60) count++;
        return count;
    }

    countPerformanceOpportunities(performance) {
        if (!performance) return 0;
        let count = 0;
        if (performance.performance_score < 70) count++;
        if (performance.core_web_vitals?.lcp > 2500) count++;
        if (performance.core_web_vitals?.cls > 0.1) count++;
        if (!performance.mobile_friendly) count++;
        return count;
    }

    countSecurityOpportunities(security) {
        if (!security) return 0;
        let count = 0;
        if (!security.ssl_present) count++;
        if (!security.security_headers?.strict_transport_security) count++;
        if (!security.security_headers?.x_frame_options) count++;
        if (security.days_until_expiry < 30) count++;
        return count;
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    resetAnalysis() {
        // Clear inputs
        document.getElementById('urlInput').value = '';
        
        // Hide dashboard
        document.getElementById('dashboard').style.display = 'none';
        
        // Reset button
        const btn = document.getElementById('analyzeBtn');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Start Advanced Analysis';
        
        // Show notification
        this.showNotification('Ready for new analysis', 'info');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    exportReport() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis data to export', 'error');
            return;
        }
        
        // Create a downloadable JSON file
        const dataStr = JSON.stringify(this.currentAnalysis, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `seo-analysis-${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        this.showNotification('Report exported successfully!', 'success');
    }

    shareResults() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis results to share', 'error');
            return;
        }
        
        const url = this.currentAnalysis.url;
        const overallScore = this.currentAnalysis.scores?.overall || 0;
        
        const shareText = `SEO Analysis for ${url}\nOverall Score: ${overallScore}/100\n\nKey Findings:\n- Technical: ${this.currentAnalysis.scores?.technical || 0}/100\n- Content: ${this.currentAnalysis.scores?.content || 0}/100\n- Performance: ${this.currentAnalysis.scores?.performance || 0}/100\n\nAnalyzed with SEO Vision Pro`;
        
        if (navigator.share) {
            navigator.share({
                title: `SEO Analysis: ${url}`,
                text: shareText,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('Results copied to clipboard!', 'success');
            });
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    }
}

// Initialize the analyzer when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.seoAnalyzer = new AdvancedSEOAnalyzer();
    console.log('Advanced SEO Analyzer Initialized');
});

// Add shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    .shake {
        animation: shake 0.5s ease;
    }
`;
document.head.appendChild(style);
