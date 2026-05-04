document.addEventListener('DOMContentLoaded', function() {
    initDropdowns();
    initModals();
    initFileUploads();
    initScrollToTop();
    initLocalTime();
    initReadMore();
    initSlideshows();
});

function initDropdowns() {
    document.querySelectorAll('.dropdown').forEach(function(d) {
        d.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
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
            var m = document.getElementById(this.dataset.modal);
            if (m) { m.classList.add('active'); document.body.style.overflow = 'hidden'; }
        });
    });
    document.querySelectorAll('.modal-overlay').forEach(function(o) {
        o.addEventListener('click', function(e) { if (e.target === this) closeModal(this); });
    });
    document.querySelectorAll('.modal-close').forEach(function(b) {
        b.addEventListener('click', function() { var m = this.closest('.modal-overlay'); if (m) closeModal(m); });
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') document.querySelectorAll('.modal-overlay.active').forEach(closeModal);
    });
}

function closeModal(m) { m.classList.remove('active'); document.body.style.overflow = ''; }

function initFileUploads() {
    document.querySelectorAll('.file-upload').forEach(function(u) {
        var input = u.querySelector('input[type="file"]');
        if (!input) return;
        var preview = u.querySelector('.file-preview');
        var text = u.querySelector('.file-upload-text');
        u.addEventListener('click', function(e) { if (e.target !== input) input.click(); });
        u.addEventListener('dragover', function(e) { e.preventDefault(); u.classList.add('dragover'); });
        u.addEventListener('dragleave', function() { u.classList.remove('dragover'); });
        u.addEventListener('drop', function(e) { e.preventDefault(); u.classList.remove('dragover'); if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; handleFileSelect(input, preview, text); } });
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
                img.style.cssText = 'max-width:100%;max-height:150px;border-radius:8px;margin-top:8px;display:block;margin-left:auto;margin-right:auto;';
                preview.appendChild(img);
            } else if (f.type.startsWith('video/')) {
                var v = document.createElement('video');
                v.src = URL.createObjectURL(f);
                v.controls = true;
                v.style.cssText = 'max-width:100%;max-height:150px;border-radius:8px;margin-top:8px;';
                preview.appendChild(v);
            }
        });
    }
}

function initScrollToTop() {
    var btn = document.createElement('button');
    btn.innerHTML = '↑';
    btn.style.cssText = 'position:fixed;bottom:20px;right:20px;width:44px;height:44px;border-radius:50%;background:var(--accent-gradient);border:none;color:white;font-size:1.3rem;cursor:pointer;opacity:0;visibility:hidden;transition:all 0.3s;z-index:999;';
    document.body.appendChild(btn);
    window.addEventListener('scroll', function() {
        btn.style.opacity = window.scrollY > 300 ? '1' : '0';
        btn.style.visibility = window.scrollY > 300 ? 'visible' : 'hidden';
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
        else el.textContent = d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    });
}

function initReadMore() {
    document.querySelectorAll('.read-more-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var card = this.closest('.post-card');
            var text = card.querySelector('.post-text');
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

        if (prev) prev.addEventListener('click', function() { goTo(current - 1); });
        if (next) next.addEventListener('click', function() { goTo(current + 1); });
        dots.forEach(function(d) { d.addEventListener('click', function() { goTo(parseInt(this.dataset.index)); }); });

        var startX = 0, diff = 0;
        ss.addEventListener('touchstart', function(e) { startX = e.touches[0].clientX; }, { passive: true });
        ss.addEventListener('touchmove', function(e) { diff = e.touches[0].clientX - startX; }, { passive: true });
        ss.addEventListener('touchend', function() { if (Math.abs(diff) > 50) { goTo(diff > 0 ? current - 1 : current + 1); } diff = 0; });
    });
}

function showToast(message, type) {
    type = type || 'info';
    var colors = { success: 'var(--accent-green)', danger: 'var(--danger)', warning: 'var(--warning)', info: 'var(--accent-blue)' };
    var toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(100px);background:var(--bg-secondary);border:1px solid ' + (colors[type] || colors.info) + ';padding:0.875rem 1.25rem;border-radius:12px;display:flex;align-items:center;gap:0.65rem;box-shadow:0 8px 24px rgba(0,0,0,0.4);z-index:10000;transition:transform 0.3s;color:var(--text-primary);font-size:0.9rem;';
    toast.innerHTML = '<span>' + message + '</span>';
    document.body.appendChild(toast);
    requestAnimationFrame(function() { toast.style.transform = 'translateX(-50%) translateY(0)'; });
    setTimeout(function() {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}