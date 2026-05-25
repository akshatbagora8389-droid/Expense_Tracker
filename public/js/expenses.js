// ── Expenses page logic ──────────────────────────

async function checkAuth() {
    try {
        const res = await fetch('/api/auth/me');
        if (!res.ok) { window.location.href = '/'; return null; }
        return await res.json();
    } catch { window.location.href = '/'; return null; }
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

async function loadExpenses() {
    try {
        const res = await fetch('/api/expenses');
        if (!res.ok) throw new Error();
        const data = await res.json();
        renderExpensesTable(data);
    } catch {
        showToast('Failed to load expense data', 'error');
    }
}

function renderExpensesTable(data) {
    const tbody = document.getElementById('expenses-tbody');

    if (!data.length) {
        tbody.innerHTML = `
            <tr><td colspan="5">
                <div class="empty-state" style="padding: 40px;">
                    <div class="empty-icon" style="margin-bottom: 12px;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted)">
                            <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                        </svg>
                    </div>
                    <h3>No expenses yet</h3>
                    <p>Add your first expense entry on the left</p>
                </div>
            </td></tr>`;
        return;
    }

    tbody.innerHTML = data.map(item => `
        <tr>
            <td><span class="badge-cat badge-cat-${item.category.toLowerCase()}">${item.category}</span></td>
            <td class="amount expense-amount">-${formatCurrency(item.amount)}</td>
            <td>${item.date}</td>
            <td>${item.description || '—'}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteExpense(${item.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;">
                        <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
                    </svg>
                    Delete
                </button>
            </td>
        </tr>
    `).join('');
}

async function handleAddExpense(e) {
    e.preventDefault();
    const btn = document.getElementById('add-expense-btn');
    const errEl = document.getElementById('expense-form-error');
    errEl.classList.remove('show');

    const category = document.getElementById('expense-category').value;
    const amount = parseFloat(document.getElementById('expense-amount').value);
    const date = document.getElementById('expense-date').value;
    const description = document.getElementById('expense-desc').value.trim();

    btn.innerHTML = '<span class="spinner"></span> Adding...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, amount, date, description }),
        });
        const data = await res.json();

        if (!res.ok) {
            errEl.textContent = data.error;
            errEl.classList.add('show');
        } else {
            showToast('Expense added successfully!');
            document.getElementById('add-expense-form').reset();
            loadExpenses();
        }
    } catch {
        errEl.textContent = 'Network error';
        errEl.classList.add('show');
    }

    btn.innerHTML = 'Add Expense';
    btn.disabled = false;
}

async function deleteExpense(id) {
    if (!confirm('Delete this expense entry?')) return;
    try {
        const res = await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Expense deleted');
            loadExpenses();
        }
    } catch {
        showToast('Failed to delete', 'error');
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
    // Set default date to today
    document.getElementById('expense-date').valueAsDate = new Date();
    loadExpenses();
})();
