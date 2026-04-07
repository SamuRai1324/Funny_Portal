import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'Web_DB.db'

def create_test_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    print("🚀 Создание тестовых данных...")
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    users_data = [
        ('admin', 'admin@mail.ru', 'admin', 'admin', 'just admin'),
        
        # Модераторы (2 штуки)
        ('moderator_alex', 'alex.mod@test.com', 'mod123', 'moderator', 'Главный модератор сообщества 🛡️'),
        ('moderator_kate', 'kate.mod@test.com', 'mod123', 'moderator', 'Слежу за порядком ⚖️'),
        
        # Обычные пользователи (15 штук)
        ('john_doe', 'john@test.com', 'pass123', 'user', 'Люблю программирование и кофе ☕'),
        ('alice_wonder', 'alice@test.com', 'pass123', 'user', 'Фотограф и путешественница 📸'),
        ('bob_builder', 'bob@test.com', 'pass123', 'user', 'Строю миры из кода 🏗️'),
        ('emma_star', 'emma@test.com', 'pass123', 'user', 'Музыкант и художник 🎨'),
        ('max_power', 'max@test.com', 'pass123', 'user', 'Геймер и стример 🎮'),
        ('lisa_cook', 'lisa@test.com', 'pass123', 'user', 'Готовлю вкусняшки 🍕'),
        ('sarah_art', 'sarah@test.com', 'pass123', 'user', 'Digital artist ✨'),
        ('mike_sport', 'mike@test.com', 'pass123', 'user', 'Фитнес и здоровый образ жизни 💪'),
        ('anna_music', 'anna@test.com', 'pass123', 'user', 'Музыка - моя жизнь 🎵'),
        ('peter_code', 'peter@test.com', 'pass123', 'user', 'Full-stack разработчик 💻'),
        ('nina_photo', 'nina@test.com', 'pass123', 'user', 'Фотографирую природу 🌿'),
        ('ivan_game', 'ivan@test.com', 'pass123', 'user', 'Киберспортсмен 🏆'),
        ('olga_design', 'olga@test.com', 'pass123', 'user', 'UI/UX дизайнер 🎯'),
        ('denis_travel', 'denis@test.com', 'pass123', 'user', 'Объездил 30 стран 🌍'),
        ('maria_book', 'maria@test.com', 'pass123', 'user', 'Книжный червь 📚'),
        ('sergey_tech', 'sergey@test.com', 'pass123', 'user', 'Обзоры гаджетов 📱'),
        ('elena_yoga', 'elena@test.com', 'pass123', 'user', 'Йога и медитация 🧘'),
        ('andrey_car', 'andrey@test.com', 'pass123', 'user', 'Автолюбитель 🚗'),
        ('victoria_food', 'victoria@test.com', 'pass123', 'user', 'Ресторанный критик 🍽️'),
    ]
    
    user_ids = []
    for username, email, password, role, bio in users_data:
        try:
            # ПАРОЛЬ БЕЗ ШИФРОВАНИЯ - просто текст
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, role, bio) VALUES (?, ?, ?, ?, ?)',
                (username, email, password, role, bio)
            )
            user_ids.append(cursor.lastrowid)
            print(f"  ✓ Пользователь: {username} ({role})")
        except sqlite3.IntegrityError:
            existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                user_ids.append(existing['id'])
            print(f"  → Пользователь {username} уже существует")
    
    # ==================== КАНАЛЫ ====================
    channels_data = [
        ('TechNews', 'Новости технологий и IT индустрии 🖥️', user_ids[2] if len(user_ids) > 2 else 1),
        ('GameZone', 'Игры, обзоры и стримы 🎮', user_ids[6] if len(user_ids) > 6 else 1),
        ('ArtCorner', 'Искусство и творчество 🎨', user_ids[8] if len(user_ids) > 8 else 1),
        ('MusicWorld', 'Музыка всех жанров 🎵', user_ids[10] if len(user_ids) > 10 else 1),
        ('FoodLovers', 'Рецепты и кулинария 🍕', user_ids[7] if len(user_ids) > 7 else 1),
        ('TravelClub', 'Путешествия и приключения ✈️', user_ids[15] if len(user_ids) > 15 else 1),
        ('FitnessLife', 'Спорт и здоровье 💪', user_ids[9] if len(user_ids) > 9 else 1),
        ('BookClub', 'Обсуждаем книги 📚', user_ids[16] if len(user_ids) > 16 else 1),
        ('AutoWorld', 'Всё об автомобилях 🚗', user_ids[19] if len(user_ids) > 19 else 1),
        ('DesignHub', 'Дизайн и креатив 🎨', user_ids[13] if len(user_ids) > 13 else 1),
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
    
    # ==================== ПОСТЫ (много!) ====================
    posts_data = [
        # TechNews
        (user_ids[2], channel_ids[0] if channel_ids else None, 'text', 
         'Новый iPhone 16 представлен!', 
         'Apple представила новую линейку смартфонов с революционными функциями ИИ. Камера теперь 200 МП! #apple #iphone #tech'),
        
        (user_ids[11], channel_ids[0] if channel_ids else None, 'text',
         'Python 4.0 - что нового?',
         'Разбираем все нововведения в новой версии Python. Спойлер: GIL наконец убрали! #python #programming'),
        
        (user_ids[17], channel_ids[0] if channel_ids else None, 'text',
         'Обзор нового MacBook Pro M4',
         'Тестирую новый макбук уже неделю. Батарея держит 25 часов! #apple #macbook #review'),
        
        (user_ids[4], channel_ids[0] if channel_ids else None, 'text',
         'Лучшие расширения для VS Code 2024',
         'Топ-10 расширений, которые ускорят вашу разработку в 2 раза! #vscode #productivity #coding'),
        
        # GameZone
        (user_ids[6], channel_ids[1] if len(channel_ids) > 1 else None, 'text',
         'Обзор GTA 6 - шедевр!',
         'Наконец-то дождались! Первые впечатления: графика нереальная, сюжет затягивает 🎮 #gta6 #gaming'),
        
        (user_ids[12], channel_ids[1] if len(channel_ids) > 1 else None, 'text',
         'Киберспорт: итоги турнира',
         'Наша команда заняла 2 место на региональном турнире по CS2! 🏆 #esports #cs2'),
        
        (user_ids[6], channel_ids[1] if len(channel_ids) > 1 else None, 'text',
         'Топ-5 инди игр месяца',
         'Подборка инди-игр, которые вы могли пропустить. Номер 3 - просто бомба! #indie #gaming'),
        
        (user_ids[12], channel_ids[1] if len(channel_ids) > 1 else None, 'text',
         'Настройка игрового ПК',
         'Гайд по сборке игрового компьютера за 100к рублей #pcbuild #gaming #guide'),
        
        # ArtCorner
        (user_ids[8], channel_ids[2] if len(channel_ids) > 2 else None, 'text',
         'Мой новый арт - закат',
         'Работал над этим рисунком целую неделю! Что думаете? #art #digital #sunset'),
        
        (user_ids[5], channel_ids[2] if len(channel_ids) > 2 else None, 'text',
         'Туториал: как рисовать глаза',
         'Подробный гайд по рисованию реалистичных глаз #tutorial #art #eyes'),
        
        (user_ids[13], channel_ids[2] if len(channel_ids) > 2 else None, 'text',
         'Тренды в UI дизайне 2024',
         'Неоморфизм уходит, возвращается скевоморфизм! #uidesign #trends'),
        
        # MusicWorld
        (user_ids[10], channel_ids[3] if len(channel_ids) > 3 else None, 'text',
         'Топ-10 альбомов года',
         'Мой личный рейтинг лучших музыкальных релизов 2024 🎵 #music #top10'),
        
        (user_ids[5], channel_ids[3] if len(channel_ids) > 3 else None, 'text',
         'Как научиться играть на гитаре',
         'Пошаговый план для новичков. За 3 месяца - первая песня! #guitar #music #tutorial'),
        
        # FoodLovers
        (user_ids[7], channel_ids[4] if len(channel_ids) > 4 else None, 'text',
         'Рецепт идеальной пасты карбонара',
         'Делюсь секретом настоящей итальянской карбонары! Без сливок! 🍝 #food #recipe #pasta'),
        
        (user_ids[20], channel_ids[4] if len(channel_ids) > 4 else None, 'text',
         'Обзор ресторана "Высота"',
         'Побывала в новом ресторане на 50 этаже. Виды шикарные, еда... средняя 🍽️ #review #restaurant'),
        
        (user_ids[7], channel_ids[4] if len(channel_ids) > 4 else None, 'text',
         'Завтрак за 5 минут',
         '3 рецепта быстрого и полезного завтрака для тех, кто спешит ☕ #breakfast #quickrecipe'),
        
        # TravelClub
        (user_ids[3], channel_ids[5] if len(channel_ids) > 5 else None, 'text',
         'Путешествие по Италии',
         'Только вернулась из невероятного путешествия! Рим, Флоренция, Венеция 🇮🇹 #travel #italy'),
        
        (user_ids[15], channel_ids[5] if len(channel_ids) > 5 else None, 'text',
         'Бюджетно по Азии',
         'Как я путешествовал месяц по Таиланду за 50к рублей #budget #travel #thailand'),
        
        (user_ids[15], channel_ids[5] if len(channel_ids) > 5 else None, 'text',
         'Что взять в путешествие',
         'Чек-лист вещей для путешествия налегке. Всё влезет в ручную кладь! #packing #travel'),
        
        # FitnessLife
        (user_ids[9], channel_ids[6] if len(channel_ids) > 6 else None, 'text',
         'Утренняя тренировка 30 минут',
         'Моя программа утренней тренировки для бодрости на весь день 💪 #fitness #workout'),
        
        (user_ids[18], channel_ids[6] if len(channel_ids) > 6 else None, 'text',
         'Йога для начинающих',
         'Простые асаны, которые можно делать дома без подготовки 🧘 #yoga #beginner'),
        
        (user_ids[9], channel_ids[6] if len(channel_ids) > 6 else None, 'text',
         'Правильное питание спортсмена',
         'Разбираем КБЖУ и составляем рацион для набора массы #nutrition #fitness'),
        
        # BookClub
        (user_ids[16], channel_ids[7] if len(channel_ids) > 7 else None, 'text',
         'Топ-5 книг по саморазвитию',
         'Книги, которые изменили мое мышление 📚 #books #selfimprovement'),
        
        (user_ids[16], channel_ids[7] if len(channel_ids) > 7 else None, 'text',
         'Обзор: "Мастер и Маргарита"',
         'Перечитала классику и нашла новые смыслы #bulgakov #classic #review'),
        
        # AutoWorld  
        (user_ids[19], channel_ids[8] if len(channel_ids) > 8 else None, 'text',
         'Тест-драйв Tesla Model S',
         'Впечатления от электромобиля после недели использования ⚡ #tesla #electric #car'),
        
        (user_ids[19], channel_ids[8] if len(channel_ids) > 8 else None, 'text',
         'Как выбрать первый автомобиль',
         'Советы для тех, кто покупает машину впервые 🚗 #firstcar #guide'),
        
        # DesignHub
        (user_ids[13], channel_ids[9] if len(channel_ids) > 9 else None, 'text',
         'Figma vs Sketch в 2024',
         'Сравнение двух главных инструментов дизайнера #figma #sketch #design'),
        
        (user_ids[8], channel_ids[9] if len(channel_ids) > 9 else None, 'text',
         'Цветовые палитры для проектов',
         '10 готовых палитр для ваших проектов #colors #palette #design'),
        
        # Посты без канала (в общую ленту)
        (user_ids[0], None, 'text',
         'Как прошёл мой день',
         'Сегодня наконец разобрался с багом, который мучил неделю! 🎉'),
        
        (user_ids[1], None, 'text',
         'Правила нашего сообщества',
         'Напоминаем: уважайте друг друга, без спама и оскорблений! ⚖️'),
        
        (user_ids[14], None, 'text',
         'Новый фотосет: осень в парке',
         'Поймала золотую осень в городском парке 🍂 #photo #autumn'),
        
        (user_ids[11], None, 'text',
         'Ищу напарника для проекта',
         'Нужен фронтендер для стартапа. Пишите в ЛС! #job #frontend #startup'),
    ]
    
    post_ids = []
    for user_id, channel_id, post_type, title, content in posts_data:
        try:
            cursor = conn.execute(
                'INSERT INTO posts (user_id, channel_id, post_type, title, content) VALUES (?, ?, ?, ?, ?)',
                (user_id, channel_id, post_type, title, content)
            )
            post_ids.append(cursor.lastrowid)
            print(f"  ✓ Пост: {title[:35]}...")
        except Exception as e:
            print(f"  ✗ Ошибка поста: {e}")
    
    # ==================== КОММЕНТАРИИ (много!) ====================
    comments_data = [
        'Отличный пост! 👍',
        'Спасибо за информацию!',
        'Очень интересно, жду продолжения',
        'Согласен на все 100%',
        'А можно подробнее?',
        'Круто! 🔥',
        'Подписался на канал',
        'Лучший контент!',
        'Наконец-то качественный материал',
        'Буду ждать новых постов',
        'Это именно то, что я искал!',
        'Сохранил в закладки 📌',
        'Автор молодец!',
        'Не согласен, но уважаю мнение',
        'Хотелось бы увидеть больше примеров',
        'Класс, спасибо! 💯',
        'Поделился с друзьями',
        'Вопрос: а как насчёт...?',
        'Это гениально!',
        'Полезная информация, благодарю',
        'Жду вторую часть!',
        'Лайк и подписка! 👊',
        'Наконец кто-то это написал',
        'Прикольно 😎',
        'Топ контент как всегда!',
    ]
    
    comment_count = 0
    for post_id in post_ids:
        num_comments = random.randint(2, 8)  # Больше комментариев
        for _ in range(num_comments):
            user_id = random.choice(user_ids) if user_ids else 1
            content = random.choice(comments_data)
            try:
                conn.execute(
                    'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                    (post_id, user_id, content)
                )
                comment_count += 1
            except:
                pass
    print(f"  ✓ Добавлено {comment_count} комментариев")
    
    # ==================== РЕАКЦИИ (много!) ====================
    reaction_types = ['like', 'dislike', 'love', 'laugh', 'wow', 'sad']
    reaction_count = 0
    for post_id in post_ids:
        num_reactions = random.randint(5, 15)  # Больше реакций
        reacted_users = random.sample(user_ids, min(num_reactions, len(user_ids))) if user_ids else []
        for user_id in reacted_users:
            reaction = random.choices(
                reaction_types, 
                weights=[50, 5, 25, 10, 8, 2]  # like чаще всего
            )[0]
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO reactions (user_id, post_id, reaction_type) VALUES (?, ?, ?)',
                    (user_id, post_id, reaction)
                )
                reaction_count += 1
            except:
                pass
    print(f"  ✓ Добавлено {reaction_count} реакций")
    
    # ==================== ПОДПИСКИ НА КАНАЛЫ ====================
    sub_count = 0
    for channel_id in channel_ids:
        num_subs = random.randint(8, 18)  # Больше подписчиков
        subscribers = random.sample(user_ids, min(num_subs, len(user_ids))) if user_ids else []
        for user_id in subscribers:
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO channel_subscribers (user_id, channel_id) VALUES (?, ?)',
                    (user_id, channel_id)
                )
                sub_count += 1
            except:
                pass
    print(f"  ✓ Добавлено {sub_count} подписок на каналы")
    
    # ==================== ГЛОБАЛЬНЫЙ ЧАТ (активный!) ====================
    chat_messages = [
        (user_ids[2], 'Привет всем! 👋'),
        (user_ids[3], 'Здравствуйте!'),
        (user_ids[4], 'Как дела у всех?'),
        (user_ids[5], 'Отличная погода сегодня ☀️'),
        (user_ids[6], 'Кто играет в новую игру?'),
        (user_ids[7], 'Готовлю ужин, кто голоден? 🍕'),
        (user_ids[2], 'Новый пост скоро выложу!'),
        (user_ids[3], 'Жду с нетерпением'),
        (user_ids[8], 'Рисую новый арт, скоро покажу'),
        (user_ids[9], 'Только с тренировки 💪'),
        (user_ids[10], 'Слушаю новый альбом, огонь!'),
        (user_ids[11], 'Кто-нибудь знает Python?'),
        (user_ids[12], 'Я знаю, что нужно?'),
        (user_ids[11], 'Помоги с одной задачей плиз'),
        (user_ids[13], 'Показываю новый дизайн сайта'),
        (user_ids[14], 'Красиво получилось!'),
        (user_ids[15], 'Планирую поездку в Грузию'),
        (user_ids[16], 'Там классно! Был в прошлом году'),
        (user_ids[17], 'Обзор нового телефона готов'),
        (user_ids[18], 'Утренняя йога - залог бодрости'),
        (user_ids[19], 'Помыл машину наконец 🚗'),
        (user_ids[20], 'Нашла классный ресторан, советую'),
        (user_ids[0], 'Модераторы, у нас всё спокойно?'),
        (user_ids[1], 'Да, всё под контролем ✅'),
        (user_ids[2], 'Спасибо за работу!'),
        (user_ids[4], 'Стрим сегодня в 20:00!'),
        (user_ids[6], 'Буду смотреть!'),
        (user_ids[12], '+1'),
        (user_ids[8], 'Я тоже подключусь'),
        (user_ids[3], 'Хорошего всем вечера! 🌙'),
    ]
    
    for user_id, content in chat_messages:
        try:
            conn.execute(
                'INSERT INTO global_chat (user_id, content) VALUES (?, ?)',
                (user_id, content)
            )
        except:
            pass
    print(f"  ✓ Добавлено {len(chat_messages)} сообщений в чат")
    
    # ==================== ЛИЧНЫЕ СООБЩЕНИЯ ====================
    conversations_created = 0
    messages_created = 0
    
    # Создаём несколько переписок
    conversation_pairs = [
        (user_ids[2], user_ids[3]),
        (user_ids[4], user_ids[6]),
        (user_ids[0], user_ids[2]),
        (user_ids[5], user_ids[7]),
        (user_ids[11], user_ids[12]),
    ]
    
    private_dialogs = [
        [
            'Привет! Видел твой пост?',
            'Да, спасибо! Старался)',
            'Очень круто получилось!',
            'Скоро будет продолжение',
            'Жду!'
        ],
        [
            'Эй, играешь сегодня?',
            'Да, в 8 вечера',
            'Окей, буду онлайн',
            'Позови остальных',
            'Уже написал им'
        ],
        [
            'Нужна помощь с постом',
            'Что случилось?',
            'Не знаю что написать',
            'Пиши от души, люди оценят',
            'Спасибо за совет!'
        ]
    ]
    
    for i, (user1, user2) in enumerate(conversation_pairs):
        user1_id, user2_id = min(user1, user2), max(user1, user2)
        try:
            cursor = conn.execute(
                'INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)',
                (user1_id, user2_id)
            )
            conv_id = cursor.lastrowid
            conversations_created += 1
            
            dialog = private_dialogs[i % len(private_dialogs)]
            for j, content in enumerate(dialog):
                sender = user1 if j % 2 == 0 else user2
                conn.execute(
                    'INSERT INTO messages (conversation_id, sender_id, content) VALUES (?, ?, ?)',
                    (conv_id, sender, content)
                )
                messages_created += 1
        except:
            pass
    
    print(f"  ✓ Создано {conversations_created} переписок с {messages_created} сообщениями")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print("="*50)
    print("\n📊 Статистика:")
    print(f"   • Пользователей: {len(users_data)}")
    print(f"   • Каналов: {len(channels_data)}")
    print(f"   • Постов: {len(posts_data)}")
    print(f"   • Комментариев: ~{comment_count}")
    print(f"   • Реакций: ~{reaction_count}")
    
    print("\n📋 ТЕСТОВЫЕ АККАУНТЫ:")
    print("-"*50)
    print("   👑 АДМИН:")
    print("      • admin / admin123")
    print("\n   🛡️ МОДЕРАТОРЫ (пароль: mod123):")
    print("      • moderator_alex")
    print("      • moderator_kate")
    print("\n   👤 ПОЛЬЗОВАТЕЛИ (пароль: pass123):")
    print("      • john_doe, alice_wonder, bob_builder")
    print("      • emma_star, max_power, lisa_cook")
    print("      • sarah_art, mike_sport, anna_music")
    print("      • peter_code, nina_photo, ivan_game")
    print("      • olga_design, denis_travel, maria_book")
    print("      • sergey_tech, elena_yoga, andrey_car")
    print("      • victoria_food")
    print("-"*50)

if __name__ == '__main__':
    create_test_data()