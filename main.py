import telebot
import config
import io
import time
from voice import get_all_voices, generate_audio

# Инициализация бота
API_TOKEN = config.bot_token
bot = telebot.TeleBot(API_TOKEN)

# Получаем все голоса из модуля voice.py
voices = get_all_voices()

# Создание клавиатуры для выбора голоса
voice_buttons = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for voice in voices.voices:
    voice_name = voice.name  # Получаем имя голоса
    button = telebot.types.KeyboardButton(voice_name)
    voice_buttons.add(button)

# Словарь для хранения выбранного голоса пользователем
selected_voice = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот для создания озвучки! Выбери голос, который будет использоваться при создании озвучки:",
        reply_markup=voice_buttons
    )

@bot.message_handler(func=lambda message: message.text in [voice.name for voice in voices.voices])
def voice_selected(message):
    user_id = message.from_user.id
    selected_voice[user_id] = message.text
    bot.reply_to(message, f"Вы выбрали голос: {message.text}. Теперь введите текст для озвучки:")

@bot.message_handler(func=lambda message: True)
def generate_voice(message):
    user_id = message.from_user.id
    if user_id in selected_voice:
        # Ищем голос по имени
        voice_name = selected_voice[user_id]
        voice = next(voice for voice in voices.voices if voice.name == voice_name)
        voice_id = voice.voice_id

        # Генерация аудио с выбранным голосом с использованием функции из voice.py
        audio_generator = generate_audio(message.text, voice_id)

        # Запись аудио в байтовый поток
        audio_bytes = io.BytesIO()
        for chunk in audio_generator:
            audio_bytes.write(chunk)

        # Сохраняем аудио в файл и отправляем пользователю
        audio_bytes.seek(0)  # Возвращаемся в начало потока
        bot.send_audio(user_id, audio_bytes)
    else:
        bot.reply_to(message, "Сначала выберите голос командой /start")

if __name__ == '__main__':
    # Проверяем информацию о webhook'е
    webhook_info = bot.get_webhook_info()
    print("Webhook info:", webhook_info)

    # Если ранее был установлен webhook, удаляем его
    if webhook_info.url:
        bot.remove_webhook()
        print("Удалён активный webhook.")

    # Запускаем polling в цикле с обработкой исключений, чтобы бот не падал при временных сетевых ошибках
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            print(f"Ошибка при polling: {ex}")
            time.sleep(15)  # задержка 15 секунд перед повторной попыткой