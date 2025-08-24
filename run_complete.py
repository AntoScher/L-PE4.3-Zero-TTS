#!/usr/bin/env python3
"""
Полный запуск всех компонентов L-PE4.3-Zero-TTS
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class CompleteSystem:
    """Полная система L-PE4.3-Zero-TTS"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        
    def check_dependencies(self):
        """Проверка всех зависимостей"""
        print("🔍 Проверка зависимостей...")
        
        required_files = [
            'main.py',
            'voice.py',
            'config.py',
            'requirements.txt'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
            return False
        
        print("✅ Все файлы найдены")
        return True
    
    def install_dependencies(self):
        """Установка зависимостей"""
        print("📦 Установка зависимостей...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, capture_output=True, text=True)
            print("✅ Зависимости установлены")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки зависимостей: {e}")
            return False
    
    def start_bot(self):
        """Запуск основного бота"""
        print("🤖 Запуск основного бота...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes['bot'] = process
            print("✅ Бот запущен")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска бота: {e}")
            return False
    
    def start_web_interface(self):
        """Запуск веб-интерфейса"""
        print("🌐 Запуск веб-интерфейса...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'web_interface.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes['web'] = process
            print("✅ Веб-интерфейс запущен")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска веб-интерфейса: {e}")
            return False
    
    def start_monitoring(self):
        """Запуск системы мониторинга"""
        print("📊 Запуск системы мониторинга...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'monitoring.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes['monitoring'] = process
            print("✅ Мониторинг запущен")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска мониторинга: {e}")
            return False
    
    def run_tests(self):
        """Запуск тестов"""
        print("🧪 Запуск тестов...")
        
        try:
            result = subprocess.run([
                sys.executable, 'run_tests.py'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Тесты прошли успешно")
                return True
            else:
                print("⚠️ Некоторые тесты не прошли")
                print(result.stdout)
                return False
        except subprocess.TimeoutExpired:
            print("❌ Тесты превысили лимит времени")
            return False
        except Exception as e:
            print(f"❌ Ошибка запуска тестов: {e}")
            return False
    
    def show_status(self):
        """Показать статус всех компонентов"""
        print("\n📊 Статус компонентов:")
        print("=" * 40)
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"✅ {name}: Работает (PID: {process.pid})")
            else:
                print(f"❌ {name}: Остановлен")
    
    def stop_all(self):
        """Остановка всех процессов"""
        print("\n⏹️ Остановка всех компонентов...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} остановлен")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {name} принудительно остановлен")
            except Exception as e:
                print(f"❌ Ошибка остановки {name}: {e}")
        
        self.running = False
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print(f"\n🛑 Получен сигнал {signum}, завершение работы...")
        self.stop_all()
        sys.exit(0)
    
    def monitor_processes(self):
        """Мониторинг процессов"""
        while self.running:
            time.sleep(10)
            
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    print(f"⚠️ Процесс {name} завершился неожиданно")
                    # Можно добавить автоматический перезапуск
                    del self.processes[name]
    
    def start_complete_system(self):
        """Запуск полной системы"""
        print("🚀 Запуск полной системы L-PE4.3-Zero-TTS")
        print("=" * 50)
        
        # Проверяем зависимости
        if not self.check_dependencies():
            return False
        
        # Устанавливаем зависимости
        if not self.install_dependencies():
            return False
        
        # Запускаем тесты
        if not self.run_tests():
            print("⚠️ Продолжаем несмотря на ошибки тестов...")
        
        # Запускаем компоненты
        success = True
        
        if not self.start_bot():
            success = False
        
        if not self.start_web_interface():
            print("⚠️ Веб-интерфейс не запущен, но система продолжает работу")
        
        if not self.start_monitoring():
            print("⚠️ Мониторинг не запущен, но система продолжает работу")
        
        if not success:
            print("❌ Не удалось запустить основные компоненты")
            return False
        
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        
        # Запускаем мониторинг процессов в отдельном потоке
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        print("\n🎉 Система запущена!")
        print("📱 Telegram бот: готов к работе")
        print("🌐 Веб-интерфейс: http://localhost:5000")
        print("📊 Мониторинг: активен")
        print("\n⏹️ Для остановки нажмите Ctrl+C")
        
        # Основной цикл
        try:
            while self.running:
                time.sleep(1)
                # Показываем статус каждые 60 секунд
                if int(time.time()) % 60 == 0:
                    self.show_status()
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
        finally:
            self.stop_all()
        
        return True

def main():
    """Основная функция"""
    system = CompleteSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            system.run_tests()
        elif command == 'bot':
            system.start_bot()
        elif command == 'web':
            system.start_web_interface()
        elif command == 'monitoring':
            system.start_monitoring()
        elif command == 'install':
            system.install_dependencies()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("Доступные команды: test, bot, web, monitoring, install")
            return 1
    else:
        # Полный запуск
        system.start_complete_system()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
