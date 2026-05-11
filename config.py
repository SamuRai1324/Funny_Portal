import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'aura-nexus-super-secret-key-2026'
DATABASE = os.path.join(BASE_DIR, 'Web_DB.db')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
UPLOAD_FOLDERS = {
    'videos': os.path.join(UPLOAD_FOLDER, 'videos'),
    'photos': os.path.join(UPLOAD_FOLDER, 'photos'),
    'audio': os.path.join(UPLOAD_FOLDER, 'audio'),
    'stories': os.path.join(UPLOAD_FOLDER, 'stories'),
    'avatars': os.path.join(UPLOAD_FOLDER, 'avatars'),
    'banners': os.path.join(UPLOAD_FOLDER, 'banners'),
}

MAX_FILE_SIZES = {
    'video': 100 * 1024 * 1024,
    'photo': 20 * 1024 * 1024,
    'audio': 30 * 1024 * 1024,
    'avatar': 5 * 1024 * 1024,
    'banner': 10 * 1024 * 1024,
}

ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'webm', 'mov'},
    'photo': {'jpg', 'jpeg', 'png', 'gif', 'webp'},
    'audio': {'mp3', 'wav', 'ogg'},
}

MAX_PHOTOS_PER_POST = 10
STORY_LIFETIME_HOURS = 24

CHAT_SPAM_MESSAGES = 3
CHAT_SPAM_SECONDS = 5
CHAT_COOLDOWN_SECONDS = 20

ROLES = {
    'user': 1,
    'moderator': 2,
    'admin': 3,
}

REACTION_TYPES = ['like', 'dislike', 'love', 'laugh', 'wow', 'sad']

REPORT_CATEGORIES = [
    ('spam', 'Спам'),
    ('offensive', 'Оскорбления'),
    ('adult', 'Контент 18+'),
    ('violation', 'Нарушение правил'),
    ('other', 'Другое'),
]

POST_TYPE_LABELS = {
    'text': 'Пост',
    'video': 'Видео',
    'photo': 'Фото',
    'audio': 'Аудио',
    'article': 'Статья',
    'story': 'История',
}

NSFW_KEYWORDS = [
    'порно', 'порнография', 'xxx', 'секс видео', 'эротика',
    'наркотики', 'купить наркотики', 'закладки',
    'убить', 'убийство', 'терроризм', 'взрыв',
    'нацизм', 'фашизм', 'расизм',
]

FONT_FAMILY = "'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

for folder in UPLOAD_FOLDERS.values():
    os.makedirs(folder, exist_ok=True)