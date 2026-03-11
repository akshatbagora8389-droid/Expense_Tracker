// ── Auth page logic ──────────────────────────

// Check if already logged in — redirect to dashboard
(async function checkAuth() {
    try {
        const res = await fetch('/api/auth/me');
        if (res.ok) {
            window.location.href = '/dashboard';
        }
    } catch (_) { /* not logged in */ }
})();

// Tab switching
function switchTab(tab) {
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

// Login handler
async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const errEl = document.getElementById('login-error');
    errEl.classList.remove('show');

    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    btn.innerHTML = '<span class="spinner"></span> Signing in...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        const data = await res.json();

        if (!res.ok) {
            errEl.textContent = data.error || 'Login failed';
            errEl.classList.add('show');
            btn.innerHTML = 'Sign In';
            btn.disabled = false;
            return;
        }

        window.location.href = '/dashboard';
    } catch (err) {
        errEl.textContent = 'Network error. Please try again.';
        errEl.classList.add('show');
        btn.innerHTML = 'Sign In';
        btn.disabled = false;
    }
}

// Register handler
async function handleRegister(e) {
    e.preventDefault();
    const btn = document.getElementById('register-btn');
    const errEl = document.getElementById('register-error');
    errEl.classList.remove('show');

    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;

    btn.innerHTML = '<span class="spinner"></span> Creating account...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password }),
        });
        const data = await res.json();

        if (!res.ok) {
            errEl.textContent = data.error || 'Registration failed';
            errEl.classList.add('show');
            btn.innerHTML = 'Create Account';
            btn.disabled = false;
            return;
        }

        window.location.href = '/dashboard';
    } catch (err) {
        errEl.textContent = 'Network error. Please try again.';
        errEl.classList.add('show');
        btn.innerHTML = 'Create Account';
        btn.disabled = false;
    }
}
