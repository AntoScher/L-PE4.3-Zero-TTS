#!/usr/bin/env python3
"""
Скрипт для быстрого запуска и проверки проекта L-PE4.3-Zero-TTS
"""

import sys
import os
import subprocess
import time

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_config():
    """Проверка конфигурации"""
    if not os.path.exists('config.py'):
        print("❌ Файл config.py не найден")
        print("📝 Создайте config.py на основе config.example.py")
        return False
    
    try:
        import config
        if not hasattr(config, 'bot_token') or not hasattr(config, 'elevenlabs_api_key'):
            print("❌ В config.py отсутствуют необходимые переменные")
            return False
        print("✅ Конфигурация загружена")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта config.py: {e}")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = ['telebot', 'elevenlabs']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📥 Установите недостающие пакеты:")
        print(f"pip install -r requirements.txt")
        return False
    
    return True

def run_quick_test():
    """Быстрый тест основных компонентов"""
    print("\n🧪 Быстрый тест компонентов...")
    
    try:
        # Тест импорта модулей
        from voice import get_all_voices, generate_audio
        print("✅ Модули voice.py импортированы")
        
        # Тест создания бота (без запуска)
        import telebot
        bot = telebot.TeleBot("test_token")
        print("✅ Telegram бот создан")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def start_bot():
    """Запуск бота"""
    print("\n🚀 Запуск бота...")
    
    try:
        # Запускаем бота в отдельном процессе
        process = subprocess.Popen([sys.executable, 'main.py'])
        
        print("✅ Бот запущен!")
        print("📱 Отправьте /start в Telegram боту")
        print("⏹️ Для остановки нажмите Ctrl+C")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Остановка бота...")
            process.terminate()
            process.wait()
            print("✅ Бот остановлен")
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

def main():
    """Основная функция"""
    print("🎵 L-PE4.3-Zero-TTS - Запуск и проверка")
    print("=" * 50)
    
    # Проверки
    checks = [
        ("Версия Python", check_python_version),
        ("Конфигурация", check_config),
        ("Зависимости", check_dependencies),
        ("Тест компонентов", run_quick_test)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Некоторые проверки не прошли. Исправьте ошибки и попробуйте снова.")
        return 1
    
    print("\n🎉 Все проверки прошли успешно!")
    
    # Спрашиваем пользователя о запуске
    response = input("\n🚀 Запустить бота? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'да', 'д']:
        start_bot()
    else:
        print("👋 До свидания!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
