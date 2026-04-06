# Aura Nexus

Социальная платформа нового поколения для обмена контентом, идеями и общения.

## Возможности

### Типы контента
- 📝 Текстовые посты с хештегами
- 📹 Видео (до 100 МБ)
- 🖼️ Фото (до 10 на публикацию)
- 🎵 Аудио (до 30 МБ)
- 📄 Статьи с WYSIWYG редактором (Quill)
- ⏱️ Истории (24 часа, затем в архив)

### Социальные функции
- 📺 Каналы с подписками
- 💬 Комментарии с вложенностью
- 👍👎❤️😂😮😢 Система реакций
- 🌐 Глобальный чат с защитой от спама
- ✉️ Личные сообщения
- 🔔 Уведомления

### Модерация
- 👤 Роли: user, moderator, admin
- 📋 Система жалоб
- 🚫 Временные и перманентные баны
- 📝 Логи действий администраторов

## Установка

### 1. Клонирование репозитория

git clone https://github.com/your-repo/aura-nexus.git
cd aura-nexus

### 2. Создание виртуального окружения

python -m venv .venv

Windows:
.venv\Scripts\activate

Linux/MacOS:
source .venv/bin/activate

### 3. Установка зависимостей

pip install -r requirements.txt

### 4. Запуск

python app.py

Приложение будет доступно по адресу: http://localhost:1324

## Структура проекта

aura_nexus/
├── app.py                    # Основное приложение
├── config.py                 # Конфигурация
├── requirements.txt          # Зависимости
├── README.md                 # Документация
├── LICENSE                   # Лицензия
├── Web_DB.db                 # База данных (создаётся автоматически)
│
├── uploads/                  # Загружаемые файлы
│   ├── videos/
│   ├── photos/
│   ├── audio/
│   ├── stories/
│   ├── avatars/
│   └── banners/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       ├── reactions.js
│       ├── chat.js
│       ├── comments.js
│       └── notifications.js
│
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── notifications.html
    ├── user_agreement.html
    │
    ├── profile/
    │   ├── view.html
    │   └── settings.html
    │
    ├── channel/
    │   ├── list.html
    │   ├── view.html
    │   └── create.html
    │
    ├── create/
    │   ├── post.html
    │   ├── video.html
    │   ├── photo.html
    │   ├── audio.html
    │   ├── article.html
    │   └── story.html
    │
    ├── messages/
    │   ├── inbox.html
    │   └── chat.html
    │
    ├── admin/
    │   ├── dashboard.html
    │   ├── users.html
    │   ├── reports.html
    │   ├── bans.html
    │   └── logs.html
    │
    ├── components/
    │   └── post_card.html
    │
    └── errors/
        ├── 404.html
        └── 500.html

## Учётные данные по умолчанию

Администратор:
- Логин: admin
- Пароль: admin123

## Технологии

- Backend: Python 3.10+, Flask 3.1.3
- Database: SQLite3
- Frontend: HTML5, CSS3, JavaScript (vanilla)
- Editor: Quill.js (для статей)

## API Endpoints

### Авторизация
- GET/POST /login - Вход
- GET/POST /register - Регистрация
- GET /logout - Выход

### Контент
- GET/POST /create/post - Текстовый пост
- GET/POST /create/video - Видео
- GET/POST /create/photo - Фото
- GET/POST /create/audio - Аудио
- GET/POST /create/article - Статья
- GET/POST /create/story - История

### Каналы
- GET /channels - Список каналов
- GET /channel/<id> - Страница канала
- GET/POST /channel/create - Создание канала
- POST /channel/<id>/subscribe - Подписка/отписка

### Реакции и комментарии
- POST /api/react/<post_id> - Поставить реакцию
- POST /api/comment/<post_id> - Добавить комментарий
- GET /api/comments/<post_id> - Получить комментарии

### Сообщения
- GET /messages - Список диалогов
- GET/POST /messages/<user_id> - Диалог с пользователем
- POST /api/global_chat - Отправить в глобальный чат

### Профиль
- GET /profile/<username> - Страница профиля
- GET/POST /profile/settings - Настройки

### Админ-панель
- GET /admin - Дашборд
- GET /admin/users - Пользователи
- POST /admin/users/<id>/role - Изменить роль
- POST /admin/users/<id>/ban - Забанить
- POST /admin/users/<id>/unban - Разбанить
- POST /admin/users/<id>/delete - Удалить
- GET /admin/reports - Жалобы
- POST /admin/reports/<id>/handle - Обработать жалобу
- GET /admin/bans - История банов
- GET /admin/logs - Логи действий

## Ограничения файлов

| Тип | Макс. размер | Форматы |
|-----|--------------|---------|
| Видео | 100 МБ | mp4, webm, mov |
| Фото | 20 МБ | jpg, png, gif, webp |
| Аудио | 30 МБ | mp3, wav, ogg |
| Аватар | 5 МБ | jpg, png, gif, webp |
| Баннер | 10 МБ | jpg, png, gif, webp |

## Антиспам в чате

Более 3 сообщений за 5 секунд = блокировка чата на 20 секунд

## Система ролей

| Роль | Возможности |
|------|-------------|
| user | Публикации, комментарии, реакции, ЛС, жалобы |
| moderator | + Удаление контента, обработка жалоб, временные баны |
| admin | + Управление ролями, перманентные баны, удаление пользователей/каналов |

## Автор

Aura Nexus Team © 2026