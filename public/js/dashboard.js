// ── Dashboard logic ──────────────────────────

let incomeChart = null;
let expensesChart = null;

// Auth guard
async function checkAuth() {
    try {
        const res = await fetch('/api/auth/me');
        if (!res.ok) {
            window.location.href = '/';
            return null;
        }
        return await res.json();
    } catch {
        window.location.href = '/';
        return null;
    }
}

async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
}

function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show ' + type;
    setTimeout(() => t.classList.remove('show'), 3000);
}

function formatCurrency(n) {
    return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

// Chart color palette matching warm minimal beige & organic green theme
const COLORS = [
    '#2D6A4F', // Forest Green (Income/Primary)
    '#40916C', // Medium Sea Green
    '#52B788', // Light Sage Green
    '#74C69D', // Soft Mint
    '#D97706', // Warm Amber
    '#B45309', // Dark Clay Amber
    '#CA6702', // Ochre / Copper
    '#9C6644', // Slate Espresso
    '#DDB892', // Sand
    '#57C5B6', // Soft Teal
    '#1A5F7A'  // Deep Ocean Blue
];

function renderIncomeChart(data) {
    const ctx = document.getElementById('income-pie-chart').getContext('2d');

    if (incomeChart) incomeChart.destroy();

    if (!data.length) {
        incomeChart = new Chart(ctx, {
            type: 'pie',
            data: { labels: ['No data'], datasets: [{ data: [1], backgroundColor: ['#F3ECE2'] }] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { 
                        labels: { 
                            color: '#70655C',
                            font: { family: 'Plus Jakarta Sans', size: 12 }
                        } 
                    } 
                }
            }
        });
        return;
    }

    incomeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.source),
            datasets: [{
                data: data.map(d => d.total),
                backgroundColor: COLORS.slice(0, data.length),
                borderWidth: 0,
                hoverOffset: 12,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#70655C',
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 12,
                        font: { family: 'Plus Jakarta Sans', size: 12, weight: '500' }
                    }
                },
                tooltip: {
                    backgroundColor: '#2C2520',
                    titleColor: '#FAF8F5',
                    bodyColor: '#F3ECE2',
                    padding: 12,
                    cornerRadius: 10,
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`
                    }
                }
            }
        }
    });
}

function renderExpensesChart(data) {
    const ctx = document.getElementById('expenses-line-chart').getContext('2d');

    if (expensesChart) expensesChart.destroy();

    if (!data.length) {
        expensesChart = new Chart(ctx, {
            type: 'line',
            data: { labels: ['No data'], datasets: [{ data: [0], borderColor: '#F3ECE2' }] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#70655C' }, grid: { color: 'rgba(44, 37, 32, 0.05)' } },
                    y: { ticks: { color: '#70655C' }, grid: { color: 'rgba(44, 37, 32, 0.05)' } }
                }
            }
        });
        return;
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(180, 83, 9, 0.15)'); // Warm Amber/Clay gradient fill
    gradient.addColorStop(1, 'rgba(180, 83, 9, 0.0)');

    expensesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Expenses',
                data: data.map(d => d.total),
                borderColor: '#B45309', // Warm Amber/Clay for expenses line
                backgroundColor: gradient,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#B45309',
                pointBorderColor: '#FFFFFF', // Clean border matching card background
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#2C2520',
                    titleColor: '#FAF8F5',
                    bodyColor: '#F3ECE2',
                    padding: 12,
                    cornerRadius: 10,
                    callbacks: {
                        label: ctx => ` Expenses: ${formatCurrency(ctx.parsed.y)}`
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#70655C', font: { family: 'Plus Jakarta Sans', size: 11 } },
                    grid: { color: 'rgba(44, 37, 32, 0.04)' },
                    border: { color: 'rgba(44, 37, 32, 0.06)' }
                },
                y: {
                    ticks: {
                        color: '#70655C',
                        font: { family: 'Plus Jakarta Sans', size: 11 },
                        callback: v => formatCurrency(v)
                    },
                    grid: { color: 'rgba(44, 37, 32, 0.04)' },
                    border: { color: 'rgba(44, 37, 32, 0.06)' }
                }
            }
        }
    });
}

function getTransactionIcon(type, label) {
    if (type === 'income') return 'payments';
    const cleanLabel = label.toLowerCase();
    const icons = {
        'food': 'restaurant',
        'lifestyle': 'sports_esports',
        'shopping': 'shopping_bag',
        'bills': 'receipt',
        'entertainment': 'movie',
        'health': 'medical_services',
        'education': 'school',
        'rent': 'home',
        'transport': 'directions_car',
        'salary': 'work',
        'freelance': 'laptop_mac'
    };
    for (const [key, value] of Object.entries(icons)) {
        if (cleanLabel.includes(key)) return value;
    }
    return 'receipt_long';
}

function formatRecentActivityDate(dateStr) {
    if (!dateStr) return '';
    try {
        const parts = dateStr.split('-');
        if (parts.length !== 3) return dateStr;
        const d = new Date(parts[0], parts[1] - 1, parts[2]);
        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(today.getDate() - 1);
        
        if (d.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (d.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        } else {
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }
    } catch {
        return dateStr;
    }
}

function capitalizeFirstLetter(str) {
    if (!str) return '';
    return str.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
}

function renderRecentTransactions(data) {
    const container = document.getElementById('recent-activity-list');

    if (!data.length) {
        container.innerHTML = `
            <div class="text-center py-8 text-on-surface-variant flex flex-col items-center justify-center gap-3">
                <span class="material-symbols-outlined text-[36px] text-outline/50">receipt_long</span>
                <p class="font-bold">No transactions yet</p>
                <p class="text-[12px] text-outline">Add transactions to see them here</p>
            </div>`;
        return;
    }

    container.innerHTML = data.map(t => {
        const icon = getTransactionIcon(t.type, t.label);
        const isIncome = t.type === 'income';
        const formattedLabel = capitalizeFirstLetter(t.label);
        const formattedDate = formatRecentActivityDate(t.date);
        const badgeBg = isIncome ? 'bg-primary/10 text-primary' : 'bg-secondary/10 text-secondary';
        const amtClass = isIncome ? 'text-primary' : 'text-secondary';
        const amtPrefix = isIncome ? '+' : '-';
        
        return `
            <div class="flex items-center justify-between group cursor-pointer p-3 rounded-xl hover:bg-surface-container-high/40 hover:translate-x-1 transition-all duration-200">
                <div class="flex items-center gap-4">
                    <div class="w-11 h-11 ${badgeBg} rounded-full flex items-center justify-center transition-transform duration-200 group-hover:scale-105">
                        <span class="material-symbols-outlined text-[20px]">${icon}</span>
                    </div>
                    <div>
                        <p class="font-body-lg font-bold text-on-surface group-hover:text-primary transition-colors">${formattedLabel}</p>
                        <p class="text-body-sm text-on-surface-variant flex items-center gap-2 mt-0.5">
                            <span class="inline-block w-1.5 h-1.5 rounded-full ${isIncome ? 'bg-primary' : 'bg-secondary'}"></span>
                            <span class="capitalize">${t.type}</span>
                            <span class="text-outline/40">•</span>
                            <span>${formattedDate}</span>
                        </p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-body-lg font-extrabold ${amtClass} tracking-tight">${amtPrefix}${formatCurrency(t.amount)}</p>
                </div>
            </div>
        `;
    }).join('');
}

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard/summary');
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.error || 'Failed to load dashboard data');
        }
        const data = await res.json();

        document.getElementById('total-income').textContent = formatCurrency(data.total_income);
        document.getElementById('total-expenses').textContent = formatCurrency(data.total_expenses);
        document.getElementById('balance').textContent = formatCurrency(data.balance);

        renderIncomeChart(data.income_by_source);
        renderExpensesChart(data.expenses_over_time);
        renderRecentTransactions(data.recent_transactions);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function formatDisplayName(name) {
    if (!name) return 'USER';
    let clean = name.split('@')[0];
    if (clean.toLowerCase().includes('akshat') && clean.toLowerCase().includes('bagora')) {
        return 'Akshat Bagora';
    }
    if (clean.toLowerCase().includes('harshita') && clean.toLowerCase().includes('agrawal')) {
        return 'Harshita Agrawal';
    }
    let split = clean.replace(/([a-z])([A-Z])/g, '$1 $2');
    return split;
}

// Init
(async function () {
    const user = await checkAuth();
    if (!user) return;

    const displayName = formatDisplayName(user.username);
    document.getElementById('user-name').textContent = displayName;
    document.getElementById('user-avatar').textContent = displayName.charAt(0).toUpperCase();
    const topAvatar = document.getElementById('top-avatar');
    if (topAvatar) {
        topAvatar.textContent = displayName.charAt(0).toUpperCase();
    }
    document.getElementById('card-holder').textContent = displayName;

    loadDashboard();
})();
