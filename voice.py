from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
import config
import logging

# Настройка логирования для модуля voice
logger = logging.getLogger(__name__)

# Инициализация клиента ElevenLabs
try:
    client = ElevenLabs(api_key=config.elevenlabs_api_key)
    logger.info("ElevenLabs клиент успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации ElevenLabs клиента: {e}")
    client = None

def get_all_voices():
    """Получение всех доступных голосов с обработкой ошибок"""
    try:
        if not client:
            raise Exception("ElevenLabs клиент не инициализирован")
        
        voices = client.voices.get_all()
        logger.info(f"Успешно получено {len(voices.voices)} голосов")
        return voices
    except Exception as e:
        logger.error(f"Ошибка получения голосов: {e}")
        raise Exception(f"Не удалось получить список голосов: {str(e)}")

def generate_audio(text: str, voice_id: str, stability: float = 0.75, 
                  similarity_boost: float = 0.5, style: float = 0.0, 
                  use_speaker_boost: bool = True):
    """
    Генерация аудио с настраиваемыми параметрами
    
    Args:
        text (str): Текст для озвучивания
        voice_id (str): ID голоса
        stability (float): Стабильность голоса (0.0 - 1.0)
        similarity_boost (float): Усиление схожести (0.0 - 1.0)
        style (float): Стиль голоса (0.0 - 1.0)
        use_speaker_boost (bool): Использовать усиление динамика
    
    Returns:
        Генератор аудио данных
    """
    try:
        if not client:
            raise Exception("ElevenLabs клиент не инициализирован")
        
        if not text or not text.strip():
            raise Exception("Текст не может быть пустым")
        
        if len(text) > 5000:
            raise Exception("Текст слишком длинный (максимум 5000 символов)")
        
        # Валидация параметров
        stability = max(0.0, min(1.0, stability))
        similarity_boost = max(0.0, min(1.0, similarity_boost))
        style = max(0.0, min(1.0, style))
        
        logger.info(f"Генерация аудио: голос={voice_id}, длина_текста={len(text)}, "
                   f"стабильность={stability}, схожесть={similarity_boost}, стиль={style}")
        
        # Создание настроек голоса
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost
        )
        
        # Создание объекта голоса
        voice = Voice(
            voice_id=voice_id,
            settings=voice_settings
        )
        
        # Генерация аудио
        audio = client.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )
        
        logger.info("Аудио успешно сгенерировано")
        return audio
        
    except Exception as e:
        logger.error(f"Ошибка генерации аудио: {e}")
        raise Exception(f"Ошибка генерации аудио: {str(e)}")

def get_voice_info(voice_id: str):
    """Получение информации о конкретном голосе"""
    try:
        if not client:
            raise Exception("ElevenLabs клиент не инициализирован")
        
        voice_info = client.voices.get(voice_id)
        logger.info(f"Получена информация о голосе: {voice_info.name}")
        return voice_info
    except Exception as e:
        logger.error(f"Ошибка получения информации о голосе {voice_id}: {e}")
        raise Exception(f"Не удалось получить информацию о голосе: {str(e)}")

def validate_voice_id(voice_id: str):
    """Проверка существования голоса"""
    try:
        if not client:
            return False
        
        voices = client.voices.get_all()
        return any(voice.voice_id == voice_id for voice in voices.voices)
    except Exception as e:
        logger.error(f"Ошибка валидации voice_id {voice_id}: {e}")
        return False

def get_available_models():
    """Получение списка доступных моделей"""
    try:
        if not client:
            raise Exception("ElevenLabs клиент не инициализирован")
        
        models = client.models.get_all()
        logger.info(f"Получено {len(models)} доступных моделей")
        return models
    except Exception as e:
        logger.error(f"Ошибка получения моделей: {e}")
        raise Exception(f"Не удалось получить список моделей: {str(e)}")
