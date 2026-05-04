document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reaction-btn').forEach(function(btn) {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            var postId = this.dataset.postId;
            var type = this.dataset.reaction;
            if (!postId || !type) return;
            try {
                var r = await fetch('/api/react/' + postId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reaction_type: type })
                });
                if (r.ok) {
                    var data = await r.json();
                    var container = document.querySelector('[data-post-reactions="' + postId + '"]');
                    if (container) {
                        container.querySelectorAll('.reaction-btn').forEach(function(b) {
                            var t = b.dataset.reaction;
                            var count = b.querySelector('.reaction-count');
                            b.classList.remove('active');
                            if (t === type && (data.action === 'added' || data.action === 'changed')) b.classList.add('active');
                            if (count) count.textContent = data.reactions[t] || '';
                        });
                    }
                } else if (r.status === 401) {
                    window.location.href = '/login';
                }
            } catch (e) {}
        });
    });
});