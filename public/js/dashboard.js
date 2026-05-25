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

function renderRecentTransactions(data) {
    const tbody = document.getElementById('recent-tbody');

    if (!data.length) {
        tbody.innerHTML = `
            <tr><td colspan="4" class="empty-state" style="padding:40px">
                <div class="empty-icon" style="margin-bottom: 12px;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted)">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                </div>
                <h3>No transactions yet</h3>
                <p>Add income or expenses to see them here</p>
            </td></tr>`;
        return;
    }

    tbody.innerHTML = data.map(t => `
        <tr>
            <td><span class="badge badge-${t.type === 'income' ? 'income' : 'expense'}">${t.type}</span></td>
            <td>${t.label}</td>
            <td class="amount ${t.type === 'income' ? 'income-amount' : 'expense-amount'}">
                ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
            </td>
            <td>${t.date}</td>
        </tr>
    `).join('');
}

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard/summary');
        if (!res.ok) throw new Error('Failed to load');
        const data = await res.json();

        document.getElementById('total-income').textContent = formatCurrency(data.total_income);
        document.getElementById('total-expenses').textContent = formatCurrency(data.total_expenses);
        document.getElementById('balance').textContent = formatCurrency(data.balance);

        renderIncomeChart(data.income_by_source);
        renderExpensesChart(data.expenses_over_time);
        renderRecentTransactions(data.recent_transactions);
    } catch (err) {
        showToast('Failed to load dashboard data', 'error');
    }
}

// Init
(async function () {
    const user = await checkAuth();
    if (!user) return;

    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();

    loadDashboard();
})();
