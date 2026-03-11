// ── AI Advisor Chat Logic ────────────────────

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

// ── Chat functions ───────────────────────────

let isWaiting = false;

function appendMessage(role, html) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = `chat-avatar ${role}-avatar`;
    avatar.textContent = role === 'bot' ? '🤖' : document.getElementById('user-avatar').textContent;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}-bubble`;
    bubble.innerHTML = html;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    container.appendChild(msgDiv);

    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
    return bubble;
}

function showTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message bot';
    msgDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar bot-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble bot-bubble typing-bubble';
    bubble.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

function formatBotReply(text) {
    // Convert markdown-like formatting to HTML
    let html = text;

    // Bold: **text** or __text__
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // Italic: *text* or _text_
    html = html.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // Bullet points: lines starting with - or *
    html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    // Clean up nested <ul> tags
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Numbered lists: lines starting with 1. 2. etc
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

    // Headings
    html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');

    // Line breaks: double newlines to paragraphs
    html = html.split('\n\n').map(p => {
        p = p.trim();
        if (!p) return '';
        // Don't wrap if it already starts with an HTML tag
        if (/^<(ul|ol|li|h[1-6]|p|div|table)/.test(p)) return p;
        return `<p>${p}</p>`;
    }).join('');

    // Single newlines within paragraphs
    html = html.replace(/(?<!<\/li>|<\/ul>|<\/ol>|<\/h[1-6]>|<\/p>)\n(?!<)/g, '<br>');

    return html;
}

async function sendMessage() {
    if (isWaiting) return;

    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Hide suggestions after first message
    const suggestionsEl = document.getElementById('chat-suggestions');
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    // Show user message
    appendMessage('user', `<p>${message.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>`);
    input.value = '';

    // Show typing indicator
    isWaiting = true;
    document.getElementById('chat-send-btn').classList.add('disabled');
    showTypingIndicator();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        removeTypingIndicator();

        if (!res.ok) {
            const err = await res.json();
            appendMessage('bot', `<p class="error-text">⚠️ ${err.error || 'Something went wrong. Please try again.'}</p>`);
        } else {
            const data = await res.json();
            const formattedReply = formatBotReply(data.reply);
            appendMessage('bot', formattedReply);
        }
    } catch (err) {
        removeTypingIndicator();
        appendMessage('bot', '<p class="error-text">⚠️ Network error. Please check your connection.</p>');
    }

    isWaiting = false;
    document.getElementById('chat-send-btn').classList.remove('disabled');
    input.focus();
}

function sendSuggestion(btn) {
    const input = document.getElementById('chat-input');
    // Remove emoji prefix for cleaner query
    input.value = btn.textContent.replace(/^[\u{1F000}-\u{1FFFF}]\s*/u, '').trim();
    sendMessage();
}

// ── Init ─────────────────────────────────────

(async function () {
    const user = await checkAuth();
    if (!user) return;

    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
})();
