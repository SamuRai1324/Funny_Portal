document.addEventListener('DOMContentLoaded', function() {
    initGlobalChat();
    initPrivateChat();
});

let chatCooldown = 0;
let cooldownInterval = null;

function initGlobalChat() {
    const chatContainer = document.getElementById('global-chat-messages');
    const chatForm = document.getElementById('global-chat-form');

    if (!chatContainer || !chatForm) return;

    scrollToBottom(chatContainer);

    chatForm.addEventListener('submit', function(e) {
        if (chatCooldown > 0) {
            e.preventDefault();
            showToast(`Подождите ${chatCooldown} секунд`, 'warning');
            return;
        }
    });

    checkCooldownStatus();

    setInterval(() => {
        refreshChat();
    }, 5000);
}

function scrollToBottom(container) {
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

async function refreshChat() {
    const chatContainer = document.getElementById('global-chat-messages');
    if (!chatContainer) return;

    try {
        const response = await fetch('/api/global_chat/messages');
        if (response.ok) {
            const messages = await response.json();
            const wasAtBottom = chatContainer.scrollHeight - chatContainer.scrollTop <= chatContainer.clientHeight + 50;

            updateChatMessages(chatContainer, messages);

            if (wasAtBottom) {
                scrollToBottom(chatContainer);
            }
        }
    } catch (error) {
        console.error('Chat refresh error:', error);
    }
}

function updateChatMessages(container, messages) {
    const currentIds = new Set(
        Array.from(container.querySelectorAll('.chat-message'))
            .map(m => m.dataset.messageId)
    );

    messages.forEach(msg => {
        if (!currentIds.has(String(msg.id))) {
            const messageEl = createChatMessageElement(msg);
            container.appendChild(messageEl);
        }
    });
}

function createChatMessageElement(msg) {
    const div = document.createElement('div');
    div.className = 'chat-message';
    div.dataset.messageId = msg.id;

    const avatarContent = msg.avatar
        ? `<img src="/uploads/${msg.avatar}" alt="">`
        : `<span>${msg.username[0].toUpperCase()}</span>`;

    div.innerHTML = `
        <div class="chat-message-avatar">${avatarContent}</div>
        <div class="chat-message-content">
            <a href="/profile/${msg.username}" class="chat-message-author">${msg.username}</a>
            <div class="chat-message-text">${escapeHtml(msg.content)}</div>
        </div>
    `;

    return div;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function startCooldown(seconds) {
    chatCooldown = seconds;
    const cooldownDisplay = document.getElementById('chat-cooldown');
    const chatInput = document.getElementById('global-chat-input');
    const chatSubmit = document.querySelector('#global-chat-form button[type="submit"]');

    if (chatInput) chatInput.disabled = true;
    if (chatSubmit) chatSubmit.disabled = true;

    if (cooldownInterval) clearInterval(cooldownInterval);

    updateCooldownDisplay();

    cooldownInterval = setInterval(() => {
        chatCooldown--;
        updateCooldownDisplay();

        if (chatCooldown <= 0) {
            clearInterval(cooldownInterval);
            if (chatInput) chatInput.disabled = false;
            if (chatSubmit) chatSubmit.disabled = false;
            if (cooldownDisplay) cooldownDisplay.style.display = 'none';
        }
    }, 1000);
}

function updateCooldownDisplay() {
    const cooldownDisplay = document.getElementById('chat-cooldown');
    if (cooldownDisplay) {
        if (chatCooldown > 0) {
            cooldownDisplay.style.display = 'block';
            cooldownDisplay.textContent = `Подождите: ${chatCooldown} сек`;
        } else {
            cooldownDisplay.style.display = 'none';
        }
    }
}

async function checkCooldownStatus() {
    try {
        const response = await fetch('/api/chat/cooldown');
        if (response.ok) {
            const data = await response.json();
            if (data.cooldown > 0) {
                startCooldown(data.cooldown);
            }
        }
    } catch (error) {
        console.error('Cooldown check error:', error);
    }
}

function initPrivateChat() {
    const messageContainer = document.getElementById('private-messages');
    if (messageContainer) {
        scrollToBottom(messageContainer);
    }

    const messageForm = document.getElementById('private-message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            const input = this.querySelector('input[name="content"]');
            if (input && !input.value.trim()) {
                e.preventDefault();
            }
        });
    }
}