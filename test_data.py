import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'Web_DB.db'

def create_test_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    print("🚀 Создание тестовых данных...")
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    # 1 админ + 1 модератор + 18 юзеров = 20 человек
    users_data = [
        # Админ (1)
        ('admin', 'admin@auranexus.com', 'admin', 'admin', 'Администратор платформы 👑'),
        
        # Модератор (1)
        ('moderator', 'moderator@auranexus.com', 'mod123', 'moderator', 'Слежу за порядком в сообществе 🛡️'),
        
        # Обычные пользователи (18)
        ('john_doe', 'john@mail.ru', 'pass123', 'user', 'Люблю программирование и кофе ☕'),
        ('alice_wonder', 'alice@mail.ru', 'pass123', 'user', 'Фотограф и путешественница 📸'),
        ('bob_builder', 'bob@mail.ru', 'pass123', 'user', 'Строю миры из кода 🏗️'),
        ('emma_star', 'emma@mail.ru', 'pass123', 'user', 'Музыкант и художник 🎨'),
        ('max_power', 'max@mail.ru', 'pass123', 'user', 'Геймер и стример 🎮'),
        ('lisa_cook', 'lisa@mail.ru', 'pass123', 'user', 'Готовлю вкусняшки 🍕'),
        ('sarah_art', 'sarah@mail.ru', 'pass123', 'user', 'Digital artist ✨'),
        ('mike_sport', 'mike@mail.ru', 'pass123', 'user', 'Фитнес и ЗОЖ 💪'),
        ('anna_music', 'anna@mail.ru', 'pass123', 'user', 'Музыка - моя жизнь 🎵'),
        ('peter_code', 'peter@mail.ru', 'pass123', 'user', 'Full-stack разработчик 💻'),
        ('nina_photo', 'nina@mail.ru', 'pass123', 'user', 'Фотографирую природу 🌿'),
        ('ivan_game', 'ivan@mail.ru', 'pass123', 'user', 'Киберспортсмен 🏆'),
        ('olga_design', 'olga@mail.ru', 'pass123', 'user', 'UI/UX дизайнер 🎯'),
        ('denis_travel', 'denis@mail.ru', 'pass123', 'user', 'Объездил 30 стран 🌍'),
        ('maria_book', 'maria@mail.ru', 'pass123', 'user', 'Книжный червь 📚'),
        ('sergey_tech', 'sergey@mail.ru', 'pass123', 'user', 'Обзоры гаджетов 📱'),
        ('elena_yoga', 'elena@mail.ru', 'pass123', 'user', 'Йога и медитация 🧘'),
        ('andrey_car', 'andrey@mail.ru', 'pass123', 'user', 'Автолюбитель 🚗'),
    ]
    
    user_ids = []
    for username, email, password, role, bio in users_data:
        try:
            # ⚠️ ПАРОЛЬ БЕЗ ШИФРОВАНИЯ - просто текст!
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, role, bio) VALUES (?, ?, ?, ?, ?)',
                (username, email, password, role, bio)
            )
            user_ids.append(cursor.lastrowid)
            role_emoji = {'admin': '👑', 'moderator': '🛡️', 'user': '👤'}
            print(f"  ✓ {role_emoji.get(role, '👤')} {username} ({role}) - пароль: {password}")
        except sqlite3.IntegrityError:
            existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                user_ids.append(existing['id'])
            print(f"  → {username} уже существует")
    
    # ==================== КАНАЛЫ (8 штук) ====================
    channels_data = [
        ('Технологии', 'Новости IT, гаджеты, программирование 🖥️', user_ids[2]),
        ('Игры', 'Обзоры игр, стримы, киберспорт 🎮', user_ids[6]),
        ('Творчество', 'Искусство, дизайн, музыка 🎨', user_ids[8]),
        ('Кулинария', 'Рецепты и кулинарные советы 🍕', user_ids[7]),
        ('Путешествия', 'Истории из поездок ✈️', user_ids[15]),
        ('Спорт', 'Фитнес, тренировки, ЗОЖ 💪', user_ids[9]),
        ('Книги', 'Обсуждаем литературу 📚', user_ids[16]),
        ('Авто', 'Всё об автомобилях 🚗', user_ids[19]),
    ]
    
    channel_ids = []
    for name, description, creator_id in channels_data:
        try:
            cursor = conn.execute(
                'INSERT INTO channels (name, description, creator_id) VALUES (?, ?, ?)',
                (name, description, creator_id)
            )
            channel_ids.append(cursor.lastrowid)
            print(f"  ✓ Канал: {name}")
        except sqlite3.IntegrityError:
            existing = conn.execute('SELECT id FROM channels WHERE name = ?', (name,)).fetchone()
            if existing:
                channel_ids.append(existing['id'])
            print(f"  → Канал {name} уже существует")
    
    # ==================== ПОСТЫ ====================
    posts_data = [
        # Технологии
        (user_ids[2], channel_ids[0], 'text', 
         'Python vs JavaScript в 2024', 
         'Сравниваем два популярных языка. Какой выбрать новичку? По моему опыту, Python лучше для начала - синтаксис проще и понятнее. #python #javascript #programming'),
        
        (user_ids[11], channel_ids[0], 'text',
         'Топ-5 расширений для VS Code',
         'Делюсь своим списком must-have расширений: Prettier, ESLint, GitLens, Live Server, Auto Rename Tag. А какие используете вы? #vscode #coding'),
        
        (user_ids[17], channel_ids[0], 'text',
         'Обзор нового MacBook Air M3',
         'Пользуюсь уже месяц. Батарея держит весь день, производительность отличная. Единственный минус - цена 😅 #apple #macbook'),
        
        # Игры
        (user_ids[6], channel_ids[1], 'text',
         'GTA 6 - первые впечатления',
         'Прошёл уже 20 часов. Графика нереальная, сюжет затягивает! Rockstar снова сделали шедевр 🎮 #gta6 #gaming'),
        
        (user_ids[13], channel_ids[1], 'text',
         'Сборка игрового ПК за 80к',
         'Собрал бюджетный игровой комп. RTX 4060, Ryzen 5 7600, 16GB RAM. Тянет всё на высоких! #pcbuild #gaming'),
        
        (user_ids[6], channel_ids[1], 'text',
         'Лучшие инди-игры 2024',
         'Моя подборка недооценённых инди: Hades 2, Balatro, Animal Well. Все - маст хэв! #indie #gaming'),
        
        # Творчество
        (user_ids[8], channel_ids[2], 'text',
         'Как я рисовал закат',
         'Работал над этим артом неделю. Использовал Procreate на iPad. Что думаете? #art #digital'),
        
        (user_ids[5], channel_ids[2], 'text',
         'Туториал: основы композиции',
         'Разбираем правило третей, золотое сечение и другие приёмы. Полезно для фото и дизайна! #tutorial #design'),
        
        (user_ids[14], channel_ids[2], 'text',
         'Тренды в UI/UX 2024',
         'Минимализм, тёмные темы, микроанимации. Что ещё актуально в этом году? #uidesign #trends'),
        
        # Кулинария
        (user_ids[7], channel_ids[3], 'text',
         'Рецепт пасты карбонара',
         'Настоящая итальянская карбонара БЕЗ сливок! Секрет в правильном соусе из желтков и пекорино 🍝 #food #recipe'),
        
        (user_ids[7], channel_ids[3], 'text',
         'Завтрак за 10 минут',
         '3 быстрых рецепта для тех, кто спешит: овсянка с ягодами, тосты с авокадо, омлет с овощами ☕ #breakfast'),
        
        # Путешествия
        (user_ids[3], channel_ids[4], 'text',
         'Неделя в Италии',
         'Вернулась из Рима и Флоренции! Делюсь впечатлениями и лайфхаками. Обязательно попробуйте джелато! 🇮🇹 #travel #italy'),
        
        (user_ids[15], channel_ids[4], 'text',
         'Бюджетно по Азии',
         'Как я месяц путешествовал по Таиланду за 50к рублей. Спойлер: уличная еда - это спасение! #budget #travel'),
        
        # Спорт
        (user_ids[9], channel_ids[5], 'text',
         'Программа тренировок для новичков',
         'Составил базовую программу на 3 дня в неделю. Все упражнения с собственным весом 💪 #fitness #workout'),
        
        (user_ids[18], channel_ids[5], 'text',
         'Йога для начинающих',
         '5 простых асан, которые можно делать дома. Улучшают гибкость и снимают стресс 🧘 #yoga'),
        
        # Книги
        (user_ids[16], channel_ids[6], 'text',
         'Топ-5 книг по саморазвитию',
         'Мой список: Атомные привычки, Думай медленно решай быстро, 7 навыков, Поток, Антихрупкость 📚 #books'),
        
        (user_ids[16], channel_ids[6], 'text',
         'Обзор "Мастер и Маргарита"',
         'Перечитала спустя 10 лет. Совершенно другое восприятие! Какая ваша любимая цитата? #bulgakov'),
        
        # Авто
        (user_ids[19], channel_ids[7], 'text',
         'Тест-драйв Tesla Model 3',
         'Взял на тест электромобиль. Автопилот впечатляет, но инфраструктура пока слабая ⚡ #tesla #electric'),
        
        (user_ids[19], channel_ids[7], 'text',
         'Как выбрать первую машину',
         'Советы новичкам: на что смотреть, какие марки надёжные, где лучше покупать 🚗 #firstcar'),
        
        # Посты без канала (общая лента)
        (user_ids[0], None, 'text',
         'Добро пожаловать!',
         'Приветствуем всех на нашей платформе! Читайте правила и общайтесь уважительно 👋'),
        
        (user_ids[1], None, 'text',
         'Правила сообщества',
         'Напоминаю основные правила: без спама, оскорблений и нелегального контента. Вопросы - в ЛС ⚖️'),
        
        (user_ids[4], None, 'text',
         'Ищу команду для проекта',
         'Запускаем стартап, нужен фронтендер и дизайнер. Пишите в ЛС! #job #startup'),
        
        (user_ids[12], None, 'text',
         'Осенний фотосет',
         'Поймала золотую осень в парке. Обожаю это время года! 🍂 #photo #autumn'),
        
        (user_ids[10], None, 'text',
         'Новый трек!',
         'Записал кавер на любимую песню. Скоро выложу, ждите! 🎵 #music'),
    ]
    
    post_ids = []
    for user_id, channel_id, post_type, title, content in posts_data:
        try:
            cursor = conn.execute(
                'INSERT INTO posts (user_id, channel_id, post_type, title, content) VALUES (?, ?, ?, ?, ?)',
                (user_id, channel_id, post_type, title, content)
            )
            post_ids.append(cursor.lastrowid)
            print(f"  ✓ Пост: {title[:40]}...")
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
    
    # ==================== КОММЕНТАРИИ ====================
    comments_templates = [
        'Отличный пост! 👍',
        'Спасибо за информацию!',
        'Очень полезно, сохранил',
        'Согласен на 100%',
        'А можно подробнее про это?',
        'Круто! 🔥',
        'Подписался!',
        'Топ контент как всегда',
        'Наконец-то качественный материал',
        'Жду продолжения!',
        'Это то, что я искал!',
        'В закладки 📌',
        'Автор молодец!',
        'Интересная точка зрения',
        'Хотелось бы больше примеров',
        'Класс! 💯',
        'Поделился с друзьями',
        'У меня вопрос...',
        'Гениально!',
        'Благодарю за пост',
        'Жду вторую часть!',
        'Лайк! 👊',
        'Давно искал такое',
        'Прикольно 😎',
        'Полностью поддерживаю!',
        'Не думал об этом раньше',
        'Очень актуально',
        'Мне помогло, спасибо',
    ]
    
    comment_count = 0
    for post_id in post_ids:
        num_comments = random.randint(3, 10)
        for _ in range(num_comments):
            user_id = random.choice(user_ids)
            content = random.choice(comments_templates)
            try:
                conn.execute(
                    'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                    (post_id, user_id, content)
                )
                comment_count += 1
            except:
                pass
    print(f"  ✓ Комментариев: {comment_count}")
    
    # ==================== РЕАКЦИИ ====================
    reaction_types = ['like', 'love', 'laugh', 'wow', 'sad', 'dislike']
    reaction_weights = [50, 25, 12, 8, 3, 2]  # like самый частый
    
    reaction_count = 0
    for post_id in post_ids:
        num_reactions = random.randint(8, 18)
        reacted_users = random.sample(user_ids, min(num_reactions, len(user_ids)))
        for user_id in reacted_users:
            reaction = random.choices(reaction_types, weights=reaction_weights)[0]
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO reactions (user_id, post_id, reaction_type) VALUES (?, ?, ?)',
                    (user_id, post_id, reaction)
                )
                reaction_count += 1
            except:
                pass
    print(f"  ✓ Реакций: {reaction_count}")
    
    # ==================== ПОДПИСКИ НА КАНАЛЫ ====================
    sub_count = 0
    for channel_id in channel_ids:
        num_subs = random.randint(10, 18)
        subscribers = random.sample(user_ids, min(num_subs, len(user_ids)))
        for user_id in subscribers:
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO channel_subscribers (user_id, channel_id) VALUES (?, ?)',
                    (user_id, channel_id)
                )
                sub_count += 1
            except:
                pass
    print(f"  ✓ Подписок: {sub_count}")
    
    # ==================== ГЛОБАЛЬНЫЙ ЧАТ ====================
    chat_messages = [
        (user_ids[0], 'Добро пожаловать всем новичкам! 👋'),
        (user_ids[2], 'Привет! Кто тут есть?'),
        (user_ids[3], 'Здравствуйте!'),
        (user_ids[4], 'Отличный день для кода ☕'),
        (user_ids[5], 'Рисую новый арт 🎨'),
        (user_ids[6], 'Кто играет сегодня вечером?'),
        (user_ids[7], 'Готовлю пасту, кто голоден? 🍝'),
        (user_ids[8], 'Новый пост скоро!'),
        (user_ids[9], 'Только с тренировки 💪'),
        (user_ids[10], 'Слушаю новый альбом'),
        (user_ids[6], 'Я! Во что играем?'),
        (user_ids[13], 'CS2 или Valorant?'),
        (user_ids[6], 'Давай CS2'),
        (user_ids[11], 'Кто шарит в Python?'),
        (user_ids[2], 'Я, что нужно?'),
        (user_ids[11], 'Помоги с asyncio плиз'),
        (user_ids[2], 'Пиши в ЛС'),
        (user_ids[14], 'Новый дизайн готов!'),
        (user_ids[3], 'Покажи!'),
        (user_ids[15], 'Планирую поездку в Грузию 🇬🇪'),
        (user_ids[16], 'Там супер! Был в прошлом году'),
        (user_ids[15], 'Что посоветуешь?'),
        (user_ids[16], 'Тбилиси и Батуми must visit'),
        (user_ids[17], 'Обзор нового iPhone готов'),
        (user_ids[18], 'Утренняя йога 🧘'),
        (user_ids[19], 'Помыл машину наконец 🚗'),
        (user_ids[1], 'Напоминаю о правилах чата ⚖️'),
        (user_ids[4], 'Стрим сегодня в 20:00!'),
        (user_ids[6], 'Буду смотреть! 👀'),
        (user_ids[13], '+1'),
        (user_ids[8], 'Я тоже приду'),
        (user_ids[3], 'Хорошего всем вечера! 🌙'),
        (user_ids[5], 'И вам!'),
        (user_ids[7], 'Спокойной ночи 😴'),
    ]
    
    for user_id, content in chat_messages:
        try:
            conn.execute(
                'INSERT INTO global_chat (user_id, content) VALUES (?, ?)',
                (user_id, content)
            )
        except:
            pass
    print(f"  ✓ Сообщений в чате: {len(chat_messages)}")
    
    # ==================== ЛИЧНЫЕ СООБЩЕНИЯ ====================
    conversations = [
        (user_ids[2], user_ids[3], [
            ('Привет! Видел твой пост про Италию?', 0),
            ('Да! Только вернулась)', 1),
            ('Как там? Стоит ехать?', 0),
            ('Однозначно! Рим - must visit', 1),
            ('Спасибо, буду планировать!', 0),
        ]),
        (user_ids[6], user_ids[13], [
            ('Го в CS2?', 0),
            ('Давай, через час', 1),
            ('Ок, пиши когда будешь', 0),
            ('Онлайн, заходи', 1),
        ]),
        (user_ids[11], user_ids[2], [
            ('Привет! Можешь помочь с кодом?', 0),
            ('Привет, конечно. Что случилось?', 1),
            ('Не работает async функция', 0),
            ('Скинь код, посмотрю', 1),
            ('Отправил в телегу', 0),
        ]),
        (user_ids[0], user_ids[1], [
            ('Как обстановка?', 0),
            ('Всё спокойно, пару спамеров забанил', 1),
            ('Отлично, продолжай в том же духе', 0),
            ('Принял!', 1),
        ]),
    ]
    
    conv_count = 0
    msg_count = 0
    for user1, user2, messages in conversations:
        user1_id, user2_id = min(user1, user2), max(user1, user2)
        try:
            cursor = conn.execute(
                'INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)',
                (user1_id, user2_id)
            )
            conv_id = cursor.lastrowid
            conv_count += 1
            
            for content, sender_idx in messages:
                sender = user1 if sender_idx == 0 else user2
                conn.execute(
                    'INSERT INTO messages (conversation_id, sender_id, content) VALUES (?, ?, ?)',
                    (conv_id, sender, content)
                )
                msg_count += 1
        except:
            pass
    
    print(f"  ✓ Переписок: {conv_count}, сообщений: {msg_count}")
    
    # ==================== УВЕДОМЛЕНИЯ ====================
    notifications_data = [
        (user_ids[2], 'reaction', 'alice_wonder оценил ваш пост', '/#post-1'),
        (user_ids[2], 'comment', 'bob_builder прокомментировал ваш пост', '/#post-1'),
        (user_ids[3], 'subscribe', 'john_doe подписался на канал "Путешествия"', '/channel/5'),
        (user_ids[6], 'reaction', 'ivan_game оценил ваш пост', '/#post-4'),
        (user_ids[7], 'comment', 'emma_star прокомментировал ваш пост', '/#post-10'),
    ]
    
    for user_id, n_type, content, link in notifications_data:
        try:
            conn.execute(
                'INSERT INTO notifications (user_id, type, content, link) VALUES (?, ?, ?, ?)',
                (user_id, n_type, content, link)
            )
        except:
            pass
    print(f"  ✓ Уведомлений: {len(notifications_data)}")
    
    conn.commit()
    conn.close()
    
    # ==================== ИТОГИ ====================
    print("\n" + "="*55)
    print("  ✅ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print("="*55)
    
    print("\n📊 СТАТИСТИКА:")
    print(f"   • Пользователей: {len(users_data)}")
    print(f"   • Каналов: {len(channels_data)}")
    print(f"   • Постов: {len(posts_data)}")
    print(f"   • Комментариев: ~{comment_count}")
    print(f"   • Реакций: ~{reaction_count}")
    print(f"   • Подписок: ~{sub_count}")
    print(f"   • Сообщений в чате: {len(chat_messages)}")
    
    print("\n" + "="*55)
    print("  📋 АККАУНТЫ ДЛЯ ВХОДА")
    print("="*55)
    print("\n  👑 АДМИНИСТРАТОР:")
    print("     Логин: admin")
    print("     Пароль: admin")
    print("\n  🛡️ МОДЕРАТОР:")
    print("     Логин: moderator")
    print("     Пароль: mod123")
    print("\n  👤 ПОЛЬЗОВАТЕЛИ (пароль у всех: pass123):")
    print("     john_doe, alice_wonder, bob_builder,")
    print("     emma_star, max_power, lisa_cook,")
    print("     sarah_art, mike_sport, anna_music,")
    print("     peter_code, nina_photo, ivan_game,")
    print("     olga_design, denis_travel, maria_book,")
    print("     sergey_tech, elena_yoga, andrey_car")
    print("="*55)


if __name__ == '__main__':
    create_test_data()