document.addEventListener('DOMContentLoaded', function() {
    initDropdowns();
    initModals();
    initFileUploads();
    initScrollToTop();
    initLocalTime();
    initReadMore();
    initSlideshows();
    initShareButtons();
    initQuillEditors();
});

function initDropdowns() {
    document.querySelectorAll('.dropdown').forEach(function(d) {
        d.addEventListener('click', function(e) {
            e.stopPropagation();
            var isActive = this.classList.contains('active');
            // закрываем все
            document.querySelectorAll('.dropdown.active').forEach(function(dd) { dd.classList.remove('active'); });
            if (!isActive) this.classList.add('active');
        });
    });
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown.active').forEach(function(d) { d.classList.remove('active'); });
    });
}

function initModals() {
    document.querySelectorAll('[data-modal]').forEach(function(t) {
        t.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var m = document.getElementById(this.dataset.modal);
            if (m) { m.classList.add('active'); document.body.style.overflow = 'hidden'; }
        });
    });
    document.querySelectorAll('.modal-overlay').forEach(function(o) {
        o.addEventListener('mousedown', function(e) {
            if (e.target === this) closeModal(this);
        });
    });
    document.querySelectorAll('.modal-close').forEach(function(b) {
        b.addEventListener('click', function() {
            var m = this.closest('.modal-overlay');
            if (m) closeModal(m);
        });
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(closeModal);
        }
    });
}

function closeModal(m) {
    m.classList.remove('active');
    document.body.style.overflow = '';
}

function initFileUploads() {
    document.querySelectorAll('.file-upload').forEach(function(u) {
        var input = u.querySelector('input[type="file"]');
        if (!input) return;
        var preview = u.querySelector('.file-preview');
        var text = u.querySelector('.file-upload-text');

        u.addEventListener('click', function(e) {
            if (e.target !== input) input.click();
        });
        u.addEventListener('dragover', function(e) { e.preventDefault(); u.classList.add('dragover'); });
        u.addEventListener('dragleave', function() { u.classList.remove('dragover'); });
        u.addEventListener('drop', function(e) {
            e.preventDefault();
            u.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                handleFileSelect(input, preview, text);
            }
        });
        input.addEventListener('change', function() { handleFileSelect(input, preview, text); });
    });
}

function handleFileSelect(input, preview, text) {
    var files = Array.from(input.files);
    if (!files.length) return;
    if (text) text.textContent = files.length === 1 ? files[0].name : files.length + ' файлов';
    if (preview) {
        preview.innerHTML = '';
        files.forEach(function(f) {
            if (f.type.startsWith('image/')) {
                var img = document.createElement('img');
                img.src = URL.createObjectURL(f);
                img.style.cssText = 'max-width:100%;max-height:200px;border-radius:8px;margin-top:8px;display:block;margin-left:auto;margin-right:auto;object-fit:contain;';
                preview.appendChild(img);
            } else if (f.type.startsWith('video/')) {
                var v = document.createElement('video');
                v.src = URL.createObjectURL(f);
                v.controls = true;
                v.style.cssText = 'max-width:100%;max-height:200px;border-radius:8px;margin-top:8px;';
                preview.appendChild(v);
            } else if (f.type.startsWith('audio/')) {
                var a = document.createElement('audio');
                a.src = URL.createObjectURL(f);
                a.controls = true;
                a.style.cssText = 'width:100%;margin-top:8px;';
                preview.appendChild(a);
            }
        });
    }
}

function initScrollToTop() {
    var btn = document.createElement('button');
    btn.innerHTML = '↑';
    btn.title = 'Наверх';
    btn.style.cssText = 'position:fixed;bottom:20px;right:20px;width:44px;height:44px;border-radius:50%;background:var(--accent-gradient);border:none;color:white;font-size:1.3rem;cursor:pointer;opacity:0;visibility:hidden;transition:all 0.3s;z-index:999;box-shadow:var(--shadow-md);';
    document.body.appendChild(btn);
    window.addEventListener('scroll', function() {
        var show = window.scrollY > 300;
        btn.style.opacity = show ? '1' : '0';
        btn.style.visibility = show ? 'visible' : 'hidden';
    });
    btn.addEventListener('click', function() { window.scrollTo({ top: 0, behavior: 'smooth' }); });
}

function initLocalTime() {
    document.querySelectorAll('[data-utc]').forEach(function(el) {
        var s = el.dataset.utc;
        if (!s) return;
        var d = new Date(s.includes('Z') ? s : s + 'Z');
        if (isNaN(d.getTime())) return;
        var diff = Math.floor((new Date() - d) / 1000);
        if (diff < 60) el.textContent = 'сейчас';
        else if (diff < 3600) el.textContent = Math.floor(diff / 60) + ' мин назад';
        else if (diff < 86400) el.textContent = Math.floor(diff / 3600) + ' ч назад';
        else if (diff < 604800) el.textContent = Math.floor(diff / 86400) + ' д назад';
        else el.textContent = d.toLocaleDateString('ru-RU', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    });
}

function initReadMore() {
    document.querySelectorAll('.read-more-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var card = this.closest('.post-card') || this.closest('.post-content');
            if (!card) return;
            var text = card.querySelector('.post-text');
            if (!text) return;
            if (text.classList.contains('truncated')) {
                text.classList.remove('truncated');
                text.classList.add('expanded');
                this.textContent = 'Свернуть ↑';
            } else {
                text.classList.add('truncated');
                text.classList.remove('expanded');
                this.textContent = 'Читать далее ↓';
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    });
}

function initSlideshows() {
    document.querySelectorAll('.slideshow').forEach(function(ss) {
        var track = ss.querySelector('.slideshow-track');
        var slides = ss.querySelectorAll('.slideshow-slide');
        var prev = ss.querySelector('.slideshow-prev');
        var next = ss.querySelector('.slideshow-next');
        var dots = ss.querySelectorAll('.slideshow-dot');
        var current = 0;
        var total = slides.length;
        if (total <= 1) return;

        function goTo(i) {
            if (i < 0) i = total - 1;
            if (i >= total) i = 0;
            current = i;
            track.style.transform = 'translateX(-' + (current * 100) + '%)';
            dots.forEach(function(d, idx) { d.classList.toggle('active', idx === current); });
        }

        if (prev) prev.addEventListener('click', function(e) { e.stopPropagation(); goTo(current - 1); });
        if (next) next.addEventListener('click', function(e) { e.stopPropagation(); goTo(current + 1); });
        dots.forEach(function(d) {
            d.addEventListener('click', function() { goTo(parseInt(this.dataset.index)); });
        });

        var startX = 0, diffX = 0;
        ss.addEventListener('touchstart', function(e) { startX = e.touches[0].clientX; }, { passive: true });
        ss.addEventListener('touchmove', function(e) { diffX = e.touches[0].clientX - startX; }, { passive: true });
        ss.addEventListener('touchend', function() {
            if (Math.abs(diffX) > 50) goTo(diffX > 0 ? current - 1 : current + 1);
            diffX = 0;
        });
    });
}

function initShareButtons() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.share-post-btn');
        if (!btn) return;
        e.preventDefault();
        var postId = btn.dataset.postId;
        var modal = document.getElementById('share-modal-' + postId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            var searchInput = modal.querySelector('.share-user-search');
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
                var resultsContainer = document.getElementById('share-results-' + postId);
                if (resultsContainer) resultsContainer.innerHTML = '';
            }
        }
    });

    // поиск пользователей для шаринга
    document.addEventListener('input', function(e) {
        if (!e.target.classList.contains('share-user-search')) return;
        var postId = e.target.dataset.postId;
        var q = e.target.value.trim();
        var container = document.getElementById('share-results-' + postId);
        if (!container) return;
        if (q.length < 2) { container.innerHTML = ''; return; }
        clearTimeout(e.target._searchTimeout);
        e.target._searchTimeout = setTimeout(async function() {
            try {
                var r = await fetch('/api/search/users?q=' + encodeURIComponent(q));
                if (!r.ok) return;
                var users = await r.json();
                if (!users.length) {
                    container.innerHTML = '<p style="color:var(--text-muted);padding:0.5rem;">Не найдено</p>';
                    return;
                }
                container.innerHTML = users.map(function(u) {
                    return '<div class="share-user-item" data-user-id="' + u.id + '" data-post-id="' + postId + '" style="display:flex;align-items:center;gap:0.75rem;padding:0.65rem 0.875rem;border-radius:var(--radius-md);cursor:pointer;transition:var(--transition);" onmouseover="this.style.background=\'var(--bg-tertiary)\'" onmouseout="this.style.background=\'\'">'+
                        '<div style="width:36px;height:36px;border-radius:50%;background:var(--bg-tertiary);display:flex;align-items:center;justify-content:center;font-weight:700;overflow:hidden;flex-shrink:0;">' +
                        (u.avatar ? '<img src="/uploads/' + u.avatar + '" style="width:100%;height:100%;object-fit:cover;">' : u.username[0].toUpperCase()) +
                        '</div>' +
                        '<span style="font-weight:600;">' + u.username + '</span>' +
                        '</div>';
                }).join('');
            } catch(err) { console.error(err); }
        }, 300);
    });

    // клик по пользователю в share
    document.addEventListener('click', async function(e) {
        var item = e.target.closest('.share-user-item');
        if (!item) return;
        var userId = item.dataset.userId;
        var postId = item.dataset.postId;
        try {
            var r = await fetch('/api/share_post/' + postId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: parseInt(userId) })
            });
            if (r.ok) {
                showToast('Пост отправлен!', 'success');
                var modal = document.getElementById('share-modal-' + postId);
                if (modal) closeModal(modal);
            }
        } catch(err) { console.error(err); }
    });
}

function initQuillEditors() {
    // инициализируем Quill редакторы для постов если есть
    var editorEl = document.getElementById('editor');
    if (editorEl && typeof Quill !== 'undefined') {
        var quill = new Quill('#editor', {
            theme: 'snow',
            placeholder: 'Начните писать...',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['blockquote', 'code-block'],
                    ['link'],
                    [{ 'color': [] }, { 'background': [] }],
                    ['clean']
                ]
            }
        });

        var form = editorEl.closest('form');
        var hiddenInput = document.getElementById('content-input');
        if (form && hiddenInput) {
            form.addEventListener('submit', function(e) {
                var content = quill.root.innerHTML;
                if (content === '<p><br></p>' || content.trim() === '') {
                    e.preventDefault();
                    showToast('Введите содержание', 'warning');
                    return;
                }
                hiddenInput.value = content;
            });
        }

        // для редактирования — заполняем редактор существующим контентом
        if (hiddenInput && hiddenInput.value) {
            quill.root.innerHTML = hiddenInput.value;
        }
    }
}

function showToast(message, type) {
    type = type || 'info';
    var colors = {
        success: 'var(--accent-green)',
        danger: 'var(--danger)',
        warning: '#d29922',
        info: 'var(--accent-blue)'
    };
    var toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(100px);background:var(--bg-secondary);border:1px solid ' + (colors[type] || colors.info) + ';padding:0.875rem 1.25rem;border-radius:12px;display:flex;align-items:center;gap:0.65rem;box-shadow:0 8px 24px rgba(0,0,0,0.4);z-index:10000;transition:transform 0.3s;color:var(--text-primary);font-size:0.9rem;font-weight:600;white-space:nowrap;';
    toast.innerHTML = '<span>' + message + '</span>';
    document.body.appendChild(toast);
    requestAnimationFrame(function() { toast.style.transform = 'translateX(-50%) translateY(0)'; });
    setTimeout(function() {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
    }, 3000);
}