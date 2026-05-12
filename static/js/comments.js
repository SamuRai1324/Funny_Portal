document.addEventListener('DOMContentLoaded', function() {
    initComments();
});

function initComments() {
    // toggle комментариев
    document.querySelectorAll('.toggle-comments').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var postId = this.dataset.postId;
            var section = document.getElementById('comments-' + postId);
            if (!section) return;
            section.classList.toggle('hidden');
            if (!section.classList.contains('hidden') && !section.dataset.loaded) {
                loadComments(postId);
            }
        });
    });

    // submit комментария через AJAX
    document.addEventListener('submit', function(e) {
        var form = e.target;
        if (!form.classList.contains('comment-form')) return;
        e.preventDefault();
        var postId = form.dataset.postId;
        var parentId = form.dataset.parentId || null;
        var input = form.querySelector('input[name="content"]');
        var content = input ? input.value.trim() : '';
        if (!content) return;

        submitComment(postId, content, parentId, function(data) {
            if (input) input.value = '';
            // не закрываем секцию — просто перезагружаем список
            loadComments(postId);
            // обновляем счётчик
            var countEl = document.querySelector('.comment-count-' + postId);
            if (countEl && data && data.comment_count !== undefined) {
                countEl.textContent = data.comment_count;
            } else if (countEl) {
                countEl.textContent = parseInt(countEl.textContent || 0) + 1;
            }
            // если это форма ответа — скрываем её
            if (parentId) {
                var container = document.getElementById('reply-form-' + parentId);
                if (container) container.style.display = 'none';
            }
        });
    });

    // клики внутри комментариев
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-btn')) {
            var commentId = e.target.dataset.commentId;
            var postId = e.target.dataset.postId;
            var currentUserId = document.body.dataset.currentUserId;
            // проверяем — не свой ли комментарий
            var node = e.target.closest('.comment-node');
            if (node && node.dataset.userId === currentUserId) {
                showToast('Нельзя ответить на свой комментарий', 'warning');
                return;
            }
            toggleReplyForm(commentId, postId);
        }
        if (e.target.classList.contains('edit-comment-btn')) {
            startEditComment(e.target.dataset.commentId);
        }
        if (e.target.classList.contains('save-edit-btn')) {
            saveEditComment(e.target.dataset.commentId);
        }
        if (e.target.classList.contains('cancel-edit-btn')) {
            cancelEditComment(e.target.dataset.commentId);
        }
        var vlineArea = e.target.closest('.comment-vline-area');
        if (vlineArea) {
            var nodeV = vlineArea.closest('.comment-node');
            if (nodeV) collapseComment(nodeV);
        }
        if (e.target.classList.contains('expand-replies-btn')) {
            var nodeE = e.target.closest('.comment-node');
            if (nodeE) expandComment(nodeE);
        }
    });

    // загружаем комментарии на странице поста
    var page = document.querySelector('.post-view-page');
    if (page) {
        var postId = page.getAttribute('data-post-id');
        if (postId) loadComments(parseInt(postId));
    }
}

function collapseComment(node) {
    var replies = node.querySelector('.comment-replies');
    var vline = node.querySelector('.comment-vline');
    var vlineArea = node.querySelector('.comment-vline-area');
    if (!replies) return;
    var count = node.querySelectorAll('.comment-node').length;
    replies.style.display = 'none';
    if (vline) vline.style.display = 'none';
    if (vlineArea) vlineArea.style.pointerEvents = 'none';
    if (!node.querySelector('.expand-replies-btn')) {
        var btn = document.createElement('button');
        btn.className = 'expand-replies-btn';
        btn.textContent = count + ' ' + pluralReplies(count);
        node.querySelector('.comment-content-wrap').appendChild(btn);
    }
}

function expandComment(node) {
    var replies = node.querySelector('.comment-replies');
    var vline = node.querySelector('.comment-vline');
    var vlineArea = node.querySelector('.comment-vline-area');
    var btn = node.querySelector('.expand-replies-btn');
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
    var formData = new FormData();
    formData.append('content', content);
    if (parentId) formData.append('parent_id', parentId);
    try {
        var response = await fetch('/api/comment/' + postId, { method: 'POST', body: formData });
        if (response.ok) {
            var data = await response.json();
            if (data.error) {
                showToast(data.error, 'warning');
                return;
            }
            if (callback) callback(data);
        } else if (response.status === 401) {
            window.location.href = '/login';
        } else if (response.status === 400) {
            var err = await response.json();
            showToast(err.error || 'Ошибка', 'warning');
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadComments(postId) {
    try {
        var response = await fetch('/api/comments/' + postId);
        if (!response.ok) return;
        var comments = await response.json();
        var listEl = document.getElementById('comments-list-' + postId);
        if (!listEl) return;
        listEl.innerHTML = comments.length === 0
            ? '<p class="comments-empty">Комментариев пока нет</p>'
            : comments.map(function(c) { return renderComment(c, postId, 0); }).join('');
        var section = document.getElementById('comments-' + postId);
        if (section) section.dataset.loaded = 'true';
    } catch (err) {
        console.error(err);
    }
}

function renderComment(comment, postId, depth) {
    var hasReplies = comment.replies && comment.replies.length > 0;
    var avatar = comment.avatar
        ? '<img src="/uploads/' + comment.avatar + '" alt="">'
        : '<span>' + comment.username[0].toUpperCase() + '</span>';
    var replies = hasReplies
        ? '<div class="comment-replies">' + comment.replies.map(function(r) { return renderComment(r, postId, depth + 1); }).join('') + '</div>'
        : '';
    var uid = document.body.dataset.currentUserId || '';
    var isOwner = String(comment.user_id) === uid;
    var editBtn = isOwner
        ? '<button class="comment-action edit-comment-btn" data-comment-id="' + comment.id + '">✏️ Изменить</button>'
        : '';
    // кнопка ответить — скрываем если это свой комментарий
    var replyBtn = (uid && String(comment.user_id) !== uid)
        ? '<button class="comment-action reply-btn" data-comment-id="' + comment.id + '" data-post-id="' + postId + '">↩ Ответить</button>'
        : '';

    return '<div class="comment-node" data-comment-id="' + comment.id + '" data-user-id="' + comment.user_id + '">' +
        '<div class="comment-gutter">' +
            '<div class="comment-avatar-small">' + avatar + '</div>' +
            (hasReplies
                ? '<div class="comment-vline-area"><div class="comment-vline"></div></div>'
                : '<div class="comment-vline-empty"></div>') +
        '</div>' +
        '<div class="comment-content-wrap">' +
            '<div class="comment-head">' +
                '<a href="/profile/' + comment.username + '" class="comment-author">' + comment.username + '</a>' +
                '<span class="comment-time">' + formatCommentTime(comment.created_at) + '</span>' +
            '</div>' +
            '<div class="comment-text" id="comment-text-' + comment.id + '">' + escapeHtml(comment.content) + '</div>' +
            '<div class="comment-edit-area" id="comment-edit-' + comment.id + '" style="display:none;"></div>' +
            '<div class="comment-actions">' + replyBtn + editBtn + '</div>' +
            '<div class="reply-form-container" id="reply-form-' + comment.id + '" style="display:none;"></div>' +
            replies +
        '</div></div>';
}

function startEditComment(commentId) {
    var textEl = document.getElementById('comment-text-' + commentId);
    var editEl = document.getElementById('comment-edit-' + commentId);
    if (!textEl || !editEl) return;
    textEl.style.display = 'none';
    editEl.style.display = 'block';
    editEl.innerHTML = '<input type="text" class="form-control edit-comment-input" value="' + escapeHtml(textEl.textContent.trim()) + '">' +
        '<div style="display:flex;gap:0.4rem;margin-top:0.4rem;">' +
        '<button class="btn btn-sm save-edit-btn" data-comment-id="' + commentId + '">Сохранить</button>' +
        '<button class="btn btn-sm btn-secondary cancel-edit-btn" data-comment-id="' + commentId + '">Отмена</button></div>';
    var inp = editEl.querySelector('.edit-comment-input');
    if (inp) inp.focus();
}

function cancelEditComment(commentId) {
    var textEl = document.getElementById('comment-text-' + commentId);
    var editEl = document.getElementById('comment-edit-' + commentId);
    if (textEl) textEl.style.display = '';
    if (editEl) { editEl.style.display = 'none'; editEl.innerHTML = ''; }
}

async function saveEditComment(commentId) {
    var editEl = document.getElementById('comment-edit-' + commentId);
    if (!editEl) return;
    var inp = editEl.querySelector('.edit-comment-input');
    var content = inp ? inp.value.trim() : '';
    if (!content) return;
    try {
        var response = await fetch('/api/comment/' + commentId + '/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });
        if (response.ok) {
            var textEl = document.getElementById('comment-text-' + commentId);
            if (textEl) textEl.textContent = content;
            cancelEditComment(commentId);
        }
    } catch (err) {
        console.error(err);
    }
}

function toggleReplyForm(commentId, postId) {
    var container = document.getElementById('reply-form-' + commentId);
    if (!container) return;
    if (container.style.display === 'none' || container.style.display === '') {
        container.style.display = 'block';
        container.innerHTML =
            '<form class="comment-form reply-form-inline" data-post-id="' + postId + '" data-parent-id="' + commentId + '">' +
            '<input type="text" name="content" placeholder="Ответ..." class="form-control reply-input">' +
            '<div class="reply-form-actions">' +
            '<button type="submit" class="btn btn-sm">➤</button>' +
            '<button type="button" class="btn btn-sm btn-secondary reply-cancel">✕</button>' +
            '</div></form>';
        var inp = container.querySelector('input');
        if (inp) inp.focus();
        container.querySelector('.reply-cancel').addEventListener('click', function() {
            container.style.display = 'none';
        });
    } else {
        container.style.display = 'none';
    }
}

function formatCommentTime(s) {
    if (!s) return '';
    var d = new Date(s.indexOf('Z') > -1 ? s : s + 'Z');
    var diff = Math.floor((new Date() - d) / 1000);
    if (diff < 60) return 'сейчас';
    if (diff < 3600) return Math.floor(diff / 60) + ' мин';
    if (diff < 86400) return Math.floor(diff / 3600) + ' ч';
    if (diff < 604800) return Math.floor(diff / 86400) + ' д';
    return d.toLocaleDateString('ru-RU');
}

function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}