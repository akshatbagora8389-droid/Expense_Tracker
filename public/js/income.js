// ── Income page logic ──────────────────────────

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

async function loadIncome() {
    try {
        const res = await fetch('/api/income');
        if (!res.ok) throw new Error();
        const data = await res.json();
        renderIncomeTable(data);
    } catch {
        showToast('Failed to load income data', 'error');
    }
}

function renderIncomeTable(data) {
    const tbody = document.getElementById('income-tbody');

    if (!data.length) {
        tbody.innerHTML = `
            <tr><td colspan="5">
                <div class="empty-state">
                    <div class="empty-icon">💵</div>
                    <h3>No income yet</h3>
                    <p>Add your first income entry above</p>
                </div>
            </td></tr>`;
        return;
    }

    tbody.innerHTML = data.map(item => `
        <tr>
            <td><strong>${item.source}</strong></td>
            <td class="amount income-amount">+${formatCurrency(item.amount)}</td>
            <td>${item.date}</td>
            <td>${item.description || '—'}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteIncome(${item.id})">🗑️ Delete</button>
            </td>
        </tr>
    `).join('');
}

async function handleAddIncome(e) {
    e.preventDefault();
    const btn = document.getElementById('add-income-btn');
    const errEl = document.getElementById('income-form-error');
    errEl.classList.remove('show');

    const source = document.getElementById('income-source').value.trim();
    const amount = parseFloat(document.getElementById('income-amount').value);
    const date = document.getElementById('income-date').value;
    const description = document.getElementById('income-desc').value.trim();

    btn.innerHTML = '<span class="spinner"></span> Adding...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/income', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, amount, date, description }),
        });
        const data = await res.json();

        if (!res.ok) {
            errEl.textContent = data.error;
            errEl.classList.add('show');
        } else {
            showToast('Income added successfully!');
            document.getElementById('add-income-form').reset();
            loadIncome();
        }
    } catch {
        errEl.textContent = 'Network error';
        errEl.classList.add('show');
    }

    btn.innerHTML = '➕ Add Income';
    btn.disabled = false;
}

async function deleteIncome(id) {
    if (!confirm('Delete this income entry?')) return;
    try {
        const res = await fetch(`/api/income/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Income deleted');
            loadIncome();
        }
    } catch {
        showToast('Failed to delete', 'error');
    }
}

// Init
(async function () {
    const user = await checkAuth();
    if (!user) return;
    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
    // Set default date to today
    document.getElementById('income-date').valueAsDate = new Date();
    loadIncome();
})();
