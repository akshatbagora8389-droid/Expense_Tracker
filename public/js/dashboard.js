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

// Chart color palette
const COLORS = [
    '#6366f1', '#8b5cf6', '#a78bfa', '#c084fc',
    '#10b981', '#34d399', '#3b82f6', '#60a5fa',
    '#f59e0b', '#fbbf24', '#ec4899', '#f472b6',
];

function renderIncomeChart(data) {
    const ctx = document.getElementById('income-pie-chart').getContext('2d');

    if (incomeChart) incomeChart.destroy();

    if (!data.length) {
        incomeChart = new Chart(ctx, {
            type: 'pie',
            data: { labels: ['No data'], datasets: [{ data: [1], backgroundColor: ['#1e293b'] }] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#64748b' } } }
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
                        color: '#94a3b8',
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 12,
                        font: { family: 'Inter', size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
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
            data: { labels: ['No data'], datasets: [{ data: [0], borderColor: '#1e293b' }] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.03)' } },
                    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.03)' } }
                }
            }
        });
        return;
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(239, 68, 68, 0.25)');
    gradient.addColorStop(1, 'rgba(239, 68, 68, 0.0)');

    expensesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Expenses',
                data: data.map(d => d.total),
                borderColor: '#ef4444',
                backgroundColor: gradient,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#0a0e1a',
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
                    backgroundColor: '#1e293b',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    padding: 12,
                    cornerRadius: 10,
                    callbacks: {
                        label: ctx => ` Expenses: ${formatCurrency(ctx.parsed.y)}`
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    border: { color: 'rgba(255,255,255,0.06)' }
                },
                y: {
                    ticks: {
                        color: '#64748b',
                        font: { family: 'Inter', size: 11 },
                        callback: v => formatCurrency(v)
                    },
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    border: { color: 'rgba(255,255,255,0.06)' }
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
                <div class="empty-icon">📭</div>
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
