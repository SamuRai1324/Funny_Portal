document.addEventListener('DOMContentLoaded', function() {
    initComments();
});

function initComments() {
    document.querySelectorAll('.toggle-comments').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const commentsSection = document.getElementById(`comments-${postId}`);

            if (commentsSection) {
                commentsSection.classList.toggle('hidden');

                if (!commentsSection.classList.contains('hidden') && !commentsSection.dataset.loaded) {
                    loadComments(postId);
                }
            }
        });
    });

    document.addEventListener('submit', function(e) {
        const form = e.target;

        if (form.classList.contains('comment-form')) {
            e.preventDefault();
            const postId = form.dataset.postId;
            const parentId = form.dataset.parentId || null;
            const input = form.querySelector('input[name="content"]');
            const content = input.value.trim();

            if (!content) return;

            submitComment(postId, content, parentId, function() {
                input.value = '';
                loadComments(postId);

                const countEl = document.querySelector(`.comment-count-${postId}`);
                if (countEl) {
                    countEl.textContent = parseInt(countEl.textContent || 0) + 1;
                }
            });
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-btn')) {
            const commentId = e.target.dataset.commentId;
            const postId = e.target.dataset.postId;
            toggleReplyForm(commentId, postId);
        }
    });
}

async function submitComment(postId, content, parentId, callback) {
    const formData = new FormData();
    formData.append('content', content);
    if (parentId) {
        formData.append('parent_id', parentId);
    }

    try {
        const response = await fetch(`/api/comment/${postId}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            if (callback) callback();
        } else if (response.status === 401) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Comment submit error:', error);
    }
}

async function loadComments(postId) {
    const container = document.getElementById(`comments-${postId}`);
    if (!container) return;

    try {
        const response = await fetch(`/api/comments/${postId}`);
        if (response.ok) {
            const comments = await response.json();
            const listEl = document.getElementById(`comments-list-${postId}`);
            if (listEl) {
                if (comments.length === 0) {
                    listEl.innerHTML = '<p class="text-muted" style="padding: 1rem 0;">Комментариев пока нет</p>';
                } else {
                    listEl.innerHTML = comments.map(c => renderComment(c, postId)).join('');
                }
            }
            container.dataset.loaded = 'true';
        }
    } catch (error) {
        console.error('Load comments error:', error);
    }
}

function renderComment(comment, postId) {
    const avatarContent = comment.avatar
        ? `<img src="/uploads/${comment.avatar}" alt="">`
        : comment.username[0].toUpperCase();

    const repliesHtml = comment.replies && comment.replies.length > 0
        ? `<div class="comment-replies">${comment.replies.map(r => renderComment(r, postId)).join('')}</div>`
        : '';

    return `
        <div class="comment" data-comment-id="${comment.id}">
            <div class="comment-avatar">${avatarContent}</div>
            <div class="comment-content">
                <div class="comment-header">
                    <a href="/profile/${comment.username}" class="comment-author">${comment.username}</a>
                    <span class="comment-time">${formatTime(comment.created_at)}</span>
                </div>
                <div class="comment-text">${escapeHtml(comment.content)}</div>
                <div class="comment-actions">
                    <button class="comment-action reply-btn" data-comment-id="${comment.id}" data-post-id="${postId}">
                        Ответить
                    </button>
                </div>
                <div class="reply-form-container" id="reply-form-${comment.id}" style="display: none;"></div>
                ${repliesHtml}
            </div>
        </div>
    `;
}

function toggleReplyForm(commentId, postId) {
    const container = document.getElementById(`reply-form-${commentId}`);
    if (!container) return;

    if (container.style.display === 'none') {
        container.style.display = 'block';
        container.innerHTML = `
            <form class="comment-form reply-form" data-post-id="${postId}" data-parent-id="${commentId}" style="margin-top: 0.75rem;">
                <input type="text" name="content" placeholder="Ваш ответ..." class="form-control" style="margin-bottom: 0.5rem;">
                <button type="submit" class="btn btn-sm">Отправить</button>
            </form>
        `;
        container.querySelector('input[name="content"]').focus();
    } else {
        container.style.display = 'none';
    }
}

function formatTime(dateString) {
    const date = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'только что';
    if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} д назад`;

    return date.toLocaleDateString('ru-RU');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}