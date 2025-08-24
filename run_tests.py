#!/usr/bin/env python3
"""
Скрипт для запуска тестов проекта L-PE4.3-Zero-TTS
"""

import sys
import os
import subprocess
import time

def run_python_tests():
    """Запуск Python тестов"""
    print("🧪 Запуск Python тестов...")
    
    try:
        result = subprocess.run([sys.executable, 'tests.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Python тесты прошли успешно!")
            print(result.stdout)
            return True
        else:
            print("❌ Python тесты не прошли!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Тесты превысили лимит времени (60 секунд)")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    print("📦 Проверка зависимостей...")
    
    required_packages = ['pyTelegramBotAPI', 'elevenlabs']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📥 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_config_files():
    """Проверка конфигурационных файлов"""
    print("⚙️ Проверка конфигурационных файлов...")
    
    required_files = [
        'requirements.txt',
        'config.example.py',
        'main.py',
        'voice.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - отсутствует")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    return True

def check_docker_files():
    """Проверка Docker файлов"""
    print("🐳 Проверка Docker файлов...")
    
    docker_files = ['Dockerfile', 'docker-compose.yml']
    
    for file in docker_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - отсутствует")
    
    return True

def main():
    """Основная функция"""
    print("🚀 Запуск проверки проекта L-PE4.3-Zero-TTS")
    print("=" * 50)
    
    start_time = time.time()
    
    # Проверяем файлы
    config_ok = check_config_files()
    docker_ok = check_docker_files()
    
    # Проверяем зависимости
    deps_ok = check_dependencies()
    
    # Запускаем тесты
    tests_ok = run_python_tests()
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ПРОВЕРКИ:")
    print(f"⚙️ Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"🐳 Docker файлы: {'✅' if docker_ok else '❌'}")
    print(f"📦 Зависимости: {'✅' if deps_ok else '❌'}")
    print(f"🧪 Тесты: {'✅' if tests_ok else '❌'}")
    
    total_time = time.time() - start_time
    print(f"⏱️ Время выполнения: {total_time:.2f} секунд")
    
    if all([config_ok, docker_ok, deps_ok, tests_ok]):
        print("\n🎉 Все проверки прошли успешно!")
        return 0
    else:
        print("\n⚠️ Некоторые проверки не прошли. Исправьте ошибки и попробуйте снова.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
