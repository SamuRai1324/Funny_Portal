from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'secret-key-12345'

DATABASE = 'users.db'

USERNAME_MIN = 3
USERNAME_MAX = 20
PASSWORD_MIN = 6
PASSWORD_MAX = 50

ROLES = {'user': 1, 'moderator': 2, 'admin': 3}


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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT
            )
        ''')
        
        admin = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
        if not admin:
            conn.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                ('admin', 'admin@site.com', 'admin123', 'admin')
            )
        conn.commit()


def get_current_user():
    if 'user_id' not in session:
        return None
    with get_db() as conn:
        return conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Войдите в систему', 'warning')
            return redirect(url_for('login'))
        user = get_current_user()
        if user and user['is_banned']:
            session.clear()
            flash('Аккаунт заблокирован: ' + (user['ban_reason'] or 'Не указана'), 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_required(min_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or ROLES.get(user['role'], 0) < ROLES.get(min_role, 0):
                flash('Недостаточно прав', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


@app.context_processor
def inject_globals():
    return {
        'current_user': get_current_user(),
        'ROLES': ROLES,
        'USERNAME_MIN': USERNAME_MIN,
        'USERNAME_MAX': USERNAME_MAX,
        'PASSWORD_MIN': PASSWORD_MIN,
        'PASSWORD_MAX': PASSWORD_MAX
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        
        if len(username) < USERNAME_MIN or len(username) > USERNAME_MAX:
            flash(f'Логин: {USERNAME_MIN}-{USERNAME_MAX} символов', 'danger')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Логин: только буквы, цифры и _', 'danger')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Некорректный email', 'danger')
        elif len(password) < PASSWORD_MIN or len(password) > PASSWORD_MAX:
            flash(f'Пароль: {PASSWORD_MIN}-{PASSWORD_MAX} символов', 'danger')
        elif password != confirm:
            flash('Пароли не совпадают', 'danger')
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, password)
                    )
                    conn.commit()
                flash('Регистрация успешна', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Пользователь уже существует', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?',
                (login_input, login_input.lower(), password)
            ).fetchone()
            
            if user:
                if user['is_banned']:
                    flash('Аккаунт заблокирован', 'danger')
                    return render_template('login.html')
                
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Добро пожаловать!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    print("http://localhost:2323")
    print("admin / admin123")
    app.run(debug=True, port=2323)