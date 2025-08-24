import telebot
import config
import io
import time
import logging
import json
import os
from voice import get_all_voices, generate_audio
from monitoring import monitoring_system

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
API_TOKEN = config.bot_token
bot = telebot.TeleBot(API_TOKEN)

# Файл для сохранения настроек пользователей
USER_SETTINGS_FILE = 'user_settings.json'

def load_user_settings():
    """Загрузка настроек пользователей из файла"""
    try:
        if os.path.exists(USER_SETTINGS_FILE):
            with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек пользователей: {e}")
        return {}

def save_user_settings(settings):
    """Сохранение настроек пользователей в файл"""
    try:
        with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек пользователей: {e}")

# Загружаем настройки пользователей
user_settings = load_user_settings()

# Получаем все голоса из модуля voice.py
try:
    voices = get_all_voices()
    logger.info(f"Загружено {len(voices.voices)} голосов")
except Exception as e:
    logger.error(f"Ошибка загрузки голосов: {e}")
    voices = None

# Создание клавиатуры для выбора голоса
voice_buttons = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
if voices:
    for voice in voices.voices:
        voice_name = voice.name
        button = telebot.types.KeyboardButton(voice_name)
        voice_buttons.add(button)

# Добавляем кнопку настроек
settings_button = telebot.types.KeyboardButton("⚙️ Настройки")
voice_buttons.add(settings_button)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
    
    welcome_text = (
        "Привет! Я бот для создания озвучки! 🎵\n\n"
        "Выбери голос, который будет использоваться при создании озвучки:\n\n"
        "💡 Как использовать:\n"
        "1. Выберите голос из списка\n"
        "2. Введите текст для озвучки\n"
        "3. Получите аудиофайл\n\n"
        "Используйте /help для получения справки"
    )
    
    bot.reply_to(message, welcome_text, reply_markup=voice_buttons)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🤖 **Справка по использованию бота**\n\n"
        "**Основные команды:**\n"
        "/start - Запуск бота и выбор голоса\n"
        "/help - Показать эту справку\n"
        "/settings - Настройки пользователя\n"
        "/status - Статус бота\n\n"
        "**Как создать озвучку:**\n"
        "1. Выберите голос из предложенных вариантов\n"
        "2. Введите любой текст (до 5000 символов)\n"
        "3. Дождитесь генерации аудио\n"
        "4. Получите готовый аудиофайл\n\n"
        "**Поддерживаемые языки:**\n"
        "Русский, английский, испанский, французский и другие\n\n"
        "**Ограничения:**\n"
        "• Максимум 5000 символов за раз\n"
        "• Только текстовые сообщения"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['settings'])
def show_settings(message):
    user_id = message.from_user.id
    user_setting = user_settings.get(str(user_id), {})
    
    settings_text = (
        "⚙️ **Ваши настройки:**\n\n"
        f"🎤 **Выбранный голос:** {user_setting.get('selected_voice', 'Не выбран')}\n"
        f"📊 **Стабильность:** {user_setting.get('stability', 0.75)}\n"
        f"🎯 **Схожесть:** {user_setting.get('similarity_boost', 0.5)}\n"
        f"🎨 **Стиль:** {user_setting.get('style', 0.0)}\n\n"
        "Используйте /start для изменения голоса"
    )
    bot.reply_to(message, settings_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def show_status(message):
    status_text = (
        "📊 **Статус бота:**\n\n"
        f"✅ **Бот активен:** Да\n"
        f"🎤 **Доступно голосов:** {len(voices.voices) if voices else 0}\n"
        f"👥 **Пользователей:** {len(user_settings)}\n"
        f"🕒 **Время работы:** {time.strftime('%H:%M:%S')}\n\n"
        "Все системы работают нормально! 🚀"
    )
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⚙️ Настройки")
def handle_settings_button(message):
    show_settings(message)

@bot.message_handler(func=lambda message: message.text in [voice.name for voice in voices.voices] if voices else [])
def voice_selected(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    selected_voice_name = message.text
    
    # Сохраняем выбор голоса в настройки пользователя
    if str(user_id) not in user_settings:
        user_settings[str(user_id)] = {}
    
    user_settings[str(user_id)]['selected_voice'] = selected_voice_name
    save_user_settings(user_settings)
    
    logger.info(f"Пользователь {username} (ID: {user_id}) выбрал голос: {selected_voice_name}")
    
    bot.reply_to(message, f"✅ Вы выбрали голос: **{selected_voice_name}**\n\nТеперь введите текст для озвучки:", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def generate_voice(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    text = message.text
    
    # Проверяем длину текста
    if len(text) > 5000:
        bot.reply_to(message, "❌ Текст слишком длинный! Максимум 5000 символов.")
        return
    
    # Проверяем, выбран ли голос
    user_setting = user_settings.get(str(user_id), {})
    if 'selected_voice' not in user_setting:
        bot.reply_to(message, "❌ Сначала выберите голос командой /start")
        return
    
    try:
        # Ищем голос по имени
        voice_name = user_setting['selected_voice']
        voice = next((v for v in voices.voices if v.name == voice_name), None)
        
        if not voice:
            bot.reply_to(message, "❌ Выбранный голос не найден. Выберите голос заново командой /start")
            return
        
        voice_id = voice.voice_id
        
        # Отправляем сообщение о начале генерации
        processing_msg = bot.reply_to(message, "🔄 Генерирую аудио... Пожалуйста, подождите.")
        
        logger.info(f"Начинаю генерацию аудио для пользователя {username} (ID: {user_id})")
        start_time = time.time()
        
        # Генерация аудио с выбранным голосом
        audio_generator = generate_audio(
            text, 
            voice_id,
            stability=user_setting.get('stability', 0.75),
            similarity_boost=user_setting.get('similarity_boost', 0.5),
            style=user_setting.get('style', 0.0)
        )
        
        # Запись аудио в байтовый поток
        audio_bytes = io.BytesIO()
        for chunk in audio_generator:
            audio_bytes.write(chunk)
        
        # Сохраняем аудио в файл и отправляем пользователю
        audio_bytes.seek(0)
        
        # Удаляем сообщение о обработке
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Отправляем аудио
        bot.send_audio(
            user_id, 
            audio_bytes,
            title=f"Озвучка: {text[:50]}{'...' if len(text) > 50 else ''}",
            performer="L-PE4.3-Zero-TTS",
            caption=f"🎤 Голос: {voice_name}\n📝 Текст: {text[:100]}{'...' if len(text) > 100 else ''}"
        )
        
        logger.info(f"Успешно сгенерировано аудио для пользователя {username} (ID: {user_id})")
        monitoring_system.update_metrics('success', time.time() - start_time)
        
    except Exception as e:
        logger.error(f"Ошибка генерации аудио для пользователя {username} (ID: {user_id}): {e}")
        monitoring_system.update_metrics('error')
        bot.reply_to(message, f"❌ Произошла ошибка при генерации аудио: {str(e)}")

if __name__ == '__main__':
    logger.info("Запуск бота L-PE4.3-Zero-TTS")
    
    # Инициализируем систему мониторинга
    try:
        monitoring_system.start_monitoring()
        logger.info("Система мониторинга запущена")
    except Exception as e:
        logger.error(f"Ошибка запуска мониторинга: {e}")
    
    # Проверяем информацию о webhook'е
    try:
        webhook_info = bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        
        # Если ранее был установлен webhook, удаляем его
        if webhook_info.url:
            bot.remove_webhook()
            logger.info("Удалён активный webhook.")
    except Exception as e:
        logger.error(f"Ошибка при проверке webhook: {e}")
    
    # Запускаем polling в цикле с обработкой исключений
    while True:
        try:
            logger.info("Бот запущен и ожидает сообщения...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as ex:
            logger.error(f"Ошибка при polling: {ex}")
            monitoring_system.update_metrics('error')
            time.sleep(15)  # задержка 15 секунд перед повторной попыткой