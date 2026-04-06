import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

DATABASE = 'Web_DB.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    print("🚀 Создание тестовых данных...")
    
    users_data = [
        ('john_doe', 'john@test.com', 'pass123', 'user', 'Люблю программирование и кофе ☕'),
        ('alice_wonder', 'alice@test.com', 'pass123', 'user', 'Фотограф и путешественница 📸'),
        ('bob_builder', 'bob@test.com', 'pass123', 'user', 'Строю миры из кода 🏗️'),
        ('emma_star', 'emma@test.com', 'pass123', 'user', 'Музыкант и художник 🎨'),
        ('max_power', 'max@test.com', 'pass123', 'user', 'Геймер и стример 🎮'),
        ('lisa_cook', 'lisa@test.com', 'pass123', 'user', 'Готовлю вкусняшки 🍕'),
        ('david_tech', 'david@test.com', 'pass123', 'moderator', 'Техноблогер и модератор 🔧'),
        ('sarah_art', 'sarah@test.com', 'pass123', 'user', 'Digital artist ✨'),
        ('mike_sport', 'mike@test.com', 'pass123', 'user', 'Фитнес и здоровый образ жизни 💪'),
        ('anna_music', 'anna@test.com', 'pass123', 'user', 'Музыка - моя жизнь 🎵'),
    ]
    
    user_ids = []
    for username, email, password, role, bio in users_data:
        try:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, role, bio) VALUES (?, ?, ?, ?, ?)',
                (username, email, hash_password(password), role, bio)
            )
            user_ids.append(cursor.lastrowid)
            print(f"  ✓ Пользователь: {username}")
        except sqlite3.IntegrityError:
            existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                user_ids.append(existing['id'])
            print(f"  → Пользователь {username} уже существует")
    
    channels_data = [
        ('TechNews', 'Новости технологий и IT индустрии 🖥️', user_ids[0] if user_ids else 1),
        ('GameZone', 'Игры, обзоры и стримы 🎮', user_ids[4] if len(user_ids) > 4 else 1),
        ('ArtCorner', 'Искусство и творчество 🎨', user_ids[7] if len(user_ids) > 7 else 1),
        ('MusicWorld', 'Музыка всех жанров 🎵', user_ids[9] if len(user_ids) > 9 else 1),
        ('FoodLovers', 'Рецепты и кулинария 🍕', user_ids[5] if len(user_ids) > 5 else 1),
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
    
    posts_data = [
        (user_ids[0] if user_ids else 1, channel_ids[0] if channel_ids else None, 'text', 
         'Новый iPhone 16 представлен!', 
         'Apple представила новую линейку смартфонов с революционными функциями ИИ. #apple #iphone #tech'),
        
        (user_ids[1] if len(user_ids) > 1 else 1, None, 'text',
         'Путешествие по Италии',
         'Только вернулась из невероятного путешествия! Рим, Флоренция, Венеция - каждый город уникален 🇮🇹 #travel #italy #photography'),
        
        (user_ids[2] if len(user_ids) > 2 else 1, channel_ids[0] if channel_ids else None, 'text',
         'Python vs JavaScript в 2026',
         'Сравнение двух популярных языков программирования. Какой выбрать для старта? #python #javascript #coding'),
        
        (user_ids[3] if len(user_ids) > 3 else 1, channel_ids[2] if len(channel_ids) > 2 else None, 'text',
         'Мой новый арт',
         'Работал над этим рисунком целую неделю! Что думаете? #art #digital #creative'),
        
        (user_ids[4] if len(user_ids) > 4 else 1, channel_ids[1] if len(channel_ids) > 1 else None, 'text',
         'Обзор GTA 6',
         'Наконец-то дождались! Первые впечатления от новой части легендарной серии 🎮 #gta6 #gaming #review'),
        
        (user_ids[5] if len(user_ids) > 5 else 1, channel_ids[4] if len(channel_ids) > 4 else None, 'text',
         'Рецепт идеальной пасты',
         'Делюсь секретом итальянской карбонары от шефа! 🍝 #food #recipe #pasta'),
        
        (user_ids[6] if len(user_ids) > 6 else 1, channel_ids[0] if channel_ids else None, 'text',
         'Правила сообщества',
         'Напоминаем о правилах нашего канала. Уважайте друг друга! #rules #community'),
        
        (user_ids[7] if len(user_ids) > 7 else 1, channel_ids[2] if len(channel_ids) > 2 else None, 'text',
         'Туториал по Blender',
         'Начинаем серию уроков по 3D моделированию для новичков #blender #3d #tutorial'),
        
        (user_ids[8] if len(user_ids) > 8 else 1, None, 'text',
         'Утренняя тренировка',
         'Начинайте день правильно! Вот моя программа на 30 минут 💪 #fitness #morning #workout'),
        
        (user_ids[9] if len(user_ids) > 9 else 1, channel_ids[3] if len(channel_ids) > 3 else None, 'text',
         'Топ-10 альбомов года',
         'Мой личный рейтинг лучших музыкальных релизов 2026 🎵 #music #top10 #albums'),
    ]
    
    post_ids = []
    for user_id, channel_id, post_type, title, content in posts_data:
        try:
            cursor = conn.execute(
                'INSERT INTO posts (user_id, channel_id, post_type, title, content) VALUES (?, ?, ?, ?, ?)',
                (user_id, channel_id, post_type, title, content)
            )
            post_ids.append(cursor.lastrowid)
            print(f"  ✓ Пост: {title[:30]}...")
        except Exception as e:
            print(f"  ✗ Ошибка поста: {e}")
    
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
    ]
    
    for post_id in post_ids:
        num_comments = random.randint(1, 4)
        for _ in range(num_comments):
            user_id = random.choice(user_ids) if user_ids else 1
            content = random.choice(comments_data)
            try:
                conn.execute(
                    'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
                    (post_id, user_id, content)
                )
            except:
                pass
    print(f"  ✓ Добавлены комментарии")
    
    reaction_types = ['like', 'dislike', 'love', 'laugh', 'wow', 'sad']
    for post_id in post_ids:
        num_reactions = random.randint(3, 10)
        reacted_users = random.sample(user_ids, min(num_reactions, len(user_ids))) if user_ids else []
        for user_id in reacted_users:
            reaction = random.choice(reaction_types)
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO reactions (user_id, post_id, reaction_type) VALUES (?, ?, ?)',
                    (user_id, post_id, reaction)
                )
            except:
                pass
    print(f"  ✓ Добавлены реакции")
    
    for channel_id in channel_ids:
        num_subs = random.randint(2, 6)
        subscribers = random.sample(user_ids, min(num_subs, len(user_ids))) if user_ids else []
        for user_id in subscribers:
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO channel_subscribers (user_id, channel_id) VALUES (?, ?)',
                    (user_id, channel_id)
                )
            except:
                pass
    print(f"  ✓ Добавлены подписки на каналы")
    
    chat_messages = [
        (user_ids[0] if user_ids else 1, 'Привет всем! 👋'),
        (user_ids[1] if len(user_ids) > 1 else 1, 'Здравствуйте!'),
        (user_ids[2] if len(user_ids) > 2 else 1, 'Как дела?'),
        (user_ids[3] if len(user_ids) > 3 else 1, 'Отличная погода сегодня ☀️'),
        (user_ids[4] if len(user_ids) > 4 else 1, 'Кто играет в новую игру?'),
        (user_ids[5] if len(user_ids) > 5 else 1, 'Готовлю ужин, кто голоден? 🍕'),
        (user_ids[0] if user_ids else 1, 'Новый пост скоро!'),
        (user_ids[1] if len(user_ids) > 1 else 1, 'Жду с нетерпением'),
    ]
    
    for user_id, content in chat_messages:
        try:
            conn.execute(
                'INSERT INTO global_chat (user_id, content) VALUES (?, ?)',
                (user_id, content)
            )
        except:
            pass
    print(f"  ✓ Добавлены сообщения в чат")
    
    if len(user_ids) >= 2:
        user1_id, user2_id = min(user_ids[0], user_ids[1]), max(user_ids[0], user_ids[1])
        try:
            cursor = conn.execute(
                'INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)',
                (user1_id, user2_id)
            )
            conv_id = cursor.lastrowid
            
            private_msgs = [
                (user_ids[0], 'Привет! Видел твой пост?'),
                (user_ids[1], 'Да, отличный материал!'),
                (user_ids[0], 'Спасибо! Скоро будет продолжение'),
            ]
            
            for sender_id, content in private_msgs:
                conn.execute(
                    'INSERT INTO messages (conversation_id, sender_id, content) VALUES (?, ?, ?)',
                    (conv_id, sender_id, content)
                )
            print(f"  ✓ Добавлены личные сообщения")
        except:
            pass
    
    conn.commit()
    conn.close()
    
    print("\n✅ Тестовые данные успешно созданы!")
    print("\n📋 Тестовые аккаунты (пароль для всех: pass123):")
    print("   • admin (администратор)")
    print("   • david_tech (модератор)")
    print("   • john_doe, alice_wonder, bob_builder... (пользователи)")

if __name__ == '__main__':
    create_test_data()