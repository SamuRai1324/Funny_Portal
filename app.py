from flask import Flask, request, redirect, session, flash, render_template, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'
DATABASE = 'Web_DB.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                creator_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users(id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER,
                post_type TEXT DEFAULT 'text',
                title TEXT,
                content TEXT NOT NULL,
                media_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (channel_id) REFERENCES channels(id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, post_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                parent_id INTEGER,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parent_id) REFERENCES comments(id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        admin = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
        if not admin:
            conn.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                ('admin', 'admin@site.com', 'admin123', 'admin')
            )
        conn.commit()


init_db()


def get_current_user():
    if 'user_id' not in session:
        return None
    with get_db() as conn:
        return conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()


def get_chat_messages():
    with get_db() as conn:
        return conn.execute('''
            SELECT m.*, u.username 
            FROM messages m 
            JOIN users u ON m.user_id = u.id 
            ORDER BY m.id ASC
        ''').fetchall()


def get_comments_dict():
    comments_dict = {}
    with get_db() as conn:
        all_comments = conn.execute('''
            SELECT c.*, u.username 
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            ORDER BY c.id ASC
        ''').fetchall()
        for c in all_comments:
            pid = c['parent_id'] or 0
            if pid not in comments_dict:
                comments_dict[pid] = []
            comments_dict[pid].append(c)
    return comments_dict


@app.route('/')
def index():
    current_user = get_current_user()
    current_tab = request.args.get('tab', 'all')
    search_query = request.args.get('q', '').strip()

    posts = []
    channels = []
    chat_messages = []
    comments_dict = {}

    if current_user:
        chat_messages = get_chat_messages()
        comments_dict = get_comments_dict()

        with get_db() as conn:
            if current_tab == 'channels' and not search_query:
                channels = conn.execute('''
                    SELECT c.*, u.username as creator_name 
                    FROM channels c 
                    LEFT JOIN users u ON c.creator_id = u.id 
                    ORDER BY c.id DESC
                ''').fetchall()
            else:
                query = '''
                    SELECT p.*, u.username 
                    FROM posts p 
                    JOIN users u ON p.user_id = u.id 
                    WHERE 1=1
                '''
                params = []

                if search_query:
                    query += ' AND (p.title LIKE ? OR p.content LIKE ?)'
                    params.extend([f'%{search_query}%', f'%{search_query}%'])
                elif current_tab != 'all':
                    query += ' AND p.post_type = ?'
                    params.append(current_tab)

                query += ' ORDER BY p.id DESC'
                posts = conn.execute(query, params).fetchall()

    return render_template(
        'index.html',
        current_user=current_user,
        posts=posts,
        channels=channels,
        current_tab=current_tab,
        chat_messages=chat_messages,
        comments_dict=comments_dict
    )


@app.route('/user_agreement')
def user_agreement():
    current_user = get_current_user()
    chat_messages = get_chat_messages() if current_user else []
    return render_template(
        'user_agreement.html',
        current_user=current_user,
        chat_messages=chat_messages
    )


@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect('/login')

    post_type = request.form.get('post_type', 'text')
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not content:
        flash('Содержание поста не может быть пустым', 'danger')
        return redirect('/')

    with get_db() as conn:
        conn.execute(
            'INSERT INTO posts (user_id, post_type, title, content) VALUES (?, ?, ?, ?)',
            (session['user_id'], post_type, title if title else None, content)
        )
        conn.commit()

    flash('Пост опубликован!', 'success')
    return redirect('/')


@app.route('/create_channel', methods=['POST'])
def create_channel():
    if 'user_id' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect('/login')

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Название канала не может быть пустым', 'danger')
        return redirect('/?tab=channels')

    try:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO channels (name, description, creator_id) VALUES (?, ?, ?)',
                (name, description, session['user_id'])
            )
            conn.commit()
        flash('Канал создан!', 'success')
    except sqlite3.IntegrityError:
        flash('Канал с таким названием уже существует', 'danger')

    return redirect('/?tab=channels')


@app.route('/send_chat', methods=['POST'])
def send_chat():
    if 'user_id' not in session:
        return redirect('/login')

    content = request.form.get('content', '').strip()
    if content:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO messages (user_id, content) VALUES (?, ?)',
                (session['user_id'], content)
            )
            conn.commit()

    return redirect(request.referrer or '/')


@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect('/login')

    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', '0')

    try:
        parent_id = int(parent_id)
    except ValueError:
        parent_id = 0

    if content:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO comments (post_id, user_id, parent_id, content) VALUES (?, ?, ?, ?)',
                (post_id, session['user_id'], parent_id if parent_id > 0 else None, content)
            )
            conn.commit()

    return redirect('/')


@app.route('/repost/<int:post_id>', methods=['POST'])
def repost(post_id):
    if 'user_id' not in session:
        return redirect('/login')

    with get_db() as conn:
        post = conn.execute(
            'SELECT title, content FROM posts WHERE id = ?',
            (post_id,)
        ).fetchone()

        if post:
            preview = post['title'] if post['title'] else post['content'][:50]
            if len(post['content']) > 50 and not post['title']:
                preview += '...'
            msg = f"📣 Поделился постом: {preview}"
            conn.execute(
                'INSERT INTO messages (user_id, content) VALUES (?, ?)',
                (session['user_id'], msg)
            )
            conn.commit()
            flash('Пост отправлен в чат!', 'success')

    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('Заполните все поля', 'danger')
        elif len(username) < 3:
            flash('Логин должен содержать минимум 3 символа', 'danger')
        elif len(password) < 4:
            flash('Пароль должен содержать минимум 4 символа', 'danger')
        elif password != confirm_password:
            flash('Пароли не совпадают', 'danger')
        elif '@' not in email:
            flash('Введите корректный email', 'danger')
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, password)
                    )
                    conn.commit()
                flash('Регистрация успешна! Теперь войдите в аккаунт.', 'success')
                return redirect('/login')
            except sqlite3.IntegrityError:
                flash('Пользователь с таким логином или email уже существует', 'danger')

    return render_template('register.html', current_user=None, chat_messages=[])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Заполните все поля', 'danger')
        else:
            with get_db() as conn:
                user = conn.execute(
                    'SELECT * FROM users WHERE username = ? AND password = ?',
                    (username, password)
                ).fetchone()

                if user:
                    session['user_id'] = user['id']
                    flash(f'Добро пожаловать, {user["username"]}!', 'success')
                    return redirect('/')
                else:
                    flash('Неверный логин или пароль', 'danger')

    return render_template('login.html', current_user=None, chat_messages=[])


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта', 'info')
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    current_user = get_current_user()
    chat_messages = get_chat_messages() if current_user else []
    return render_template(
        'base.html',
        current_user=current_user,
        chat_messages=chat_messages,
        error_message='Страница не найдена (404)'
    ), 404


@app.errorhandler(500)
def internal_error(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=1324, host='0.0.0.0')