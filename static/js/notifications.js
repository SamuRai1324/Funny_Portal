document.addEventListener('DOMContentLoaded', function() {
    var badge = document.querySelector('.notification-badge');
    var count = badge ? parseInt(badge.textContent) || 0 : 0;
    setInterval(async function() {
        try {
            var r = await fetch('/api/notifications/count');
            if (r.ok) {
                var d = await r.json();
                if (d.count > count && typeof showToast === 'function') showToast('Новые уведомления: ' + (d.count - count), 'info');
                count = d.count;
                if (badge) { badge.textContent = count > 99 ? '99+' : count; badge.style.display = count > 0 ? 'flex' : 'none'; }
            }
        } catch (e) {}
    }, 30000);
});