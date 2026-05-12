from flask import Flask, request, redirect, session, flash, render_template, url_for, jsonify, send_from_directory, abort, g
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
import re
import uuid
from datetime import datetime, timedelta
from config import *

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=WAL')
        g.db.execute('PRAGMA busy_timeout=30000')
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            avatar TEXT,
            banner TEXT,
            bio TEXT,
            birth_date TEXT,
            theme TEXT DEFAULT 'dark',
            custom_bg TEXT,
            custom_secondary TEXT,
            custom_accent TEXT,
            custom_text TEXT,
            is_banned INTEGER DEFAULT 0,
            ban_until TEXT,
            ban_reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            banned_by INTEGER NOT NULL,
            reason TEXT,
            is_permanent INTEGER DEFAULT 0,
            ban_until TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            avatar TEXT,
            banner TEXT,
            creator_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS channel_subscribers (
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, channel_id)
        );
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id INTEGER,
            post_type TEXT NOT NULL,
            title TEXT,
            content TEXT,
            file_path TEXT,
            is_story INTEGER DEFAULT 0,
            is_nsfw INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 1,
            story_expires_at TEXT,
            view_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS post_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS post_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            reaction_type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, post_id)
        );
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS hashtags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS post_hashtags (
            post_id INTEGER NOT NULL,
            hashtag_id INTEGER NOT NULL,
            PRIMARY KEY (post_id, hashtag_id)
        );
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            last_message_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id)
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            content TEXT,
            file_path TEXT,
            file_type TEXT,
            shared_post_id INTEGER,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS global_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_cooldowns (
            user_id INTEGER PRIMARY KEY,
            cooldown_until TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            link TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            post_id INTEGER,
            comment_id INTEGER,
            user_id INTEGER,
            category TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            handled_by INTEGER,
            handled_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS marquee_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            link TEXT,
            is_auto INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    # миграция: добавить столбцы если не существуют
    try:
        conn.execute('ALTER TABLE posts ADD COLUMN is_nsfw INTEGER DEFAULT 0')
    except:
        pass
    try:
        conn.execute('ALTER TABLE posts ADD COLUMN is_approved INTEGER DEFAULT 1')
    except:
        pass
    try:
        conn.execute('ALTER TABLE messages ADD COLUMN shared_post_id INTEGER')
    except:
        pass
    conn.commit()
    conn.close()


def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())


def save_file(file, file_type):
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        folder_map = {
            'video': 'videos', 'photo': 'photos', 'audio': 'audio',
            'story': 'stories', 'avatar': 'avatars', 'banner': 'banners'
        }
        folder = UPLOAD_FOLDERS.get(folder_map.get(file_type, 'photos'))
        file.save(os.path.join(folder, filename))
        return f"{folder_map.get(file_type, 'photos')}/{filename}"
    return None


def check_nsfw_text(text):
    if not text:
        return False
    text_lower = text.lower()
    for keyword in NSFW_KEYWORDS:
        if keyword in text_lower:
            return True
    return False


def get_current_user():
    if 'user_id' not in session:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user:
        session.clear()
        return None
    if user['is_banned']:
        if user['ban_until']:
            if datetime.fromisoformat(user['ban_until']) > datetime.now():
                return dict(user) | {'is_currently_banned': True}
            else:
                conn.execute('UPDATE users SET is_banned = 0, ban_until = NULL, ban_reason = NULL WHERE id = ?', (user['id'],))
                conn.commit()
        else:
            return dict(user) | {'is_currently_banned': True}
    return user


def is_user_adult(user):
    if not user:
        return False
    try:
        bd = user['birth_date']
        if not bd:
            return False
        born = datetime.strptime(bd, '%Y-%m-%d')
        age = (datetime.now() - born).days // 365
        return age >= 18
    except:
        return False


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо войти в аккаунт', 'danger')
            return redirect('/login')
        user = get_current_user()
        if user and isinstance(user, dict) and user.get('is_currently_banned'):
            session.clear()
            flash('Ваш аккаунт заблокирован', 'danger')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def role_required(min_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect('/login')
            if ROLES.get(user['role'], 0) < ROLES.get(min_role, 999):
                flash('Недостаточно прав', 'danger')
                return redirect('/')
            return f(*args, **kwargs)
        return decorated
    return decorator


def add_notification(user_id, notif_type, content, link=None):
    conn = get_db()
    conn.execute('INSERT INTO notifications (user_id, type, content, link) VALUES (?, ?, ?, ?)',
                (user_id, notif_type, content, link))
    conn.commit()


def log_admin_action(admin_id, action, target_type=None, target_id=None, details=None):
    conn = get_db()
    # предотвращаем дублирование логов
    existing = conn.execute(
        'SELECT id FROM admin_logs WHERE admin_id=? AND action=? AND target_type=? AND target_id=? AND created_at > datetime("now", "-2 seconds")',
        (admin_id, action, target_type, target_id)
    ).fetchone()
    if not existing:
        conn.execute('INSERT INTO admin_logs (admin_id, action, target_type, target_id, details) VALUES (?, ?, ?, ?, ?)',
                    (admin_id, action, target_type, target_id, details))
        conn.commit()


def extract_hashtags(text):
    if not text:
        return []
    return list(set(re.findall(r'#(\w+)', text)))


def save_hashtags(post_id, hashtags):
    conn = get_db()
    for tag in hashtags:
        existing = conn.execute('SELECT id FROM hashtags WHERE name = ?', (tag.lower(),)).fetchone()
        hid = existing['id'] if existing else conn.execute('INSERT INTO hashtags (name) VALUES (?)', (tag.lower(),)).lastrowid
        conn.execute('INSERT OR IGNORE INTO post_hashtags (post_id, hashtag_id) VALUES (?, ?)', (post_id, hid))
    conn.commit()


def get_chat_messages():
    return get_db().execute(
        'SELECT g.*, u.username, u.avatar FROM global_chat g JOIN users u ON g.user_id = u.id ORDER BY g.id DESC LIMIT 50'
    ).fetchall()[::-1]


def get_unread_notifications_count(user_id):
    r = get_db().execute('SELECT COUNT(*) as c FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,)).fetchone()
    return r['c'] if r else 0


def get_unread_messages_count(user_id):
    r = get_db().execute(
        'SELECT COUNT(*) as c FROM messages m JOIN conversations c ON m.conversation_id = c.id '
        'WHERE (c.user1_id = ? OR c.user2_id = ?) AND m.sender_id != ? AND m.is_read = 0',
        (user_id, user_id, user_id)
    ).fetchone()
    return r['c'] if r else 0


def get_pending_reports_count():
    r = get_db().execute('SELECT COUNT(*) as c FROM reports WHERE status = "pending"').fetchone()
    return r['c'] if r else 0


def get_marquee_items():
    conn = get_db()
    items = []
    # последние популярные посты
    popular = conn.execute(
        'SELECT id, title, content FROM posts WHERE is_story = 0 AND title IS NOT NULL AND title != "" '
        'ORDER BY view_count DESC LIMIT 5'
    ).fetchall()
    for p in popular:
        items.append({'text': f"🔥 {p['title']}", 'link': f"/post/{p['id']}"})
    # последние новые посты
    recent = conn.execute(
        'SELECT id, title, content FROM posts WHERE is_story = 0 AND title IS NOT NULL AND title != "" '
        'ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    for p in recent:
        if not any(i['link'] == f"/post/{p['id']}" for i in items):
            items.append({'text': f"✨ {p['title']}", 'link': f"/post/{p['id']}"})
    return items


def enrich_posts(posts, user, conn):
    result = []
    for post in posts:
        p = dict(post)
        reactions = conn.execute(
            'SELECT reaction_type, COUNT(*) as count FROM reactions WHERE post_id = ? GROUP BY reaction_type',
            (post['id'],)
        ).fetchall()
        p['reactions'] = {r['reaction_type']: r['count'] for r in reactions}
        p['user_reaction'] = None
        if user:
            ur = conn.execute('SELECT reaction_type FROM reactions WHERE user_id = ? AND post_id = ?',
                            (user['id'], post['id'])).fetchone()
            p['user_reaction'] = ur['reaction_type'] if ur else None
        else:
            p['user_reaction'] = None
        files = conn.execute('SELECT * FROM post_files WHERE post_id = ?', (post['id'],)).fetchall()
        p['files'] = [dict(f) for f in files]
        # проверяем просмотрен ли
        if user:
            viewed = conn.execute('SELECT 1 FROM post_views WHERE post_id = ? AND user_id = ?',
                                  (post['id'], user['id'])).fetchone()
            p['is_viewed'] = viewed is not None
        else:
            p['is_viewed'] = False
        result.append(p)
    return result


def record_view(post_id, user_id):
    conn = get_db()
    try:
        conn.execute('INSERT OR IGNORE INTO post_views (post_id, user_id) VALUES (?, ?)', (post_id, user_id))
        conn.execute('UPDATE posts SET view_count = (SELECT COUNT(*) FROM post_views WHERE post_id = ?) WHERE id = ?',
                    (post_id, post_id))
        conn.commit()
    except:
        pass


@app.context_processor
def inject_globals():
    user = get_current_user()
    notif_count = get_unread_notifications_count(user['id']) if user else 0
    msg_count = get_unread_messages_count(user['id']) if user else 0
    pending_reports = get_pending_reports_count() if user and user['role'] in ['admin', 'moderator'] else 0
    theme = 'dark'
    theme_vars = {}
    if user:
        try:
            theme = user['theme'] or 'dark'
        except:
            theme = 'dark'
        if theme == 'custom':
            try:
                theme_vars = {
                    'custom_bg': user['custom_bg'] or '#0d1117',
                    'custom_secondary': user['custom_secondary'] or '#161b22',
                    'custom_accent': user['custom_accent'] or '#7D71D8',
                    'custom_text': user['custom_text'] or '#f0f6fc',
                }
            except:
                theme = 'dark'
    marquee = get_marquee_items() if user else []
    return {
        'current_user': user, 'notification_count': notif_count,
        'message_count': msg_count, 'pending_reports_count': pending_reports,
        'REACTION_TYPES': REACTION_TYPES, 'REPORT_CATEGORIES': REPORT_CATEGORIES,
        'POST_TYPE_LABELS': POST_TYPE_LABELS,
        'current_theme': theme, 'theme_vars': theme_vars,
        'marquee_items': marquee,
    }


# ══════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════

@app.route('/')
def index():
    user = get_current_user()
    current_tab = request.args.get('tab', 'all')
    search_query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'new')
    post_type = request.args.get('type', 'all')
    conn = get_db()

    stories = []
    chat_messages = []
    if user:
        chat_messages = get_chat_messages()
        stories = conn.execute(
            'SELECT p.*, u.username, u.avatar FROM posts p JOIN users u ON p.user_id = u.id '
            'WHERE p.is_story = 1 AND p.story_expires_at > datetime("now") ORDER BY p.created_at DESC'
        ).fetchall()

    q = ('SELECT p.*, u.username, u.avatar, c.name as channel_name, c.avatar as channel_avatar, '
         '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
         'FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN channels c ON p.channel_id = c.id '
         'WHERE p.is_story = 0')
    params = []

    if search_query:
        q += ' AND (p.title LIKE ? OR p.content LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])

    if current_tab == 'popular':
        q += ' ORDER BY p.view_count DESC, p.created_at DESC LIMIT 50'
    elif sort_by == 'week':
        q += " AND p.created_at > datetime('now', '-7 days') ORDER BY p.view_count DESC LIMIT 50"
    elif sort_by == 'month':
        q += " AND p.created_at > datetime('now', '-30 days') ORDER BY p.view_count DESC LIMIT 50"
    elif current_tab not in ('all',):
        q += ' AND p.post_type = ?'
        params.append(current_tab)
        if sort_by == 'popular':
            q += ' ORDER BY p.view_count DESC, p.created_at DESC LIMIT 50'
        elif sort_by == 'views':
            q += ' ORDER BY p.view_count DESC LIMIT 50'
        else:
            q += ' ORDER BY p.created_at DESC LIMIT 50'
    else:
        if sort_by == 'popular':
            q += ' ORDER BY p.view_count DESC, p.created_at DESC LIMIT 50'
        elif sort_by == 'views':
            q += ' ORDER BY p.view_count DESC LIMIT 50'
        else:
            q += ' ORDER BY p.created_at DESC LIMIT 50'

    posts = conn.execute(q, params).fetchall()
    posts_data = enrich_posts(posts, user, conn)

    if user:
        for p in posts_data:
            record_view(p['id'], user['id'])

    # для незалогиненных тоже показываем посты
    all_posts_for_guests = []
    if not user:
        guest_posts = conn.execute(
            'SELECT p.*, u.username, u.avatar, c.name as channel_name, c.avatar as channel_avatar, '
            '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
            'FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN channels c ON p.channel_id = c.id '
            'WHERE p.is_story = 0 AND p.is_nsfw = 0 ORDER BY p.created_at DESC LIMIT 20'
        ).fetchall()
        all_posts_for_guests = enrich_posts(guest_posts, None, conn)

    return render_template('index.html', posts=posts_data, stories=stories,
                           current_tab=current_tab, chat_messages=chat_messages,
                           search_query=search_query, sort_by=sort_by,
                           guest_posts=all_posts_for_guests)


@app.route('/post/<int:post_id>')
def post_view(post_id):
    conn = get_db()
    post = conn.execute(
        'SELECT p.*, u.username, u.avatar, c.name as channel_name, c.avatar as channel_avatar, '
        '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
        'FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN channels c ON p.channel_id = c.id '
        'WHERE p.id = ? AND p.is_story = 0', (post_id,)
    ).fetchone()
    if not post:
        abort(404)
    user = get_current_user()
    post_data = enrich_posts([post], user, conn)[0]
    if user:
        record_view(post_id, user['id'])
    chat_messages = get_chat_messages() if user else []
    return render_template('post_view.html', post=post_data, chat_messages=chat_messages)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    user = get_current_user()
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        abort(404)
    if post['user_id'] != user['id'] and user['role'] != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(f'/post/{post_id}')
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        conn.execute('UPDATE posts SET title = ?, content = ?, is_nsfw = ? WHERE id = ?',
                     (title or None, content, is_nsfw, post_id))
        conn.commit()
        tags = extract_hashtags(content)
        if tags:
            conn.execute('DELETE FROM post_hashtags WHERE post_id = ?', (post_id,))
            save_hashtags(post_id, tags)
        flash('Пост обновлён', 'success')
        return redirect(f'/post/{post_id}')
    chat_messages = get_chat_messages()
    return render_template('create/edit_post.html', post=post, chat_messages=chat_messages)


@app.route('/story/<int:story_id>')
def story_view(story_id):
    conn = get_db()
    story = conn.execute(
        'SELECT p.*, u.username, u.avatar FROM posts p JOIN users u ON p.user_id = u.id '
        'WHERE p.id = ? AND p.is_story = 1', (story_id,)
    ).fetchone()
    if not story:
        abort(404)
    user = get_current_user()
    return render_template('story_view.html', story=story, chat_messages=get_chat_messages() if user else [])


@app.route('/search/users')
def search_users():
    q = request.args.get('q', '').strip()
    conn = get_db()
    users = []
    if q and len(q) >= 2:
        users = conn.execute('SELECT id, username, avatar, bio FROM users WHERE username LIKE ? LIMIT 20',
                             (f'%{q}%',)).fetchall()
    user = get_current_user()
    return render_template('search_users.html', users=users, search_query=q,
                           chat_messages=get_chat_messages() if user else [])


@app.route('/api/search/users')
@login_required
def api_search_users():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    users = get_db().execute('SELECT id, username, avatar, bio FROM users WHERE username LIKE ? LIMIT 10',
                             (f'%{q}%',)).fetchall()
    return jsonify([{'id': u['id'], 'username': u['username'], 'avatar': u['avatar'], 'bio': u['bio']} for u in users])


@app.route('/api/search/posts')
@login_required
def api_search_posts():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    posts = get_db().execute(
        'SELECT p.id, p.title, p.post_type, p.file_path, u.username FROM posts p JOIN users u ON p.user_id = u.id '
        'WHERE p.is_story = 0 AND (p.title LIKE ? OR p.content LIKE ?) LIMIT 10',
        (f'%{q}%', f'%{q}%')
    ).fetchall()
    return jsonify([{
        'id': p['id'], 'title': p['title'] or 'Без названия',
        'post_type': POST_TYPE_LABELS.get(p['post_type'], p['post_type']),
        'username': p['username'], 'file_path': p['file_path']
    } for p in posts])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        if get_current_user():
            return redirect('/')
        session.clear()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        birth_date = request.form.get('birth_date', '').strip()
        if not username or not email or not password or not birth_date:
            flash('Заполните все поля', 'danger')
            return render_template('register.html')
        if len(username) < 3:
            flash('Логин минимум 3 символа', 'danger')
            return render_template('register.html')
        if len(password) < 4:
            flash('Пароль минимум 4 символа', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        try:
            get_db().execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                             (username, email, password))
            get_db().commit()
            flash('Регистрация успешна!', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Пользователь уже существует', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if get_current_user():
            return redirect('/')
        session.clear()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Заполните все поля', 'danger')
            return render_template('login.html')
        user = get_db().execute('SELECT * FROM users WHERE username = ? AND password = ?',
                                (username, password)).fetchone()
        if user:
            if user['is_banned']:
                if user['ban_until']:
                    try:
                        if datetime.fromisoformat(user['ban_until']) > datetime.now():
                            flash(f'Заблокирован до {user["ban_until"][:16]}', 'danger')
                            return render_template('login.html')
                    except:
                        pass
                else:
                    flash('Заблокирован навсегда', 'danger')
                    return render_template('login.html')
            session['user_id'] = user['id']
            flash(f'Добро пожаловать, {user["username"]}!', 'success')
            return redirect('/')
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли', 'info')
    return redirect('/')


@app.route('/profile/<username>')
def profile(username):
    conn = get_db()
    puser = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if not puser:
        abort(404)
    posts = conn.execute(
        'SELECT p.*, u.username, u.avatar, c.name as channel_name, c.avatar as channel_avatar, '
        '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
        'FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN channels c ON p.channel_id = c.id '
        'WHERE p.user_id = ? AND p.is_story = 0 ORDER BY p.created_at DESC', (user['id'],)
    ).fetchall()
    active_stories = conn.execute(
        'SELECT * FROM posts WHERE user_id = ? AND is_story = 1 AND story_expires_at > datetime("now") '
        'ORDER BY created_at DESC', (user['id'],)
    ).fetchall()
    archived_stories = conn.execute(
        'SELECT * FROM posts WHERE user_id = ? AND is_story = 1 AND story_expires_at <= datetime("now") '
        'ORDER BY created_at DESC LIMIT 20', (user['id'],)
    ).fetchall()
    channels = conn.execute(
        'SELECT c.*, (SELECT COUNT(*) FROM channel_subscribers WHERE channel_id = c.id) as sub_count '
        'FROM channels c WHERE c.creator_id = ?', (user['id'],)
    ).fetchall()
    stats = {
        'posts': conn.execute('SELECT COUNT(*) as c FROM posts WHERE user_id = ? AND is_story = 0',
                              (user['id'],)).fetchone()['c'],
        'subscribers': conn.execute(
            'SELECT COUNT(*) as c FROM channel_subscribers cs JOIN channels ch ON cs.channel_id = ch.id '
            'WHERE ch.creator_id = ?', (user['id'],)
        ).fetchone()['c'],
        'channels': len(channels),
    }
    current_user = get_current_user()
    chat_messages = get_chat_messages() if current_user else []
    return render_template('profile/view.html', profile_user=user,
                           posts=enrich_posts(posts, current_user, conn),
                           active_stories=active_stories, archived_stories=archived_stories,
                           channels=channels, stats=stats, chat_messages=chat_messages)


@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            bio = request.form.get('bio', '')
            updates, params = ['bio = ?'], [bio]
            avatar = request.files.get('avatar')
            banner = request.files.get('banner')
            if avatar and avatar.filename and allowed_file(avatar.filename, 'photo'):
                updates.append('avatar = ?')
                params.append(save_file(avatar, 'avatar'))
            if banner and banner.filename and allowed_file(banner.filename, 'photo'):
                updates.append('banner = ?')
                params.append(save_file(banner, 'banner'))
            params.append(user['id'])
            conn.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
            flash('Профиль обновлён', 'success')
        elif action == 'change_password':
            if request.form.get('current_password') != user['password']:
                flash('Неверный пароль', 'danger')
            elif len(request.form.get('new_password', '')) < 4:
                flash('Минимум 4 символа', 'danger')
            elif request.form.get('new_password') != request.form.get('confirm_password'):
                flash('Пароли не совпадают', 'danger')
            else:
                conn.execute('UPDATE users SET password = ? WHERE id = ?',
                             (request.form['new_password'], user['id']))
                conn.commit()
                flash('Пароль изменён', 'success')
        elif action == 'change_theme':
            conn.execute(
                'UPDATE users SET theme=?, custom_bg=?, custom_secondary=?, custom_accent=?, custom_text=? WHERE id=?',
                (request.form.get('theme', 'dark'),
                 request.form.get('custom_bg', '#0d1117'),
                 request.form.get('custom_secondary', '#161b22'),
                 request.form.get('custom_accent', '#7D71D8'),
                 request.form.get('custom_text', '#f0f6fc'),
                 user['id']))
            conn.commit()
            flash('Тема обновлена', 'success')
        elif action == 'delete_account':
            if request.form.get('delete_password') != user['password']:
                flash('Неверный пароль', 'danger')
            else:
                conn.execute('DELETE FROM users WHERE id = ?', (user['id'],))
                conn.commit()
                session.clear()
                return redirect('/')
        return redirect('/profile/settings')
    return render_template('profile/settings.html', chat_messages=get_chat_messages())


# ══════════════════════════════════════════════
# CREATE CONTENT
# ══════════════════════════════════════════════

@app.route('/create/post', methods=['GET', 'POST'])
@login_required
def create_post():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        channel_id = request.form.get('channel_id')
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        if not content:
            flash('Введите текст', 'danger')
            return redirect('/create/post')
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        photos = request.files.getlist('photos')
        video = request.files.get('video')
        valid_photos = [p for p in photos if p and p.filename and allowed_file(p.filename, 'photo')]
        valid_video = video if video and video.filename and allowed_file(video.filename, 'video') else None
        file_path = None
        if valid_video:
            file_path = save_file(valid_video, 'video')
        elif valid_photos:
            file_path = save_file(valid_photos[0], 'photo')
        cursor = conn.execute(
            'INSERT INTO posts (user_id, channel_id, post_type, title, content, file_path, is_nsfw) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user['id'], channel_id or None, 'text', title or None, content, file_path, is_nsfw))
        post_id = cursor.lastrowid
        for i, photo in enumerate(valid_photos):
            path = file_path if i == 0 and not valid_video else save_file(photo, 'photo')
            conn.execute('INSERT INTO post_files (post_id, file_path, file_type) VALUES (?, ?, ?)',
                         (post_id, path, 'photo'))
        if valid_video:
            conn.execute('INSERT INTO post_files (post_id, file_path, file_type) VALUES (?, ?, ?)',
                         (post_id, file_path, 'video'))
        conn.commit()
        if content:
            tags = extract_hashtags(content)
            if tags:
                save_hashtags(post_id, tags)
        flash('Пост опубликован!', 'success')
        return redirect(f'/post/{post_id}')
    channels = conn.execute('SELECT * FROM channels WHERE creator_id = ?', (user['id'],)).fetchall()
    channel_id_preselect = request.args.get('channel_id', '')
    return render_template('create/post.html', channels=channels, chat_messages=get_chat_messages(),
                           channel_id_preselect=channel_id_preselect)


@app.route('/create/video', methods=['GET', 'POST'])
@login_required
def create_video():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        channel_id = request.form.get('channel_id')
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        video = request.files.get('video')
        if not video or not video.filename or not allowed_file(video.filename, 'video'):
            flash('Выберите видео', 'danger')
            return redirect('/create/video')
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        path = save_file(video, 'video')
        cursor = conn.execute(
            'INSERT INTO posts (user_id, channel_id, post_type, title, content, file_path, is_nsfw) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user['id'], channel_id or None, 'video', title or None, content, path, is_nsfw))
        post_id = cursor.lastrowid
        conn.execute('INSERT INTO post_files (post_id, file_path, file_type) VALUES (?, ?, ?)',
                     (post_id, path, 'video'))
        conn.commit()
        tags = extract_hashtags(content)
        if tags:
            save_hashtags(post_id, tags)
        flash('Видео опубликовано!', 'success')
        return redirect(f'/post/{post_id}')
    channels = conn.execute('SELECT * FROM channels WHERE creator_id = ?', (user['id'],)).fetchall()
    channel_id_preselect = request.args.get('channel_id', '')
    return render_template('create/video.html', channels=channels, chat_messages=get_chat_messages(),
                           channel_id_preselect=channel_id_preselect)


@app.route('/create/photo', methods=['GET', 'POST'])
@login_required
def create_photo():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        channel_id = request.form.get('channel_id')
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        photos = request.files.getlist('photos')
        valid = [p for p in photos if p and p.filename and allowed_file(p.filename, 'photo')]
        if not valid:
            flash('Выберите фото', 'danger')
            return redirect('/create/photo')
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        first = save_file(valid[0], 'photo')
        cursor = conn.execute(
            'INSERT INTO posts (user_id, channel_id, post_type, title, content, file_path, is_nsfw) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user['id'], channel_id or None, 'photo', title or None, content, first, is_nsfw))
        post_id = cursor.lastrowid
        for i, photo in enumerate(valid):
            path = first if i == 0 else save_file(photo, 'photo')
            conn.execute('INSERT INTO post_files (post_id, file_path, file_type) VALUES (?, ?, ?)',
                         (post_id, path, 'photo'))
        conn.commit()
        if content:
            tags = extract_hashtags(content)
            if tags:
                save_hashtags(post_id, tags)
        flash('Фото опубликовано!', 'success')
        return redirect(f'/post/{post_id}')
    channels = conn.execute('SELECT * FROM channels WHERE creator_id = ?', (user['id'],)).fetchall()
    channel_id_preselect = request.args.get('channel_id', '')
    return render_template('create/photo.html', channels=channels, chat_messages=get_chat_messages(),
                           channel_id_preselect=channel_id_preselect)


@app.route('/create/audio', methods=['GET', 'POST'])
@login_required
def create_audio():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        channel_id = request.form.get('channel_id')
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        audio = request.files.get('audio')
        if not audio or not audio.filename or not allowed_file(audio.filename, 'audio'):
            flash('Выберите аудио', 'danger')
            return redirect('/create/audio')
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        path = save_file(audio, 'audio')
        cursor = conn.execute(
            'INSERT INTO posts (user_id, channel_id, post_type, title, content, file_path, is_nsfw) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user['id'], channel_id or None, 'audio', title or None, content, path, is_nsfw))
        conn.commit()
        if content:
            tags = extract_hashtags(content)
            if tags:
                save_hashtags(cursor.lastrowid, tags)
        flash('Аудио опубликовано!', 'success')
        return redirect(f'/post/{cursor.lastrowid}')
    channels = conn.execute('SELECT * FROM channels WHERE creator_id = ?', (user['id'],)).fetchall()
    channel_id_preselect = request.args.get('channel_id', '')
    return render_template('create/audio.html', channels=channels, chat_messages=get_chat_messages(),
                           channel_id_preselect=channel_id_preselect)


@app.route('/create/article', methods=['GET', 'POST'])
@login_required
def create_article():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        channel_id = request.form.get('channel_id')
        is_nsfw = 1 if request.form.get('is_nsfw') else 0
        if not title or not content:
            flash('Заполните заголовок и текст', 'danger')
            return redirect('/create/article')
        if not is_nsfw:
            is_nsfw = 1 if check_nsfw_text(title + ' ' + content) else 0
        cursor = conn.execute(
            'INSERT INTO posts (user_id, channel_id, post_type, title, content, is_nsfw) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (user['id'], channel_id or None, 'article', title, content, is_nsfw))
        conn.commit()
        tags = extract_hashtags(content)
        if tags:
            save_hashtags(cursor.lastrowid, tags)
        flash('Статья опубликована!', 'success')
        return redirect(f'/post/{cursor.lastrowid}')
    channels = conn.execute('SELECT * FROM channels WHERE creator_id = ?', (user['id'],)).fetchall()
    channel_id_preselect = request.args.get('channel_id', '')
    return render_template('create/article.html', channels=channels, chat_messages=get_chat_messages(),
                           channel_id_preselect=channel_id_preselect)


@app.route('/create/story', methods=['GET', 'POST'])
@login_required
def create_story():
    user = get_current_user()
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        duration = max(1, min(48, int(request.form.get('duration', 24))))
        media = request.files.get('media')
        file_path = None
        if media and media.filename:
            ext = media.filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS['photo'] or ext in ALLOWED_EXTENSIONS['video']:
                file_path = save_file(media, 'story')
        expires = (datetime.now() + timedelta(hours=duration)).isoformat()
        cursor = conn.execute(
            'INSERT INTO posts (user_id, post_type, content, file_path, is_story, story_expires_at) '
            'VALUES (?, ?, ?, ?, 1, ?)',
            (user['id'], 'story', content, file_path, expires))
        get_db().commit()
        flash('История опубликована!', 'success')
        return redirect(f'/story/{cursor.lastrowid}')
    return render_template('create/story.html', chat_messages=get_chat_messages())


# ══════════════════════════════════════════════
# CHANNELS
# ══════════════════════════════════════════════

@app.route('/channel/create', methods=['GET', 'POST'])
@login_required
def create_channel():
    user = get_current_user()
    conn = get_db()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Введите название', 'danger')
            return redirect('/channel/create')
        avatar = request.files.get('avatar')
        banner = request.files.get('banner')
        ap = save_file(avatar, 'avatar') if avatar and avatar.filename and allowed_file(avatar.filename, 'photo') else None
        bp = save_file(banner, 'banner') if banner and banner.filename and allowed_file(banner.filename, 'photo') else None
        try:
            cursor = conn.execute(
                'INSERT INTO channels (name, description, avatar, banner, creator_id) VALUES (?, ?, ?, ?, ?)',
                (name, request.form.get('description', '').strip(), ap, bp, user['id']))
            conn.commit()
            flash('Канал создан!', 'success')
            return redirect(f'/channel/{cursor.lastrowid}')
        except sqlite3.IntegrityError:
            flash('Канал уже существует', 'danger')
    return render_template('channel/create.html', chat_messages=get_chat_messages())


@app.route('/channel/<int:channel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_channel(channel_id):
    user = get_current_user()
    conn = get_db()
    channel = conn.execute('SELECT * FROM channels WHERE id = ?', (channel_id,)).fetchone()
    if not channel:
        abort(404)
    if channel['creator_id'] != user['id'] and user['role'] != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(f'/channel/{channel_id}')
    if request.method == 'POST':
        updates, params = ['description = ?'], [request.form.get('description', '').strip()]
        name = request.form.get('name', '').strip()
        if name and name != channel['name']:
            updates.append('name = ?')
            params.append(name)
        avatar = request.files.get('avatar')
        banner = request.files.get('banner')
        if avatar and avatar.filename and allowed_file(avatar.filename, 'photo'):
            updates.append('avatar = ?')
            params.append(save_file(avatar, 'avatar'))
        if banner and banner.filename and allowed_file(banner.filename, 'photo'):
            updates.append('banner = ?')
            params.append(save_file(banner, 'banner'))
        params.append(channel_id)
        conn.execute(f'UPDATE channels SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
        flash('Канал обновлён', 'success')
        return redirect(f'/channel/{channel_id}')
    return render_template('channel/edit.html', channel=channel, chat_messages=get_chat_messages())


@app.route('/channels')
def channels_list():
    channels = get_db().execute(
        'SELECT c.*, u.username as creator_name, '
        '(SELECT COUNT(*) FROM channel_subscribers WHERE channel_id = c.id) as sub_count '
        'FROM channels c JOIN users u ON c.creator_id = u.id ORDER BY sub_count DESC'
    ).fetchall()
    user = get_current_user()
    return render_template('channel/list.html', channels=channels,
                           chat_messages=get_chat_messages() if user else [])


@app.route('/channel/<int:channel_id>')
def channel_view(channel_id):
    conn = get_db()
    channel = conn.execute(
        'SELECT c.*, u.username as creator_name FROM channels c JOIN users u ON c.creator_id = u.id '
        'WHERE c.id = ?', (channel_id,)
    ).fetchone()
    if not channel:
        abort(404)
    sub_count = conn.execute('SELECT COUNT(*) as c FROM channel_subscribers WHERE channel_id = ?',
                             (channel_id,)).fetchone()['c']
    posts = conn.execute(
        'SELECT p.*, u.username, u.avatar, c.name as channel_name, c.avatar as channel_avatar, '
        '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
        'FROM posts p JOIN users u ON p.user_id = u.id LEFT JOIN channels c ON p.channel_id = c.id '
        'WHERE p.channel_id = ? AND p.is_story = 0 ORDER BY p.created_at DESC', (channel_id,)
    ).fetchall()
    user = get_current_user()
    is_owner = user and channel['creator_id'] == user['id']
    is_subscribed = False
    if user and not is_owner:
        is_subscribed = conn.execute(
            'SELECT 1 FROM channel_subscribers WHERE user_id = ? AND channel_id = ?',
            (user['id'], channel_id)
        ).fetchone() is not None
    return render_template('channel/view.html', channel=channel, sub_count=sub_count,
                           posts=enrich_posts(posts, user, conn), is_subscribed=is_subscribed,
                           is_owner=is_owner, chat_messages=get_chat_messages() if user else [])


@app.route('/channel/<int:channel_id>/subscribe', methods=['POST'])
@login_required
def channel_subscribe(channel_id):
    user = get_current_user()
    conn = get_db()
    channel = conn.execute('SELECT * FROM channels WHERE id = ?', (channel_id,)).fetchone()
    if not channel:
        return jsonify({'error': 'not found'}), 404
    if channel['creator_id'] == user['id']:
        return jsonify({'error': 'Нельзя подписаться на свой канал'}), 403
    existing = conn.execute('SELECT 1 FROM channel_subscribers WHERE user_id = ? AND channel_id = ?',
                            (user['id'], channel_id)).fetchone()
    if existing:
        conn.execute('DELETE FROM channel_subscribers WHERE user_id = ? AND channel_id = ?',
                     (user['id'], channel_id))
        action = 'unsubscribed'
    else:
        conn.execute('INSERT INTO channel_subscribers (user_id, channel_id) VALUES (?, ?)',
                     (user['id'], channel_id))
        action = 'subscribed'
        add_notification(channel['creator_id'], 'subscribe',
                         f'{user["username"]} подписался на "{channel["name"]}"',
                         f'/channel/{channel_id}')
    conn.commit()
    new_count = conn.execute('SELECT COUNT(*) as c FROM channel_subscribers WHERE channel_id = ?',
                             (channel_id,)).fetchone()['c']
    return jsonify({'status': 'ok', 'action': action, 'sub_count': new_count})


# ══════════════════════════════════════════════
# REACTIONS & COMMENTS
# ══════════════════════════════════════════════

@app.route('/api/react/<int:post_id>', methods=['POST'])
@login_required
def react_to_post(post_id):
    user = get_current_user()
    data = request.get_json()
    rt = data.get('reaction_type') if data else None
    if rt not in REACTION_TYPES:
        return jsonify({'error': 'invalid'}), 400
    conn = get_db()
    existing = conn.execute('SELECT reaction_type FROM reactions WHERE user_id = ? AND post_id = ?',
                            (user['id'], post_id)).fetchone()
    if existing:
        if existing['reaction_type'] == rt:
            conn.execute('DELETE FROM reactions WHERE user_id = ? AND post_id = ?', (user['id'], post_id))
            action = 'removed'
        else:
            conn.execute('UPDATE reactions SET reaction_type = ? WHERE user_id = ? AND post_id = ?',
                         (rt, user['id'], post_id))
            action = 'changed'
    else:
        conn.execute('INSERT INTO reactions (user_id, post_id, reaction_type) VALUES (?, ?, ?)',
                     (user['id'], post_id, rt))
        action = 'added'
    conn.commit()
    if action == 'added':
        post = conn.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
        if post and post['user_id'] != user['id']:
            add_notification(post['user_id'], 'reaction',
                             f'{user["username"]} оценил ваш пост', f'/post/{post_id}')
    reactions = conn.execute(
        'SELECT reaction_type, COUNT(*) as count FROM reactions WHERE post_id = ? GROUP BY reaction_type',
        (post_id,)
    ).fetchall()
    ur = conn.execute('SELECT reaction_type FROM reactions WHERE user_id = ? AND post_id = ?',
                      (user['id'], post_id)).fetchone()
    return jsonify({
        'status': 'ok', 'action': action,
        'reactions': {r['reaction_type']: r['count'] for r in reactions},
        'user_reaction': ur['reaction_type'] if ur else None
    })


@app.route('/api/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    user = get_current_user()
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id')
    if not content:
        return jsonify({'error': 'empty'}), 400
    conn = get_db()
    # нельзя ответить на свой комментарий
    if parent_id:
        parent = conn.execute('SELECT user_id FROM comments WHERE id = ?', (parent_id,)).fetchone()
        if parent and parent['user_id'] == user['id']:
            return jsonify({'error': 'Нельзя ответить на свой комментарий'}), 400
    cursor = conn.execute(
        'INSERT INTO comments (post_id, user_id, parent_id, content) VALUES (?, ?, ?, ?)',
        (post_id, user['id'], parent_id or None, content))
    cid = cursor.lastrowid
    conn.commit()
    post = conn.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post and post['user_id'] != user['id']:
        add_notification(post['user_id'], 'comment',
                         f'{user["username"]} прокомментировал ваш пост', f'/post/{post_id}')
    c = conn.execute(
        'SELECT c.*, u.username, u.avatar FROM comments c JOIN users u ON c.user_id = u.id WHERE c.id = ?',
        (cid,)
    ).fetchone()
    comment_count = conn.execute('SELECT COUNT(*) as c FROM comments WHERE post_id = ?', (post_id,)).fetchone()['c']
    return jsonify({
        'status': 'ok',
        'comment': {
            'id': c['id'], 'content': c['content'], 'username': c['username'],
            'avatar': c['avatar'], 'created_at': c['created_at'],
            'parent_id': c['parent_id'], 'user_id': c['user_id'], 'replies': []
        },
        'comment_count': comment_count
    })


@app.route('/api/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    user = get_current_user()
    conn = get_db()
    comment = conn.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        return jsonify({'error': 'not found'}), 404
    if comment['user_id'] != user['id']:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json()
    content = data.get('content', '').strip() if data else ''
    if not content:
        return jsonify({'error': 'empty'}), 400
    conn.execute('UPDATE comments SET content = ? WHERE id = ?', (content, comment_id))
    conn.commit()
    return jsonify({'status': 'ok', 'content': content})


@app.route('/api/comments/<int:post_id>')
def get_comments(post_id):
    comments = get_db().execute(
        'SELECT c.*, u.username, u.avatar FROM comments c JOIN users u ON c.user_id = u.id '
        'WHERE c.post_id = ? ORDER BY c.created_at ASC', (post_id,)
    ).fetchall()

    def build(pid=None):
        r = []
        for c in comments:
            if c['parent_id'] == pid:
                d = dict(c)
                d['replies'] = build(c['id'])
                r.append(d)
        return r
    return jsonify(build())


# ══════════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════════

@app.route('/messages')
@login_required
def messages_inbox():
    user = get_current_user()
    conversations = get_db().execute('''
        SELECT c.*,
        CASE WHEN c.user1_id = ? THEN u2.username ELSE u1.username END as other_username,
        CASE WHEN c.user1_id = ? THEN u2.avatar ELSE u1.avatar END as other_avatar,
        CASE WHEN c.user1_id = ? THEN u2.id ELSE u1.id END as other_id,
        (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
        (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_id != ? AND is_read = 0) as unread_count
        FROM conversations c JOIN users u1 ON c.user1_id = u1.id JOIN users u2 ON c.user2_id = u2.id
        WHERE c.user1_id = ? OR c.user2_id = ? ORDER BY c.last_message_at DESC
    ''', (user['id'],) * 6).fetchall()
    return render_template('messages/inbox.html', conversations=conversations,
                           chat_messages=get_chat_messages())


@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def messages_chat(user_id):
    user = get_current_user()
    conn = get_db()
    other = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not other:
        abort(404)
    u1, u2 = min(user['id'], user_id), max(user['id'], user_id)
    conv = conn.execute('SELECT * FROM conversations WHERE user1_id = ? AND user2_id = ?', (u1, u2)).fetchone()

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        media = request.files.get('media')
        shared_post_id = request.form.get('shared_post_id')
        fp, ft = None, None
        if media and media.filename:
            ext = media.filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS.get('photo', set()):
                fp, ft = save_file(media, 'photo'), 'photo'
            elif ext in ALLOWED_EXTENSIONS.get('video', set()):
                fp, ft = save_file(media, 'video'), 'video'
            elif ext in ALLOWED_EXTENSIONS.get('audio', set()):
                fp, ft = save_file(media, 'audio'), 'audio'
        if content or fp or shared_post_id:
            if not conv:
                cursor = conn.execute('INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)', (u1, u2))
                cid = cursor.lastrowid
            else:
                cid = conv['id']
            conn.execute(
                'INSERT INTO messages (conversation_id, sender_id, content, file_path, file_type, shared_post_id) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (cid, user['id'], content or None, fp, ft, shared_post_id or None))
            conn.execute('UPDATE conversations SET last_message_at = CURRENT_TIMESTAMP WHERE id = ?', (cid,))
            conn.commit()
            add_notification(user_id, 'message',
                             f'{user["username"]} отправил вам сообщение',
                             f'/messages/{user["id"]}')
        return redirect(f'/messages/{user_id}')

    msgs = []
    if conv:
        conn.execute('UPDATE messages SET is_read = 1 WHERE conversation_id = ? AND sender_id != ?',
                     (conv['id'], user['id']))
        conn.commit()
        msgs = conn.execute(
            'SELECT m.*, u.username, u.avatar FROM messages m JOIN users u ON m.sender_id = u.id '
            'WHERE m.conversation_id = ? ORDER BY m.created_at ASC', (conv['id'],)
        ).fetchall()
    # подгрузим данные о shared_post
    msgs_data = []
    for msg in msgs:
        md = dict(msg)
        if md.get('shared_post_id'):
            shared = conn.execute(
                'SELECT p.id, p.title, p.post_type, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ?',
                (md['shared_post_id'],)
            ).fetchone()
            md['shared_post'] = dict(shared) if shared else None
        else:
            md['shared_post'] = None
        msgs_data.append(md)
    return render_template('messages/chat.html', other_user=other, messages=msgs_data,
                           chat_messages=get_chat_messages())


@app.route('/api/share_post/<int:post_id>', methods=['POST'])
@login_required
def share_post(post_id):
    """Поделиться постом в ЛС"""
    user = get_current_user()
    data = request.get_json()
    target_user_id = data.get('user_id') if data else None
    if not target_user_id:
        return jsonify({'error': 'no user'}), 400
    conn = get_db()
    target = conn.execute('SELECT id FROM users WHERE id = ?', (target_user_id,)).fetchone()
    if not target:
        return jsonify({'error': 'user not found'}), 404
    post = conn.execute('SELECT id, title FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        return jsonify({'error': 'post not found'}), 404
    u1, u2 = min(user['id'], target_user_id), max(user['id'], target_user_id)
    conv = conn.execute('SELECT id FROM conversations WHERE user1_id = ? AND user2_id = ?', (u1, u2)).fetchone()
    if not conv:
        cursor = conn.execute('INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)', (u1, u2))
        cid = cursor.lastrowid
    else:
        cid = conv['id']
    conn.execute(
        'INSERT INTO messages (conversation_id, sender_id, content, shared_post_id) VALUES (?, ?, ?, ?)',
        (cid, user['id'], f'Поделился постом: {post["title"] or "Без названия"}', post_id))
    conn.execute('UPDATE conversations SET last_message_at = CURRENT_TIMESTAMP WHERE id = ?', (cid,))
    conn.commit()
    return jsonify({'status': 'ok'})


# ══════════════════════════════════════════════
# GLOBAL CHAT
# ══════════════════════════════════════════════

@app.route('/api/global_chat', methods=['POST'])
@login_required
def send_global_chat():
    user = get_current_user()
    content = request.form.get('content', '').strip()
    if not content:
        return redirect(request.referrer or '/')
    conn = get_db()
    cd = conn.execute('SELECT cooldown_until FROM chat_cooldowns WHERE user_id = ?', (user['id'],)).fetchone()
    if cd and datetime.fromisoformat(cd['cooldown_until']) > datetime.now():
        flash(f'Подождите {(datetime.fromisoformat(cd["cooldown_until"]) - datetime.now()).seconds} сек', 'warning')
        return redirect(request.referrer or '/')
    recent = conn.execute(
        "SELECT COUNT(*) as c FROM global_chat WHERE user_id = ? AND created_at > datetime('now', '-5 seconds')",
        (user['id'],)
    ).fetchone()
    if recent['c'] >= CHAT_SPAM_MESSAGES:
        cu = (datetime.now() + timedelta(seconds=CHAT_COOLDOWN_SECONDS)).isoformat()
        conn.execute('INSERT OR REPLACE INTO chat_cooldowns (user_id, cooldown_until) VALUES (?, ?)',
                     (user['id'], cu))
        conn.commit()
        flash(f'Подождите {CHAT_COOLDOWN_SECONDS} сек', 'warning')
        return redirect(request.referrer or '/')
    conn.execute('INSERT INTO global_chat (user_id, content) VALUES (?, ?)', (user['id'], content))
    conn.commit()
    return redirect(request.referrer or '/')


@app.route('/api/global_chat/messages')
def get_global_chat_messages():
    msgs = get_chat_messages()
    return jsonify([{
        'id': m['id'], 'user_id': m['user_id'], 'username': m['username'],
        'avatar': m['avatar'], 'content': m['content'], 'created_at': m['created_at']
    } for m in msgs])


@app.route('/api/chat/cooldown')
@login_required
def get_chat_cooldown():
    user = get_current_user()
    cd = get_db().execute('SELECT cooldown_until FROM chat_cooldowns WHERE user_id = ?',
                          (user['id'],)).fetchone()
    if cd:
        try:
            ct = datetime.fromisoformat(cd['cooldown_until'])
            if ct > datetime.now():
                return jsonify({'cooldown': (ct - datetime.now()).seconds})
        except:
            pass
    return jsonify({'cooldown': 0})


# ══════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════

@app.route('/api/notifications/count')
@login_required
def get_notifications_count():
    user = get_current_user()
    return jsonify({'count': get_unread_notifications_count(user['id'])})


@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_notifications_read():
    user = get_current_user()
    conn = get_db()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user['id'],))
    conn.commit()
    return jsonify({'status': 'ok'})


@app.route('/notifications')
@login_required
def notifications():
    user = get_current_user()
    conn = get_db()
    notifs = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50',
                          (user['id'],)).fetchall()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user['id'],))
    conn.commit()
    return render_template('notifications.html', notifications=notifs, chat_messages=get_chat_messages())


# ══════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════

@app.route('/api/report', methods=['POST'])
@login_required
def submit_report():
    user = get_current_user()
    category = request.form.get('category')
    if category not in [c[0] for c in REPORT_CATEGORIES]:
        flash('Неверная категория', 'danger')
        return redirect(request.referrer or '/')
    get_db().execute(
        'INSERT INTO reports (reporter_id, post_id, comment_id, user_id, category, description) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (user['id'], request.form.get('post_id') or None, request.form.get('comment_id') or None,
         request.form.get('user_id') or None, category, request.form.get('description', '').strip()))
    get_db().commit()
    flash('Жалоба отправлена', 'success')
    return redirect(request.referrer or '/')


# ══════════════════════════════════════════════
# ADMIN — SINGLE PAGE
# ══════════════════════════════════════════════

@app.route('/admin')
@role_required('moderator')
def admin_panel():
    conn = get_db()
    tab = request.args.get('tab', 'dashboard')
    search = request.args.get('q', '').strip()
    report_status = request.args.get('status', 'pending')

    # stats для dashboard
    stats = {
        'users': conn.execute('SELECT COUNT(*) as c FROM users').fetchone()['c'],
        'posts': conn.execute('SELECT COUNT(*) as c FROM posts').fetchone()['c'],
        'channels': conn.execute('SELECT COUNT(*) as c FROM channels').fetchone()['c'],
        'reports_pending': conn.execute('SELECT COUNT(*) as c FROM reports WHERE status = "pending"').fetchone()['c'],
        'bans_active': conn.execute('SELECT COUNT(*) as c FROM users WHERE is_banned = 1').fetchone()['c'],
        'total_views': conn.execute('SELECT COALESCE(SUM(view_count), 0) as c FROM posts').fetchone()['c'],
    }

    # users
    if search:
        users = conn.execute('SELECT * FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY created_at DESC',
                             (f'%{search}%', f'%{search}%')).fetchall()
    else:
        users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()

    # reports
    reports = conn.execute(
        'SELECT r.*, reporter.username as reporter_name, p.title as post_title, '
        'c.content as comment_content, ru.username as reported_username '
        'FROM reports r JOIN users reporter ON r.reporter_id = reporter.id '
        'LEFT JOIN posts p ON r.post_id = p.id LEFT JOIN comments c ON r.comment_id = c.id '
        'LEFT JOIN users ru ON r.user_id = ru.id WHERE r.status = ? ORDER BY r.created_at DESC',
        (report_status,)
    ).fetchall()

    # bans
    bans = conn.execute(
        'SELECT ub.*, u.username as banned_username, a.username as admin_username '
        'FROM user_bans ub JOIN users u ON ub.user_id = u.id JOIN users a ON ub.banned_by = a.id '
        'ORDER BY ub.created_at DESC'
    ).fetchall()

    # logs
    logs = conn.execute(
        'SELECT al.*, u.username as admin_username FROM admin_logs al JOIN users u ON al.admin_id = u.id '
        'ORDER BY al.created_at DESC LIMIT 100'
    ).fetchall()

    # analytics
    top_posts = conn.execute(
        'SELECT p.*, u.username, p.view_count, '
        '(SELECT COUNT(*) FROM reactions WHERE post_id = p.id) as reaction_count, '
        '(SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count '
        'FROM posts p JOIN users u ON p.user_id = u.id WHERE p.is_story = 0 '
        'ORDER BY p.view_count DESC LIMIT 20'
    ).fetchall()
    top_users = conn.execute(
        'SELECT u.username, u.avatar, '
        '(SELECT COUNT(*) FROM posts WHERE user_id = u.id) as post_count, '
        '(SELECT COALESCE(SUM(view_count), 0) FROM posts WHERE user_id = u.id) as total_views '
        'FROM users u ORDER BY total_views DESC LIMIT 20'
    ).fetchall()

    recent_users = conn.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT 5').fetchall()

    return render_template('admin/panel.html',
                           tab=tab, stats=stats, users=users, reports=reports,
                           bans=bans, logs=logs, top_posts=top_posts, top_users=top_users,
                           recent_users=recent_users, search=search,
                           current_status=report_status,
                           chat_messages=get_chat_messages())


@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@role_required('admin')
def admin_change_role(user_id):
    admin = get_current_user()
    new_role = request.form.get('role')
    if new_role not in ROLES:
        flash('Неверная роль', 'danger')
        return redirect('/admin?tab=users')
    target = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not target or target['id'] == admin['id']:
        flash('Ошибка', 'danger')
        return redirect('/admin?tab=users')
    get_db().execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    get_db().commit()
    log_admin_action(admin['id'], 'change_role', 'user', user_id, new_role)
    flash(f'Роль: {new_role}', 'success')
    return redirect('/admin?tab=users')


@app.route('/admin/users/<int:user_id>/ban', methods=['POST'])
@role_required('moderator')
def admin_ban_user(user_id):
    admin = get_current_user()
    conn = get_db()
    target = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not target or ROLES.get(target['role'], 0) >= ROLES.get(admin['role'], 0):
        flash('Ошибка', 'danger')
        return redirect('/admin?tab=users')
    ban_type = request.form.get('ban_type')
    reason = request.form.get('reason', '').strip()
    if ban_type == 'permanent':
        if admin['role'] != 'admin':
            flash('Только админ', 'danger')
            return redirect('/admin?tab=users')
        conn.execute('UPDATE users SET is_banned = 1, ban_until = NULL, ban_reason = ? WHERE id = ?',
                     (reason, user_id))
        ban_until = None
    else:
        hours = int(request.form.get('duration', 24))
        ban_until = (datetime.now() + timedelta(hours=hours)).isoformat()
        conn.execute('UPDATE users SET is_banned = 1, ban_until = ?, ban_reason = ? WHERE id = ?',
                     (ban_until, reason, user_id))
    conn.execute(
        'INSERT INTO user_bans (user_id, banned_by, reason, is_permanent, ban_until) VALUES (?, ?, ?, ?, ?)',
        (user_id, admin['id'], reason, 1 if ban_type == 'permanent' else 0, ban_until))
    conn.commit()
    log_admin_action(admin['id'], 'ban_user', 'user', user_id, f'{ban_type}: {reason}')
    flash('Забанен', 'success')
    return redirect('/admin?tab=users')


@app.route('/admin/users/<int:user_id>/unban', methods=['POST'])
@role_required('moderator')
def admin_unban_user(user_id):
    admin = get_current_user()
    get_db().execute('UPDATE users SET is_banned = 0, ban_until = NULL, ban_reason = NULL WHERE id = ?', (user_id,))
    get_db().commit()
    log_admin_action(admin['id'], 'unban_user', 'user', user_id)
    flash('Разбанен', 'success')
    return redirect('/admin?tab=users')


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_user(user_id):
    admin = get_current_user()
    target = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not target or target['id'] == admin['id'] or target['role'] == 'admin':
        flash('Ошибка', 'danger')
        return redirect('/admin?tab=users')
    get_db().execute('DELETE FROM users WHERE id = ?', (user_id,))
    get_db().commit()
    log_admin_action(admin['id'], 'delete_user', 'user', user_id, target['username'])
    flash('Удалён', 'success')
    return redirect('/admin?tab=users')


@app.route('/admin/reports/<int:report_id>/handle', methods=['POST'])
@role_required('moderator')
def admin_handle_report(report_id):
    admin = get_current_user()
    conn = get_db()
    report = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
    if not report:
        flash('Не найдена', 'danger')
        return redirect('/admin?tab=reports')
    action = request.form.get('action')
    if action == 'approve':
        if report['post_id']:
            conn.execute('DELETE FROM posts WHERE id = ?', (report['post_id'],))
        if report['comment_id']:
            conn.execute('DELETE FROM comments WHERE id = ?', (report['comment_id'],))
        status = 'approved'
    else:
        status = 'rejected'
    conn.execute('UPDATE reports SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP WHERE id = ?',
                 (status, admin['id'], report_id))
    conn.commit()
    log_admin_action(admin['id'], f'report_{action}', 'report', report_id)
    flash('Обработано', 'success')
    return redirect('/admin?tab=reports')


@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    user = get_current_user()
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        flash('Не найден', 'danger')
        return redirect('/')
    if post['user_id'] != user['id'] and user['role'] not in ['admin', 'moderator']:
        flash('Недостаточно прав', 'danger')
        return redirect('/')
    for table in ['post_files', 'comments', 'reactions', 'post_views', 'post_hashtags']:
        conn.execute(f'DELETE FROM {table} WHERE post_id = ?', (post_id,))
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    if user['role'] in ['admin', 'moderator'] and post['user_id'] != user['id']:
        log_admin_action(user['id'], 'delete_post', 'post', post_id)
    flash('Удалён', 'success')
    return redirect('/')


@app.route('/admin/comments/<int:comment_id>/delete', methods=['POST'])
@role_required('moderator')
def admin_delete_comment(comment_id):
    admin = get_current_user()
    get_db().execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    get_db().commit()
    log_admin_action(admin['id'], 'delete_comment', 'comment', comment_id)
    flash('Удалён', 'success')
    return redirect(request.referrer or '/')


@app.route('/admin/channels/<int:channel_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_channel(channel_id):
    admin = get_current_user()
    get_db().execute('DELETE FROM channels WHERE id = ?', (channel_id,))
    get_db().commit()
    log_admin_action(admin['id'], 'delete_channel', 'channel', channel_id)
    flash('Удалён', 'success')
    return redirect('/channels')


# ══════════════════════════════════════════════
# STATIC & PAGES
# ══════════════════════════════════════════════

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/user_agreement')
def user_agreement():
    return render_template('user_agreement.html',
                        chat_messages=get_chat_messages() if get_current_user() else [])


@app.route('/about')
def about():
    return render_template('about.html',
                        chat_messages=get_chat_messages() if get_current_user() else [])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500


init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1324)