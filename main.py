from flask import Flask, request, redirect, session, flash, render_template_string, render_template
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'
DATABASE = 'app4.db'


# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'user')''')

        conn.execute('''CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, description TEXT, creator_id INTEGER)''')

        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, channel_id INTEGER, 
            post_type TEXT DEFAULT 'text', title TEXT, content TEXT, media_url TEXT, 
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

        conn.execute(
            '''CREATE TABLE IF NOT EXISTS likes (user_id INTEGER, post_id INTEGER, PRIMARY KEY (user_id, post_id))''')

        conn.execute('''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, user_id INTEGER, 
            parent_id INTEGER, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

        conn.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

        admin = conn.execute('SELECT id FROM users WHERE username = "admin"').fetchone()
        if not admin:
            conn.execute(
                'INSERT INTO users (username, email, password, role) VALUES ("admin", "admin@site.com", "admin123", "admin")')
        conn.commit()


init_db()


def get_current_user():
    if 'user_id' not in session: return None
    with get_db() as conn:
        return conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()


# --- ЕДИНЫЙ ШАБЛОН ДИЗАЙНА ---
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>MyApp</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, sans-serif; }
        body { background: #0d1117; color: #eee; min-height: 100vh; display: flex; flex-direction: column; overflow-y: scroll; }
        a { color: #58a6ff; text-decoration: none; }
        nav { background: #161b22; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; position: sticky; top: 0; z-index: 100; }
        .search-bar { display: flex; width: 400px; }
        .search-bar input { margin: 0; border-radius: 20px 0 0 20px; border-right: none; padding: 0.6rem 1rem; flex: 1; }
        .search-bar button { background: #21262d; border: 1px solid #30363d; border-radius: 0 20px 20px 0; padding: 0 1.2rem; color: #8b949e; cursor: pointer; }
        .btn { background: #238636; color: #fff; padding: 0.6rem 1.2rem; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #2ea043; }
        .layout { display: flex; max-width: 1400px; margin: 0 auto; padding: 2rem; gap: 2rem; align-items: flex-start; flex: 1; width: 100%; }
        .content { flex: 1; width: 100%; min-width: 0; }
        .sidebar { width: 350px; flex-shrink: 0; position: sticky; top: 80px; }
        .box { background: #161b22; padding: 1.5rem; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 1.5rem; }
        input, textarea, select { width: 100%; padding: 0.8rem; margin-bottom: 0.5rem; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #eee; font-size: 1rem; }
        input:focus, textarea:focus { outline: none; border-color: #58a6ff; }
        .alert { padding: 1rem; margin-bottom: 1rem; border-radius: 6px; font-weight: bold; text-align: center; }
        .alert.danger { background: #da3633; color: white; }
        .alert.success { background: #238636; color: white; }
        .tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
        .tab { padding: 0.5rem 1rem; background: #21262d; border-radius: 20px; color: #fff; border: 1px solid #30363d; font-size: 0.9rem; }
        .tab.active { background: #eee; color: #111; border-color: #eee; }
        .action-btn { background: transparent; border: none; color: #8b949e; cursor: pointer; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.9rem; }
        .action-btn:hover { background: #21262d; color: #c9d1d9; }
        /* Мессенджер */
        .chat-box { height: 500px; display: flex; flex-direction: column; padding: 0; overflow: hidden; }
        .chat-header { padding: 1rem; background: #21262d; border-bottom: 1px solid #30363d; font-weight: bold; text-align: center; }
        .chat-messages { flex: 1; padding: 1rem; overflow-y: auto; display: flex; flex-direction: column; gap: 0.5rem; }
        .msg { background: #21262d; padding: 0.6rem; border-radius: 8px; font-size: 0.9rem; word-break: break-word; }
        .chat-input { padding: 1rem; border-top: 1px solid #30363d; display: flex; gap: 0.5rem; }
        .chat-input input { margin: 0; border-radius: 20px; }
        .chat-input button { padding: 0 1rem; border-radius: 50%; width: 45px; }
        /* Комментарии */
        .comment-thread { margin-left: 20px; border-left: 2px solid #30363d; padding-left: 15px; margin-top: 10px; }
        .comment-box { margin-bottom: 10px; font-size: 0.95rem; }
        details { margin-top: 1rem; background: #0d1117; padding: 1rem; border-radius: 8px; border: 1px solid #30363d; }
        summary { cursor: pointer; color: #58a6ff; font-weight: bold; margin-bottom: 10px; outline: none; }
        /* Подвал */
        footer { text-align: center; padding: 2rem; margin-top: auto; border-top: 1px solid #30363d; background: #0d1117; }
        footer a { color: #8b949e; font-size: 0.9rem; text-decoration: underline; }
        footer a:hover { color: #58a6ff; }
    </style>
</head>
<body>
    <nav>
        <h2><a href="/" style="color: white;">MyApp</a></h2>

        <form class="search-bar" action="/" method="GET">
            <input type="text" name="q" placeholder="Поиск постов...">
            <button type="submit">🔍</button>
        </form>

        <div style="display: flex; gap: 15px; align-items: center;">
            {% if user %}
                <span style="color: #8b949e;">Привет, {{ user.username }}!</span>
                <a href="/logout" style="color: #da3633; font-weight: bold;">Выйти</a>
            {% else %}
                <a href="/login">Вход</a>
                <a href="/register" class="btn" style="padding: 0.4rem 1rem;">Регистрация</a>
            {% endif %}
        </div>
    </nav>

    <div class="layout">
        <main class="content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for cat, msg in messages %}<div class="alert {{ cat }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            {CONTENT_PLACEHOLDER}
        </main>

        {% if user %}
        <aside class="sidebar">
            <div class="box chat-box">
                <div class="chat-header">🌐 Общий чат</div>
                <div class="chat-messages" id="chat-messages">
                    {% for m in chat_messages %}
                        <div class="msg">
                            <b style="color: #58a6ff;">{{ m.username }}:</b> {{ m.content }}
                        </div>
                    {% else %}
                        <p style="color: #8b949e; text-align: center; font-size: 0.8rem;">Сообщений пока нет</p>
                    {% endfor %}
                </div>
                <form class="chat-input" action="/send_chat" method="POST">
                    <input type="text" name="content" placeholder="Написать..." required autocomplete="off">
                    <button type="submit" class="btn">➤</button>
                </form>
            </div>
        </aside>
        <script>
            var chat = document.getElementById("chat-messages");
            chat.scrollTop = chat.scrollHeight;
        </script>
        {% endif %}
    </div>

    <!-- ПОДВАЛ (Пользовательское соглашение) -->
    <footer>
        <a href="/user_agreement">Пользовательское соглашение</a>
        <p style="color: #444; font-size: 0.8rem; margin-top: 2px;">&copy; 2024 MyApp. Все права защищены.</p>
    </footer>
</body>
</html>
'''

MACRO_COMMENTS = '''
{% macro render_comments(parent_id, post_id) %}
    {% if comments_dict[parent_id] %}
        <div class="comment-thread">
        {% for c in comments_dict[parent_id] %}
            <div class="comment-box">
                <b style="color: #8b949e;">{{ c.username }}</b> <span style="font-size: 0.7rem; color: #444;">{{ c.created_at[:16] }}</span><br>
                {{ c.content }}
                <details style="padding: 0; border: none; background: transparent; margin-top: 5px;">
                    <summary style="font-size: 0.8rem; color: #8b949e; margin: 0;">Ответить</summary>
                    <form action="/add_comment/{{ post_id }}" method="POST" style="margin-top: 5px; display: flex; gap: 5px;">
                        <input type="hidden" name="parent_id" value="{{ c.id }}">
                        <input type="text" name="content" placeholder="Ваш ответ..." required style="padding: 0.4rem; margin: 0;">
                        <button type="submit" class="btn" style="padding: 0.4rem 0.8rem;">✓</button>
                    </form>
                </details>
                {{ render_comments(c.id, post_id) }}
            </div>
        {% endfor %}
        </div>
    {% endif %}
{% endmacro %}
'''


# --- МАРШРУТЫ ---

@app.route('/')
def index():
    user = get_current_user()
    current_tab = request.args.get('tab', 'all')
    search_query = request.args.get('q', '').strip()

    posts, channels, chat_messages = [], [], []
    comments_dict = {}

    with get_db() as conn:
        if user:
            chat_messages = conn.execute(
                'SELECT m.*, u.username FROM messages m JOIN users u ON m.user_id = u.id ORDER BY m.id ASC').fetchall()
            all_comments = conn.execute(
                'SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id ORDER BY c.id ASC').fetchall()
            for c in all_comments:
                pid = c['parent_id'] or 0
                if pid not in comments_dict: comments_dict[pid] = []
                comments_dict[pid].append(c)

        if current_tab == 'channels' and not search_query:
            channels = conn.execute('SELECT * FROM channels ORDER BY id DESC').fetchall()
        else:
            query = "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE 1=1"
            params = []

            if search_query:
                query += " AND (p.title LIKE ? OR p.content LIKE ?)"
                params.extend([f'%{search_query}%', f'%{search_query}%'])
            elif current_tab != 'all':
                query += " AND p.post_type = ?"
                params.append(current_tab)

            query += " ORDER BY p.id DESC"
            posts = conn.execute(query, params).fetchall()

    content = MACRO_COMMENTS + '''
        {% if user %}
            <div class="tabs">
                <a href="/?tab=all" class="tab {% if current_tab == 'all' and not request.args.get('q') %}active{% endif %}">Все посты</a>
                <a href="/?tab=text" class="tab {% if current_tab == 'text' %}active{% endif %}">Новости</a>
                <a href="/?tab=video" class="tab {% if current_tab == 'video' %}active{% endif %}">Видео</a>
                <a href="/?tab=short" class="tab {% if current_tab == 'short' %}active{% endif %}">Shorts</a>
                <a href="/?tab=channels" class="tab {% if current_tab == 'channels' %}active{% endif %}">Каналы</a>
            </div>

            {% if request.args.get('q') %}
                <h3 style="margin-bottom: 1rem;">Результаты поиска: "{{ request.args.get('q') }}" <a href="/" style="font-size: 0.9rem;">(Сбросить)</a></h3>
            {% else %}
                <details class="box" style="border: 1px dashed #58a6ff; margin-top: 0; padding: 1rem;">
                    <summary>➕ Написать пост / Создать канал</summary>
                    <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                        <form action="/create_post" method="POST" style="flex: 1;">
                            <h4>Новый пост</h4>
                            <select name="post_type">
                                <option value="text">Новость (Текст)</option>
                                <option value="video">Видео</option>
                                <option value="short">Shorts</option>
                            </select>
                            <input type="text" name="title" placeholder="Заголовок">
                            <textarea name="content" placeholder="Описание..." required></textarea>
                            <button type="submit" class="btn">Опубликовать</button>
                        </form>
                        <form action="/create_channel" method="POST" style="flex: 1; border-left: 1px solid #30363d; padding-left: 2rem;">
                            <h4>Новый канал</h4>
                            <input type="text" name="name" placeholder="Название канала" required>
                            <textarea name="description" placeholder="Описание канала..." required></textarea>
                            <button type="submit" class="btn">Создать канал</button>
                        </form>
                    </div>
                </details>
            {% endif %}

            {% if current_tab == 'channels' and not request.args.get('q') %}
                {% for c in channels %}
                    <div class="box">
                        <h4 style="color: #58a6ff; font-size: 1.4rem;">{{ c.name }}</h4>
                        <p style="color: #8b949e; margin-top: 5px;">{{ c.description }}</p>
                    </div>
                {% else %}
                    <p style="text-align: center; color: #8b949e;">Каналов пока нет.</p>
                {% endfor %}
            {% else %}
                {% for p in posts %}
                    <div class="box">
                        <div style="margin-bottom: 10px;">
                            <span style="font-weight: bold;">{{ p.username }}</span>
                            <span style="background: #30363d; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 10px;">{{ p.post_type|upper }}</span>
                        </div>
                        {% if p.title %}<h3 style="margin-bottom: 10px;">{{ p.title }}</h3>{% endif %}
                        <p style="line-height: 1.5;">{{ p.content }}</p>

                        <div style="margin-top: 15px; display: flex; gap: 10px; border-top: 1px solid #30363d; padding-top: 10px;">
                            <form action="/repost/{{ p.id }}" method="POST" style="margin: 0;">
                                <button type="submit" class="action-btn">↪️ В чат</button>
                            </form>
                        </div>

                        <details>
                            <summary>💬 Комментарии</summary>
                            <form action="/add_comment/{{ p.id }}" method="POST" style="display: flex; gap: 10px; margin-bottom: 15px;">
                                <input type="hidden" name="parent_id" value="0">
                                <input type="text" name="content" placeholder="Написать комментарий..." required style="margin: 0;">
                                <button type="submit" class="btn">Отправить</button>
                            </form>
                            {{ render_comments(0, p.id) }}
                        </details>
                    </div>
                {% else %}
                    <p style="text-align: center; color: #8b949e; padding: 3rem;">Постов не найдено.</p>
                {% endfor %}
            {% endif %}

        {% else %}
            <div style="text-align: center; margin-top: 50px;">
                <h1>Добро пожаловать в MyApp!</h1>
                <p style="color: #8b949e; margin: 20px 0;">Войдите или зарегистрируйтесь, чтобы видеть ленту и писать в чат.</p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <a href="/login" class="btn">Войти в аккаунт</a>
                    <a href="/register" class="btn" style="background: transparent; border: 1px solid #30363d;">Создать аккаунт</a>
                </div>
            </div>
        {% endif %}
    '''
    return render_template_string(BASE_TEMPLATE.replace('{CONTENT_PLACEHOLDER}', content),
                                  user=user, posts=posts, channels=channels, current_tab=current_tab,
                                  chat_messages=chat_messages, comments_dict=comments_dict)


# --- НОВЫЙ МАРШРУТ: ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ ---
@app.route('/user_agreement')
def user_agreement():
    # Мы используем умную защиту. Если файла нет, выдастся красивая заглушка!
    try:
        return render_template('user_agreement.html')
    except Exception:
        return '''
        <body style="background: #0d1117; color: #eee; font-family: sans-serif; text-align: center; padding-top: 100px;">
            <h1 style="color: #da3633;">Ошибка: Файл не найден!</h1>
            <p>Вы забыли создать файл <b>user_agreement.html</b> внутри папки <b>templates</b>.</p>
            <p>Создайте его, и здесь появится текст соглашения.</p>
            <br>
            <a href="/" style="color: #58a6ff; text-decoration: none;">Вернуться на главную</a>
        </body>
        '''


# --- ОСТАЛЬНЫЕ ФУНКЦИИ ---
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session: return redirect('/')
    with get_db() as conn:
        conn.execute('INSERT INTO posts (user_id, post_type, title, content) VALUES (?, ?, ?, ?)',
                     (session['user_id'], request.form.get('post_type'), request.form.get('title'),
                      request.form.get('content')))
        conn.commit()
    flash('Опубликовано!', 'success')
    return redirect('/')


@app.route('/create_channel', methods=['POST'])
def create_channel():
    if 'user_id' not in session: return redirect('/')
    with get_db() as conn:
        conn.execute('INSERT INTO channels (name, description, creator_id) VALUES (?, ?, ?)',
                     (request.form.get('name'), request.form.get('description'), session['user_id']))
        conn.commit()
    flash('Канал создан!', 'success')
    return redirect('/?tab=channels')


@app.route('/send_chat', methods=['POST'])
def send_chat():
    if 'user_id' not in session: return redirect('/')
    content = request.form.get('content', '').strip()
    if content:
        with get_db() as conn:
            conn.execute('INSERT INTO messages (user_id, content) VALUES (?, ?)', (session['user_id'], content))
            conn.commit()
    return redirect('/')


@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session: return redirect('/')
    content = request.form.get('content', '').strip()
    parent_id = int(request.form.get('parent_id', 0))
    if content:
        with get_db() as conn:
            conn.execute('INSERT INTO comments (post_id, user_id, parent_id, content) VALUES (?, ?, ?, ?)',
                         (post_id, session['user_id'], parent_id if parent_id > 0 else None, content))
            conn.commit()
    return redirect('/')


@app.route('/repost/<int:post_id>', methods=['POST'])
def repost(post_id):
    if 'user_id' not in session: return redirect('/')
    with get_db() as conn:
        post = conn.execute('SELECT title, content FROM posts WHERE id = ?', (post_id,)).fetchone()
        if post:
            msg = f"📣 Поделился постом: {post['title'] or post['content'][:30] + '...'}"
            conn.execute('INSERT INTO messages (user_id, content) VALUES (?, ?)', (session['user_id'], msg))
            conn.commit()
            flash('Пост отправлен в чат!', 'success')
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if len(password) < 4:
            flash('Пароль слишком короткий!', 'danger')
        else:
            try:
                with get_db() as conn:
                    conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                                 (username, f"{username}@test.com", password))
                    conn.commit()
                flash('Регистрация успешна!', 'success')
                return redirect('/login')
            except:
                flash('Логин занят!', 'danger')

    content = '<div class="box" style="max-width: 400px; margin: 0 auto; text-align: center;"><h2>Регистрация</h2><form method="POST" style="margin-top: 1rem;"><input type="text" name="username" placeholder="Логин" required><input type="password" name="password" placeholder="Пароль" required><button type="submit" class="btn" style="width: 100%;">Создать</button></form></div>'
    return render_template_string(BASE_TEMPLATE.replace('{CONTENT_PLACEHOLDER}', content), user=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                                (request.form.get('username'), request.form.get('password'))).fetchone()
            if user:
                session['user_id'] = user['id']
                return redirect('/')
            else:
                flash('Неверный логин или пароль!', 'danger')

    content = '<div class="box" style="max-width: 400px; margin: 0 auto; text-align: center;"><h2>Вход</h2><form method="POST" style="margin-top: 1rem;"><input type="text" name="username" placeholder="Логин" required><input type="password" name="password" placeholder="Пароль" required><button type="submit" class="btn" style="width: 100%;">Войти</button></form></div>'
    return render_template_string(BASE_TEMPLATE.replace('{CONTENT_PLACEHOLDER}', content), user=None)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=1324)