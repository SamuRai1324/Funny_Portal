document.addEventListener('DOMContentLoaded', function() {
    initNotifications();
});

let notificationCount = 0;

function initNotifications() {
    updateNotificationBadge();
    
    setInterval(checkNewNotifications, 30000);
}

async function checkNewNotifications() {
    try {
        const response = await fetch('/api/notifications/count');
        if (response.ok) {
            const data = await response.json();
            if (data.count > notificationCount) {
                showNewNotificationToast(data.count - notificationCount);
            }
            notificationCount = data.count;
            updateNotificationBadge(data.count);
        }
    } catch (error) {
        console.error('Notification check error:', error);
    }
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

function showNewNotificationToast(count) {
    if (typeof showToast === 'function') {
        showToast(`У вас ${count} новых уведомлений`, 'info');
    }
}

async function markAllAsRead() {
    try {
        const response = await fetch('/api/notifications/read-all', {
            method: 'POST'
        });
        if (response.ok) {
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
            });
            updateNotificationBadge(0);
        }
    } catch (error) {
        console.error('Mark as read error:', error);
    }
}