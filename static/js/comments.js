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

        const vlineArea = e.target.closest('.comment-vline-area');
        if (vlineArea) {
            const node = vlineArea.closest('.comment-node');
            if (node) collapseComment(node);
        }

        if (e.target.classList.contains('expand-replies-btn')) {
            const node = e.target.closest('.comment-node');
            if (node) expandComment(node);
        }
    });
}

function collapseComment(node) {
    const replies = node.querySelector('.comment-replies');
    const vline = node.querySelector('.comment-vline');
    const vlineArea = node.querySelector('.comment-vline-area');
    if (!replies) return;

    const count = node.querySelectorAll('.comment-node').length;

    replies.style.display = 'none';
    if (vline) vline.style.display = 'none';
    if (vlineArea) vlineArea.style.pointerEvents = 'none';

    const existing = node.querySelector('.expand-replies-btn');
    if (!existing) {
        const btn = document.createElement('button');
        btn.className = 'expand-replies-btn';
        btn.textContent = `${count} ${pluralReplies(count)}`;
        node.querySelector('.comment-content-wrap').appendChild(btn);
    }
}

function expandComment(node) {
    const replies = node.querySelector('.comment-replies');
    const vline = node.querySelector('.comment-vline');
    const vlineArea = node.querySelector('.comment-vline-area');
    const btn = node.querySelector('.expand-replies-btn');

    if (replies) replies.style.display = '';
    if (vline) vline.style.display = '';
    if (vlineArea) vlineArea.style.pointerEvents = '';
    if (btn) btn.remove();
}

function pluralReplies(n) {
    if (n % 10 === 1 && n % 100 !== 11) return 'ответ';
    if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return 'ответа';
    return 'ответов';
}

async function submitComment(postId, content, parentId, callback) {
    const formData = new FormData();
    formData.append('content', content);
    if (parentId) formData.append('parent_id', parentId);

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
                    listEl.innerHTML = '<p class="comments-empty">Комментариев пока нет</p>';
                } else {
                    listEl.innerHTML = comments.map(c => renderComment(c, postId, 0)).join('');
                }
            }
            container.dataset.loaded = 'true';
        }
    } catch (error) {
        console.error('Load comments error:', error);
    }
}

function renderComment(comment, postId, depth) {
    const maxDepth = 6;
    const currentDepth = Math.min(depth, maxDepth);
    const hasReplies = comment.replies && comment.replies.length > 0;

    const avatarContent = comment.avatar
        ? `<img src="/uploads/${comment.avatar}" alt="">`
        : `<span>${comment.username[0].toUpperCase()}</span>`;

    const repliesHtml = hasReplies
        ? `<div class="comment-replies">
               ${comment.replies.map(r => renderComment(r, postId, depth + 1)).join('')}
           </div>`
        : '';

    return `
        <div class="comment-node" data-depth="${currentDepth}" data-comment-id="${comment.id}">
            <div class="comment-gutter">
                <div class="comment-avatar-small">${avatarContent}</div>
                ${hasReplies
                    ? `<div class="comment-vline-area" title="Свернуть">
                           <div class="comment-vline"></div>
                       </div>`
                    : `<div class="comment-vline-empty"></div>`
                }
            </div>
            <div class="comment-content-wrap">
                <div class="comment-head">
                    <a href="/profile/${comment.username}" class="comment-author">${comment.username}</a>
                    <span class="comment-time">${formatTime(comment.created_at)}</span>
                </div>
                <div class="comment-text">${escapeHtml(comment.content)}</div>
                <div class="comment-actions">
                    <button class="comment-action reply-btn"
                            data-comment-id="${comment.id}"
                            data-post-id="${postId}">
                        ↩ Ответить
                    </button>
                </div>
                <div class="reply-form-container" id="reply-form-${comment.id}" style="display:none;"></div>
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
            <form class="comment-form reply-form-inline"
                  data-post-id="${postId}"
                  data-parent-id="${commentId}">
                <input type="text"
                       name="content"
                       placeholder="Ваш ответ..."
                       class="form-control reply-input">
                <div class="reply-form-actions">
                    <button type="submit" class="btn btn-sm">Отправить</button>
                    <button type="button" class="btn btn-sm btn-secondary reply-cancel">Отмена</button>
                </div>
            </form>
        `;
        container.querySelector('input[name="content"]').focus();
        container.querySelector('.reply-cancel').addEventListener('click', function() {
            container.style.display = 'none';
        });
    } else {
        container.style.display = 'none';
    }
}

function formatTime(dateString) {
    const date = new Date(dateString.includes('Z') ? dateString : dateString + 'Z');
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