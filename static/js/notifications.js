document.addEventListener('DOMContentLoaded', function() {
    var badge = document.querySelector('.notification-badge');
    var count = 0;

    if (badge) {
        count = parseInt(badge.textContent) || 0;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    setInterval(async function() {
        try {
            var r = await fetch('/api/notifications/count');
            if (!r.ok) return;
            var d = await r.json();
            if (d.count > count && typeof showToast === 'function') {
                showToast('Новое уведомление!', 'info');
            }
            count = d.count;

            // обновляем все бейджи уведомлений
            document.querySelectorAll('.notification-badge').forEach(function(b) {
                b.textContent = count > 99 ? '99+' : count;
                b.style.display = count > 0 ? 'inline-flex' : 'none';
            });
        } catch (e) {}
    }, 30000);
});