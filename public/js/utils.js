// ── Shared Utility Helpers for ExpenseIQ ────────────────────────

/**
 * Check if user is authenticated. Redirects to landing page if not.
 */
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

/**
 * Log out user and redirect to landing page.
 */
async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (err) {
        console.error('Error during logout:', err);
    } finally {
        window.location.href = '/';
    }
}

/**
 * Show toast notification.
 */
function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className = 'toast show ' + type;
    setTimeout(() => t.classList.remove('show'), 3000);
}

/**
 * Format number to Indian Currency (INR) format.
 */
function formatCurrency(n) {
    return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

/**
 * Format displaying username by removing email domain and capitalization.
 */
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

// ── Responsive Sidebar Toggle Drawer ───────────────
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('sidebar-toggle-btn');
    const collapseBtn = document.getElementById('sidebar-collapse-btn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    const toggleSidebar = () => {
        if (window.innerWidth >= 768) {
            // Desktop collapse mode
            document.body.classList.toggle('sidebar-collapsed');
        } else {
            // Mobile slide drawer mode
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        }
    };

    if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
    if (collapseBtn) collapseBtn.addEventListener('click', toggleSidebar);
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
        });
    }
});
