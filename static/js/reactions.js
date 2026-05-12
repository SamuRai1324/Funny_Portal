document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.reaction-btn');
        if (!btn) return;
        e.preventDefault();

        var postId = btn.dataset.postId;
        var type = btn.dataset.reaction;
        if (!postId || !type) return;

        reactToPost(postId, type);
    });
});

async function reactToPost(postId, type) {
    try {
        var r = await fetch('/api/react/' + postId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reaction_type: type })
        });
        if (r.ok) {
            var data = await r.json();
            var container = document.querySelector('[data-post-reactions="' + postId + '"]');
            if (!container) return;
            container.querySelectorAll('.reaction-btn').forEach(function(b) {
                var t = b.dataset.reaction;
                var countEl = b.querySelector('.reaction-count');
                b.classList.remove('active');
                if (t === data.user_reaction) {
                    b.classList.add('active');
                }
                if (countEl) {
                    countEl.textContent = data.reactions[t] || '';
                }
            });
        } else if (r.status === 401) {
            window.location.href = '/login';
        }
    } catch (e) {
        console.error('Reaction error:', e);
    }
}