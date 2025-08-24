import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Добавляем корневую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestVoiceModule(unittest.TestCase):
    """Тесты для модуля voice.py"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок для config
        self.config_mock = Mock()
        self.config_mock.elevenlabs_api_key = "test_api_key"
        
        # Патчим импорт config
        self.config_patcher = patch('voice.config', self.config_mock)
        self.config_patcher.start()
        
        # Импортируем модуль voice после патчинга
        from voice import get_all_voices, generate_audio, validate_voice_id
        
        self.get_all_voices = get_all_voices
        self.generate_audio = generate_audio
        self.validate_voice_id = validate_voice_id
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.config_patcher.stop()
    
    @patch('voice.client')
    def test_get_all_voices_success(self, mock_client):
        """Тест успешного получения голосов"""
        # Мокаем ответ от API
        mock_voices = Mock()
        mock_voices.voices = [
            Mock(name="Voice 1", voice_id="voice1"),
            Mock(name="Voice 2", voice_id="voice2")
        ]
        mock_client.voices.get_all.return_value = mock_voices
        
        result = self.get_all_voices()
        
        self.assertEqual(len(result.voices), 2)
        self.assertEqual(result.voices[0].name, "Voice 1")
        self.assertEqual(result.voices[1].name, "Voice 2")
    
    @patch('voice.client')
    def test_get_all_voices_error(self, mock_client):
        """Тест обработки ошибки при получении голосов"""
        mock_client.voices.get_all.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception) as context:
            self.get_all_voices()
        
        self.assertIn("Не удалось получить список голосов", str(context.exception))
    
    @patch('voice.client')
    def test_generate_audio_success(self, mock_client):
        """Тест успешной генерации аудио"""
        # Мокаем генератор аудио
        mock_audio = [b"audio_data_1", b"audio_data_2"]
        mock_client.generate.return_value = mock_audio
        
        result = self.generate_audio("Test text", "voice1")
        
        self.assertEqual(result, mock_audio)
        mock_client.generate.assert_called_once()
    
    def test_generate_audio_empty_text(self):
        """Тест генерации аудио с пустым текстом"""
        with self.assertRaises(Exception) as context:
            self.generate_audio("", "voice1")
        
        self.assertIn("Текст не может быть пустым", str(context.exception))
    
    def test_generate_audio_long_text(self):
        """Тест генерации аудио с длинным текстом"""
        long_text = "a" * 5001
        
        with self.assertRaises(Exception) as context:
            self.generate_audio(long_text, "voice1")
        
        self.assertIn("Текст слишком длинный", str(context.exception))
    
    @patch('voice.client')
    def test_validate_voice_id_true(self, mock_client):
        """Тест валидации существующего voice_id"""
        mock_voices = Mock()
        mock_voices.voices = [
            Mock(voice_id="voice1"),
            Mock(voice_id="voice2")
        ]
        mock_client.voices.get_all.return_value = mock_voices
        
        result = self.validate_voice_id("voice1")
        self.assertTrue(result)
    
    @patch('voice.client')
    def test_validate_voice_id_false(self, mock_client):
        """Тест валидации несуществующего voice_id"""
        mock_voices = Mock()
        mock_voices.voices = [
            Mock(voice_id="voice1"),
            Mock(voice_id="voice2")
        ]
        mock_client.voices.get_all.return_value = mock_voices
        
        result = self.validate_voice_id("voice3")
        self.assertFalse(result)

class TestMainModule(unittest.TestCase):
    """Тесты для модуля main.py"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок для config
        self.config_mock = Mock()
        self.config_mock.bot_token = "test_bot_token"
        
        # Патчим импорт config
        self.config_patcher = patch('main.config', self.config_mock)
        self.config_patcher.start()
        
        # Патчим telebot
        self.telebot_patcher = patch('main.telebot')
        self.mock_telebot = self.telebot_patcher.start()
        
        # Патчим voice модуль
        self.voice_patcher = patch('main.get_all_voices')
        self.mock_get_voices = self.voice_patcher.start()
        
        # Создаем мок для голосов
        self.mock_voices = Mock()
        self.mock_voices.voices = [
            Mock(name="Voice 1", voice_id="voice1"),
            Mock(name="Voice 2", voice_id="voice2")
        ]
        self.mock_get_voices.return_value = self.mock_voices
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.config_patcher.stop()
        self.telebot_patcher.stop()
        self.voice_patcher.stop()
    
    def test_load_user_settings_file_exists(self):
        """Тест загрузки настроек пользователей при существующем файле"""
        # Создаем временный файл с настройками
        test_settings = {"123": {"selected_voice": "Voice 1"}}
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(test_settings)
            
            # Импортируем функцию после патчинга
            from main import load_user_settings
            result = load_user_settings()
            
            self.assertEqual(result, test_settings)
    
    def test_load_user_settings_file_not_exists(self):
        """Тест загрузки настроек пользователей при отсутствующем файле"""
        with patch('os.path.exists', return_value=False):
            from main import load_user_settings
            result = load_user_settings()
            
            self.assertEqual(result, {})
    
    def test_save_user_settings(self):
        """Тест сохранения настроек пользователей"""
        test_settings = {"123": {"selected_voice": "Voice 1"}}
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            from main import save_user_settings
            save_user_settings(test_settings)
            
            mock_file.write.assert_called_once()

class TestConfiguration(unittest.TestCase):
    """Тесты конфигурации"""
    
    def test_config_file_structure(self):
        """Тест структуры файла конфигурации"""
        # Проверяем, что config.example.py существует
        self.assertTrue(os.path.exists('config.example.py'))
        
        # Проверяем содержимое файла
        with open('config.example.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('bot_token', content)
        self.assertIn('elevenlabs_api_key', content)
        self.assertIn('YOUR_TELEGRAM_BOT_TOKEN_HERE', content)
        self.assertIn('YOUR_ELEVENLABS_API_KEY_HERE', content)

class TestRequirements(unittest.TestCase):
    """Тесты зависимостей"""
    
    def test_requirements_file_exists(self):
        """Тест существования файла requirements.txt"""
        self.assertTrue(os.path.exists('requirements.txt'))
    
    def test_requirements_content(self):
        """Тест содержимого файла requirements.txt"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
        self.assertIn('pyTelegramBotAPI', content)
        self.assertIn('elevenlabs', content)

def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestVoiceModule))
    suite.addTests(loader.loadTestsFromTestCase(TestMainModule))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirements))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
