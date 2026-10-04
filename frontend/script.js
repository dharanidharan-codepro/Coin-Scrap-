// ═══════════════════════════════════════════════
//  CryptoTracker — Main Application Script
//  Particle background, toast system, data engine
// ═══════════════════════════════════════════════

const API_URL = 'http://localhost:5000/api';
let cryptoData = [];
let allCryptos = [];

// ─── DOM Elements ───
const scrapBtn = document.getElementById('scrapBtn');
const limitInput = document.getElementById('limitInput');
const exportBtn = document.getElementById('exportBtn');
const searchInput = document.getElementById('searchInput');
const tableBody = document.getElementById('tableBody');
const gainersBody = document.getElementById('gainersBody');
const losersBody = document.getElementById('losersBody');
const searchBody = document.getElementById('searchBody');
const lastUpdate = document.getElementById('lastUpdate');
const dataCount = document.getElementById('dataCount');
const statusText = document.getElementById('statusText');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const themeToggle = document.getElementById('themeToggle');
const toastContainer = document.getElementById('toastContainer');

// ═══════════════════════════════════════════════
//  PARTICLE CANVAS ANIMATION
// ═══════════════════════════════════════════════
(function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animId;
    let mouse = { x: -999, y: -999 };

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Track mouse for interactive glow
    window.addEventListener('mousemove', e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    const COLORS = [
        'rgba(167, 139, 250, ',
        'rgba(94, 234, 212, ',
        'rgba(196, 181, 253, ',
        'rgba(125, 211, 252, ',
    ];

    class Particle {
        constructor() {
            this.reset();
        }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
            this.baseAlpha = Math.random() * 0.5 + 0.15;
            this.alpha = this.baseAlpha;
            this.pulse = Math.random() * Math.PI * 2;
            this.pulseSpeed = Math.random() * 0.02 + 0.005;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.pulse += this.pulseSpeed;
            this.alpha = this.baseAlpha + Math.sin(this.pulse) * 0.15;

            // Mouse interaction — particles glow when near cursor
            const dx = this.x - mouse.x;
            const dy = this.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                this.alpha = Math.min(1, this.alpha + (1 - dist / 150) * 0.5);
                this.size = Math.min(4, this.size + 0.02);
            }

            if (this.x < -10 || this.x > canvas.width + 10 ||
                this.y < -10 || this.y > canvas.height + 10) {
                this.reset();
            }
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color + this.alpha + ')';
            ctx.fill();

            // Glow effect
            if (this.alpha > 0.3) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
                ctx.fillStyle = this.color + (this.alpha * 0.12) + ')';
                ctx.fill();
            }
        }
    }

    // Create particles
    const count = Math.min(80, Math.floor(window.innerWidth * window.innerHeight / 15000));
    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }

    // Draw lines between close particles
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    const alpha = (1 - dist / 120) * 0.08;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(167, 139, 250, ${alpha})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        drawConnections();
        animId = requestAnimationFrame(animate);
    }
    animate();
})();

// ═══════════════════════════════════════════════
//  NAVBAR SCROLL EFFECT
// ═══════════════════════════════════════════════
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ═══════════════════════════════════════════════
//  INTERSECTION OBSERVER — reveal on scroll
// ═══════════════════════════════════════════════
const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            revealObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.summary-card').forEach(el => {
    el.classList.add('reveal-target');
    revealObserver.observe(el);
});

// ═══════════════════════════════════════════════
//  THEME SYSTEM
// ═══════════════════════════════════════════════
function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    if (themeToggle) {
        themeToggle.setAttribute('aria-pressed', String(theme === 'light'));
    }
    localStorage.setItem('theme', theme);
}

const savedTheme = localStorage.getItem('theme') || 'dark';
applyTheme(savedTheme);

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const isLight = document.body.classList.contains('light-theme');
        const nextTheme = isLight ? 'dark' : 'light';
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (document.startViewTransition && !prefersReducedMotion) {
            document.startViewTransition(() => applyTheme(nextTheme));
        } else {
            applyTheme(nextTheme);
        }
    });
}

// ═══════════════════════════════════════════════
//  TOAST NOTIFICATION SYSTEM
// ═══════════════════════════════════════════════
function showNotification(message, type = 'info') {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Auto-remove
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 350);
    }, 3500);
}

// ═══════════════════════════════════════════════
//  EVENT LISTENERS
// ═══════════════════════════════════════════════
scrapBtn.addEventListener('click', scrapData);
exportBtn.addEventListener('click', exportData);
searchInput.addEventListener('input', handleSearch);

tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        switchTab(this.dataset.tab);
    });
});

document.addEventListener('DOMContentLoaded', loadData);

// ═══════════════════════════════════════════════
//  DATA: SCRAPE
// ═══════════════════════════════════════════════
const REFRESH_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`;

async function scrapData() {
    scrapBtn.disabled = true;
    scrapBtn.innerHTML = '<span class="spinner"></span> <span>Scraping...</span>';
    setStatus('Fetching...', 'loading');

    try {
        const limitVal = (limitInput && limitInput.value) ? limitInput.value.trim() : 10;
        const payload = { limit: isNaN(Number(limitVal)) ? limitVal : Number(limitVal) };
        const response = await fetch(`${API_URL}/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            allCryptos = data.data;
            cryptoData = data.data;
            updateLastUpdate();
            populateTable(tableBody, allCryptos);
            loadAnalytics();
            showNotification('Data refreshed successfully!', 'success');
            setStatus('Live', 'live');
        } else {
            showNotification('Error scraping data', 'error');
            setStatus('Error', 'error');
        }
    } catch (error) {
        console.error('Refresh error:', error);
        showNotification('Failed to scrape. Is the API running?', 'error');
        setStatus('Offline', 'error');
    } finally {
        scrapBtn.disabled = false;
        scrapBtn.innerHTML = `${REFRESH_SVG} <span>Scrap</span>`;
    }
}

// ═══════════════════════════════════════════════
//  DATA: LOAD
// ═══════════════════════════════════════════════
async function loadData() {
    try {
        const response = await fetch(`${API_URL}/data`);
        const data = await response.json();

        if (response.ok && data.data.length > 0) {
            allCryptos = data.data;
            cryptoData = data.data;
            updateLastUpdate();
            populateTable(tableBody, allCryptos);
            dataCount.textContent = allCryptos.length;
            setStatus('Live', 'live');
        }
    } catch (error) {
        console.error('Load error:', error);
    }
}

// ═══════════════════════════════════════════════
//  DATA: ANALYTICS
// ═══════════════════════════════════════════════
async function loadAnalytics() {
    try {
        const [gainersRes, losersRes, summaryRes] = await Promise.all([
            fetch(`${API_URL}/analytics/gainers?limit=5`),
            fetch(`${API_URL}/analytics/losers?limit=5`),
            fetch(`${API_URL}/analytics/summary`)
        ]);

        const gainersData = await gainersRes.json();
        if (gainersRes.ok) populateTable(gainersBody, gainersData.data);

        const losersData = await losersRes.json();
        if (losersRes.ok) populateTable(losersBody, losersData.data);

        const summaryData = await summaryRes.json();
        if (summaryRes.ok) updateSummary(summaryData.data);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// ═══════════════════════════════════════════════
//  TABLE: POPULATE WITH STAGGER ANIMATION
// ═══════════════════════════════════════════════
function populateTable(tbody, data) {
    tbody.innerHTML = '';

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">
            <p class="empty-title">No data available</p>
            <p class="empty-desc">Refresh to load cryptocurrency data</p>
        </td></tr>`;
        return;
    }

    data.forEach((crypto, index) => {
        const change = parseFloat(crypto.change_24h);
        const changeClass = change >= 0 ? 'positive' : 'negative';
        const changeSign = change >= 0 ? '+' : '';
        const changeArrow = change >= 0 ? '↑' : '↓';
        const name = escapeHtml(crypto.name || '-');
        const symbol = escapeHtml(crypto.symbol || '-');
        const logoUrl = getCoinLogoUrl(crypto.image_url);
        const logo = logoUrl
            ? `<img src="${escapeHtml(logoUrl)}" alt="${name} logo" loading="lazy" decoding="async">`
            : '';

        const row = document.createElement('tr');
        row.className = 'fade-up';
        row.style.animationDelay = `${index * 0.04}s`;

        row.innerHTML = `
            <td class="rank">${escapeHtml(crypto.rank || '-')}</td>
            <td>
                <div class="crypto-name-cell">
                    <div class="crypto-avatar" style="--hue: ${(index * 47) % 360}" aria-hidden="true">
                        ${logo}
                        <span>${escapeHtml((crypto.symbol || '?').charAt(0))}</span>
                    </div>
                    <div>
                        <div class="name">${name}</div>
                        <div class="symbol">${symbol}</div>
                    </div>
                </div>
            </td>
            <td class="price">${escapeHtml(crypto.price || '-')}</td>
            <td>
                <div class="change ${changeClass}">
                    <span class="change-arrow">${changeArrow}</span>
                    ${changeSign}${escapeHtml(crypto.change_24h || '-')}
                </div>
            </td>
            <td class="market-cap">${escapeHtml(crypto.market_cap || '-')}</td>
        `;

        // Highlight matching search
        const query = (searchInput && searchInput.value) ? searchInput.value.trim().toLowerCase() : '';
        if (query && ((crypto.name && crypto.name.toLowerCase().includes(query)) || (crypto.symbol && crypto.symbol.toLowerCase().includes(query)))) {
            row.classList.add('highlight');
        }

        tbody.appendChild(row);
    });

    if (tbody.id === 'tableBody') {
        dataCount.textContent = data.length;
    }
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[character]);
}

function getCoinLogoUrl(value) {
    if (typeof value !== 'string' || !value) return '';

    try {
        const url = new URL(value);
        return url.protocol === 'https:' &&
            (url.hostname === 'coingecko.com' || url.hostname.endsWith('.coingecko.com'))
            ? url.href
            : '';
    } catch (error) {
        return '';
    }
}

// ═══════════════════════════════════════════════
//  SUMMARY: UPDATE CARDS WITH COUNT-UP
// ═══════════════════════════════════════════════
function updateSummary(summary) {
    animateValue('totalMarketCap', summary.total_market_cap || '—');
    animateValue('avgPrice', summary.avg_price || '—');
    animateValue('avgChange', summary.avg_24h_change || '—');
    animateValue('positiveCount', summary.positive_change_count || 0);
}

function animateValue(elementId, value) {
    const el = document.getElementById(elementId);
    if (!el) return;

    // Flash animation on value change
    el.classList.add('value-flash');
    el.textContent = value;
    setTimeout(() => el.classList.remove('value-flash'), 600);
}

// ═══════════════════════════════════════════════
//  SEARCH
// ═══════════════════════════════════════════════
let searchTimeout;
async function handleSearch(e) {
    const query = e.target.value.trim();

    clearTimeout(searchTimeout);

    if (query.length === 0) {
        switchTab('all');
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                populateTable(searchBody, data.data);
                switchTab('search');
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

// ═══════════════════════════════════════════════
//  EXPORT
// ═══════════════════════════════════════════════
const EXPORT_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;

async function exportData() {
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<span class="spinner"></span> <span>Exporting...</span>';

    try {
        const response = await fetch(`${API_URL}/export`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `crypto_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('CSV exported successfully!', 'success');
        } else {
            showNotification('No data to export', 'warning');
        }
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Export failed', 'error');
    } finally {
        exportBtn.disabled = false;
        exportBtn.innerHTML = `${EXPORT_SVG} <span>Export CSV</span>`;
    }
}

// ═══════════════════════════════════════════════
//  TAB SWITCHING
// ═══════════════════════════════════════════════
function switchTab(tabName) {
    tabContents.forEach(tab => tab.classList.remove('active'));
    tabBtns.forEach(btn => btn.classList.remove('active'));

    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) tabElement.classList.add('active');

    const btnElement = document.querySelector(`[data-tab="${tabName}"]`);
    if (btnElement) btnElement.classList.add('active');

    if (tabName !== 'search') {
        searchInput.value = '';
    }
}

// ═══════════════════════════════════════════════
//  STATUS HELPERS
// ═══════════════════════════════════════════════
function updateLastUpdate() {
    const now = new Date();
    lastUpdate.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function setStatus(text, state) {
    if (statusText) statusText.textContent = text;

    const dot = document.querySelector('.pulse-dot');
    const navDot = document.querySelector('.status-dot');
    if (dot) {
        dot.style.background = state === 'live' ? 'var(--success)' :
                               state === 'error' ? 'var(--danger)' :
                               'var(--warning)';
        dot.style.boxShadow = state === 'live' ? '0 0 8px rgba(34,197,94,0.5)' :
                               state === 'error' ? '0 0 8px rgba(239,68,68,0.5)' :
                               '0 0 8px rgba(245,158,11,0.5)';
    }
    if (navDot) {
        navDot.style.background = dot ? dot.style.background : '';
        navDot.style.boxShadow = dot ? dot.style.boxShadow : '';
    }
}

// ═══════════════════════════════════════════════
//  CARD TILT EFFECT (3D hover)
// ═══════════════════════════════════════════════
document.querySelectorAll('.summary-card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / 12;
        const rotateY = (centerX - x) / 12;

        card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});

// Auto-load analytics on page load
loadAnalytics();
