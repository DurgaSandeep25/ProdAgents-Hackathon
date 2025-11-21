// UI Logic for Self-Improving Scraper Dashboard

let isRunning = false;
let currentIteration = 0;
let totalIterations = 3;
let metricsData = {
    iterations: [],
    successRates: [],
    completeness: [],
    quality: []
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadInitialData();
});

function setupEventListeners() {
    document.getElementById('startBtn').addEventListener('click', startScraping);
    document.getElementById('stopBtn').addEventListener('click', stopScraping);
    document.getElementById('resetBtn').addEventListener('click', resetDashboard);
}

function loadInitialData() {
    // Load configuration
    const urlParams = new URLSearchParams(window.location.search);
    const url = urlParams.get('url') || 'https://www.amazon.com/dp/B08N5WRWNW';
    const iterations = parseInt(urlParams.get('iterations') || '3');
    
    document.getElementById('targetUrl').value = url;
    document.getElementById('numIterations').value = iterations;
    totalIterations = iterations;
}

async function startScraping() {
    if (isRunning) return;
    
    isRunning = true;
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    
    addLogEntry('think', 'Starting autonomous scraping agent...');
    
    // In a real implementation, this would connect to the backend
    // For now, simulate the process
    simulateScraping();
}

function stopScraping() {
    isRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    addLogEntry('feedback', 'Scraping stopped by user');
}

function resetDashboard() {
    isRunning = false;
    currentIteration = 0;
    metricsData = { iterations: [], successRates: [], completeness: [], quality: [] };
    
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('currentIteration').textContent = 'Not started';
    document.getElementById('iterationDetails').innerHTML = '<p class="placeholder">Waiting for iteration to start...</p>';
    document.getElementById('actionsLog').innerHTML = '<p class="placeholder">No actions yet...</p>';
    document.getElementById('bestScraper').innerHTML = '<p class="placeholder">No best scraper selected yet...</p>';
    
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
}

function simulateScraping() {
    // This is a placeholder - in real implementation, connect to backend API
    for (let i = 1; i <= totalIterations; i++) {
        if (!isRunning) break;
        
        setTimeout(() => {
            runIteration(i);
        }, i * 2000);
    }
}

function runIteration(iterationNum) {
    currentIteration = iterationNum;
    const progress = (iterationNum / totalIterations) * 100;
    
    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('currentIteration').textContent = `Iteration ${iterationNum} of ${totalIterations}`;
    
    addLogEntry('think', `Iteration ${iterationNum}: Analyzing HTML structure...`);
    
    setTimeout(() => {
        addLogEntry('build', `Iteration ${iterationNum}: Generating scraping strategies...`);
    }, 500);
    
    setTimeout(() => {
        addLogEntry('act', `Iteration ${iterationNum}: Executing strategies and extracting data...`);
    }, 1000);
    
    setTimeout(() => {
        addLogEntry('eval', `Iteration ${iterationNum}: Evaluating results...`);
        
        // Simulate metrics
        const successRate = 0.6 + (iterationNum * 0.1) + Math.random() * 0.1;
        const completeness = 0.7 + (iterationNum * 0.05) + Math.random() * 0.1;
        const quality = 0.65 + (iterationNum * 0.08) + Math.random() * 0.1;
        
        metricsData.iterations.push(iterationNum);
        metricsData.successRates.push(successRate);
        metricsData.completeness.push(completeness);
        metricsData.quality.push(quality);
        
        updateMetricsChart();
        updateIterationDetails(iterationNum, successRate, completeness, quality);
    }, 1500);
    
    setTimeout(() => {
        addLogEntry('feedback', `Iteration ${iterationNum}: Storing results and updating patterns...`);
        
        if (iterationNum === totalIterations) {
            setTimeout(() => {
                updateBestScraper();
                isRunning = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                addLogEntry('think', 'All iterations completed! Best scraper selected.');
            }, 500);
        }
    }, 2000);
}

function addLogEntry(phase, message) {
    const log = document.getElementById('actionsLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${phase}`;
    entry.textContent = `[${phase.toUpperCase()}] ${message}`;
    
    if (log.querySelector('.placeholder')) {
        log.innerHTML = '';
    }
    
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function updateIterationDetails(iteration, successRate, completeness, quality) {
    const details = document.getElementById('iterationDetails');
    details.innerHTML = `
        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">${(successRate * 100).toFixed(1)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Completeness</div>
            <div class="metric-value">${(completeness * 100).toFixed(1)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Quality Score</div>
            <div class="metric-value">${quality.toFixed(3)}</div>
        </div>
    `;
}

function updateMetricsChart() {
    const canvas = document.getElementById('metricsChart');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (metricsData.iterations.length === 0) return;
    
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // Draw axes
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw grid
    ctx.strokeStyle = '#eee';
    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Plot success rates
    if (metricsData.successRates.length > 0) {
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        metricsData.iterations.forEach((iter, idx) => {
            const x = padding + (chartWidth / (totalIterations - 1)) * (iter - 1);
            const y = height - padding - (metricsData.successRates[idx] * chartHeight);
            
            if (idx === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
        
        // Draw points
        metricsData.iterations.forEach((iter, idx) => {
            const x = padding + (chartWidth / (totalIterations - 1)) * (iter - 1);
            const y = height - padding - (metricsData.successRates[idx] * chartHeight);
            ctx.fillStyle = '#667eea';
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, 2 * Math.PI);
            ctx.fill();
        });
    }
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Success Rate Over Iterations', width / 2, height - 10);
    
    ctx.textAlign = 'right';
    ctx.fillText('0%', padding - 10, height - padding);
    ctx.fillText('100%', padding - 10, padding + 5);
}

function updateBestScraper() {
    if (metricsData.successRates.length === 0) return;
    
    const bestIdx = metricsData.successRates.indexOf(Math.max(...metricsData.successRates));
    const bestIteration = metricsData.iterations[bestIdx];
    const bestRate = metricsData.successRates[bestIdx];
    
    document.getElementById('bestScraper').innerHTML = `
        <h3>✅ Best Scraper Selected</h3>
        <div class="strategy-details">
            <p><strong>Iteration:</strong> ${bestIteration}</p>
            <p><strong>Success Rate:</strong> ${(bestRate * 100).toFixed(1)}%</p>
            <p><strong>Completeness:</strong> ${(metricsData.completeness[bestIdx] * 100).toFixed(1)}%</p>
            <p><strong>Quality Score:</strong> ${metricsData.quality[bestIdx].toFixed(3)}</p>
        </div>
    `;
}

