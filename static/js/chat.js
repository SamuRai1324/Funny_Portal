document.addEventListener('DOMContentLoaded', function() {
    initGlobalChat();
    initPrivateChat();
});

var chatCooldown = 0;
var cooldownInterval = null;

function initGlobalChat() {
    var container = document.getElementById('global-chat-messages');
    var form = document.getElementById('global-chat-form');
    if (!container || !form) return;
    scrollToBottom(container);
    form.addEventListener('submit', function(e) {
        if (chatCooldown > 0) { e.preventDefault(); showToast('Подождите ' + chatCooldown + ' сек', 'warning'); }
    });
    checkCooldownStatus();
    setInterval(refreshChat, 5000);
}

function scrollToBottom(c) { if (c) c.scrollTop = c.scrollHeight; }

async function refreshChat() {
    var c = document.getElementById('global-chat-messages');
    if (!c) return;
    try {
        var r = await fetch('/api/global_chat/messages');
        if (r.ok) {
            var msgs = await r.json();
            var atBottom = c.scrollHeight - c.scrollTop <= c.clientHeight + 50;
            var ids = new Set(Array.from(c.querySelectorAll('.chat-message')).map(function(m) { return m.dataset.messageId; }));
            msgs.forEach(function(msg) {
                if (!ids.has(String(msg.id))) {
                    var d = document.createElement('div');
                    d.className = 'chat-message';
                    d.dataset.messageId = msg.id;
                    var av = msg.avatar ? '<img src="/uploads/' + msg.avatar + '">' : '<span>' + msg.username[0].toUpperCase() + '</span>';
                    d.innerHTML = '<div class="chat-message-avatar">' + av + '</div><div class="chat-message-content"><a href="/profile/' + msg.username + '" class="chat-message-author">' + msg.username + '</a><div class="chat-message-text">' + escapeHtmlChat(msg.content) + '</div></div>';
                    c.appendChild(d);
                }
            });
            if (atBottom) scrollToBottom(c);
        }
    } catch (e) {}
}

function escapeHtmlChat(t) { var d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

function startCooldown(s) {
    chatCooldown = s;
    var display = document.getElementById('chat-cooldown');
    var input = document.getElementById('global-chat-input');
    var submit = document.querySelector('#global-chat-form button[type="submit"]');
    if (input) input.disabled = true;
    if (submit) submit.disabled = true;
    if (cooldownInterval) clearInterval(cooldownInterval);
    updateCooldownDisplay();
    cooldownInterval = setInterval(function() {
        chatCooldown--;
        updateCooldownDisplay();
        if (chatCooldown <= 0) {
            clearInterval(cooldownInterval);
            if (input) input.disabled = false;
            if (submit) submit.disabled = false;
            if (display) display.style.display = 'none';
        }
    }, 1000);
}

function updateCooldownDisplay() {
    var d = document.getElementById('chat-cooldown');
    if (d) { d.style.display = chatCooldown > 0 ? 'block' : 'none'; d.textContent = 'Подождите: ' + chatCooldown + ' сек'; }
}

async function checkCooldownStatus() {
    try {
        var r = await fetch('/api/chat/cooldown');
        if (r.ok) { var d = await r.json(); if (d.cooldown > 0) startCooldown(d.cooldown); }
    } catch (e) {}
}

function initPrivateChat() {
    var c = document.getElementById('private-messages');
    if (c) scrollToBottom(c);
}