document.addEventListener('DOMContentLoaded', function() {
    initDropdowns();
    initModals();
    initFileUploads();
    initVideoPreview();
    initScrollToTop();
    initLocalTime();
    initReadMore();
});

function initDropdowns() {
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
        });
    });

    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown.active').forEach(d => {
            d.classList.remove('active');
        });
    });
}

function initModals() {
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this);
            }
        });
    });

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) closeModal(modal);
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                closeModal(modal);
            });
        }
    });
}

function closeModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function initFileUploads() {
    document.querySelectorAll('.file-upload').forEach(upload => {
        const input = upload.querySelector('input[type="file"]');
        if (!input) return;

        const preview = upload.querySelector('.file-preview');
        const text = upload.querySelector('.file-upload-text');

        upload.addEventListener('click', function(e) {
            if (e.target !== input) input.click();
        });

        upload.addEventListener('dragover', (e) => {
            e.preventDefault();
            upload.classList.add('dragover');
        });

        upload.addEventListener('dragleave', () => {
            upload.classList.remove('dragover');
        });

        upload.addEventListener('drop', (e) => {
            e.preventDefault();
            upload.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                handleFileSelect(input, preview, text);
            }
        });

        input.addEventListener('change', () => {
            handleFileSelect(input, preview, text);
        });
    });
}

function handleFileSelect(input, preview, text) {
    const files = Array.from(input.files);
    if (files.length === 0) return;

    if (text) {
        text.textContent = files.length === 1 ? files[0].name : `Выбрано файлов: ${files.length}`;
    }

    if (preview) {
        preview.innerHTML = '';
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'max-width:100%;max-height:200px;border-radius:8px;margin-top:10px;display:block;margin-left:auto;margin-right:auto;';
                preview.appendChild(img);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.style.cssText = 'max-width:100%;max-height:200px;border-radius:8px;margin-top:10px;display:block;';
                preview.appendChild(video);
            } else if (file.type.startsWith('audio/')) {
                const audio = document.createElement('audio');
                audio.src = URL.createObjectURL(file);
                audio.controls = true;
                audio.style.cssText = 'width:100%;margin-top:10px;';
                preview.appendChild(audio);
            }
        });
    }
}

function initVideoPreview() {
    document.querySelectorAll('.video-preview-container video').forEach(video => {
        video.addEventListener('mouseenter', function() {
            this.play().catch(() => {});
        });

        video.addEventListener('mouseleave', function() {
            this.pause();
            this.currentTime = 0;
        });
    });
}

function initScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '↑';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--accent-gradient);
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s;
        z-index: 999;
    `;
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.visibility = 'visible';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.visibility = 'hidden';
        }
    });

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

function initLocalTime() {
    document.querySelectorAll('[data-utc]').forEach(el => {
        const utcStr = el.dataset.utc;
        if (!utcStr) return;

        const date = new Date(utcStr.includes('Z') ? utcStr : utcStr + 'Z');
        if (isNaN(date.getTime())) return;

        const now = new Date();
        const diff = Math.floor((now - date) / 1000);

        if (diff < 60) {
            el.textContent = 'только что';
        } else if (diff < 3600) {
            el.textContent = `${Math.floor(diff / 60)} мин назад`;
        } else if (diff < 86400) {
            el.textContent = `${Math.floor(diff / 3600)} ч назад`;
        } else if (diff < 604800) {
            el.textContent = `${Math.floor(diff / 86400)} д назад`;
        } else {
            el.textContent = date.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    });
}

function initReadMore() {
    document.querySelectorAll('.read-more-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const postCard = this.closest('.post-card');
            const postText = postCard.querySelector('.post-text');

            if (postText.classList.contains('truncated')) {
                postText.classList.remove('truncated');
                postText.classList.add('expanded');
                this.textContent = 'Свернуть ↑';
            } else {
                postText.classList.add('truncated');
                postText.classList.remove('expanded');
                this.textContent = 'Читать далее ↓';
                postCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const colors = {
        success: 'var(--accent-green)',
        danger: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--accent-blue)'
    };

    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: var(--bg-secondary);
        border: 1px solid ${colors[type] || colors.info};
        padding: 1rem 1.5rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        z-index: 10000;
        transition: transform 0.3s ease;
        color: var(--text-primary);
        font-size: 0.95rem;
    `;

    const icons = { success: '✓', danger: '✕', warning: '⚠️', info: 'ℹ' };
    toast.innerHTML = `<span style="color:${colors[type] || colors.info}">${icons[type] || icons.info}</span><span>${message}</span>`;

    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    });

    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function confirmAction(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay active';
        overlay.innerHTML = `
            <div class="modal" style="max-width: 400px;">
                <div class="modal-header">
                    <h3 class="modal-title">Подтверждение</h3>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">Отмена</button>
                    <button class="btn btn-danger" data-action="confirm">Подтвердить</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';

        overlay.querySelector('[data-action="cancel"]').addEventListener('click', () => {
            overlay.remove();
            document.body.style.overflow = '';
            resolve(false);
        });

        overlay.querySelector('[data-action="confirm"]').addEventListener('click', () => {
            overlay.remove();
            document.body.style.overflow = '';
            resolve(true);
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
                document.body.style.overflow = '';
                resolve(false);
            }
        });
    });
}