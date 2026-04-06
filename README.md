# MyApp - Социальная платформа

## Описание

MyApp - это веб-приложение на Flask, представляющее собой социальную платформу с возможностью публикации постов, создания каналов, общения в чате и комментирования.

## Функциональность

- Регистрация и авторизация пользователей
- Публикация постов (новости, видео, shorts)
- Создание каналов/сообществ
- Общий чат в реальном времени
- Система комментариев с вложенностью
- Поиск по постам
- Репост записей в чат

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-repo/myapp.git
cd myapp
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
```

3. Активируйте окружение:

```bash
# Windows
.venv\Scripts\activate

# Linux/MacOS
source .venv/bin/activate
```

4. Установите зависимости:

```bash 
pip install -r requirements.txt
```

5. Запустите приложение:

```bash
python app.py
```

6. Откройте в браузере: http://localhost:1234 (Или любой другой свободный порт)

## Cтруктура проекта

```txt
myapp/
├── app.py
├── requirements.txt
├── README.md
├── Web_DB.db
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    └── user_agreement.html
```

## Учетные данные администратора
Логин: admin
Пароль: admin123

## Технологии которые были использованы в проекте

- Python 3.10+
- Flask 3.1.3
- SQLite3
- HTML5/CSS3
- JavaScript (vanilla)

## Лицензия
MIT License 