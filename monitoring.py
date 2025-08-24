#!/usr/bin/env python3
"""
Система мониторинга и уведомлений для L-PE4.3-Zero-TTS
"""

import time
import json
import os
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import threading

logger = logging.getLogger(__name__)

class MonitoringSystem:
    """Система мониторинга"""
    
    def __init__(self):
        self.alerts = []
        self.metrics = {
            'total_requests': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_response_time': 0,
            'uptime': 0,
            'last_activity': None
        }
        self.config = self.load_config()
        self.monitoring_active = True
    
    def load_config(self):
        """Загрузка конфигурации мониторинга"""
        config_file = 'monitoring_config.json'
        default_config = {
            'email_notifications': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'email': '',
                'password': '',
                'recipients': []
            },
            'telegram_notifications': {
                'enabled': False,
                'bot_token': '',
                'chat_id': ''
            },
            'alerts': {
                'error_threshold': 5,
                'response_time_threshold': 30,
                'uptime_threshold': 0.95
            },
            'monitoring_interval': 60  # секунды
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации мониторинга: {e}")
        
        return default_config
    
    def save_config(self):
        """Сохранение конфигурации мониторинга"""
        try:
            with open('monitoring_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации мониторинга: {e}")
    
    def update_metrics(self, event_type, response_time=None):
        """Обновление метрик"""
        self.metrics['total_requests'] += 1
        self.metrics['last_activity'] = datetime.now()
        
        if event_type == 'success':
            self.metrics['successful_generations'] += 1
        elif event_type == 'error':
            self.metrics['failed_generations'] += 1
        
        if response_time:
            # Обновляем среднее время ответа
            current_avg = self.metrics['average_response_time']
            total_requests = self.metrics['total_requests']
            self.metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def check_alerts(self):
        """Проверка условий для уведомлений"""
        alerts = []
        
        # Проверка процента ошибок
        total_requests = self.metrics['total_requests']
        if total_requests > 0:
            error_rate = self.metrics['failed_generations'] / total_requests
            if error_rate > (1 - self.config['alerts']['uptime_threshold']):
                alerts.append({
                    'type': 'error_rate',
                    'message': f'Высокий процент ошибок: {error_rate:.2%}',
                    'severity': 'high'
                })
        
        # Проверка времени ответа
        if self.metrics['average_response_time'] > self.config['alerts']['response_time_threshold']:
            alerts.append({
                'type': 'response_time',
                'message': f'Медленное время ответа: {self.metrics["average_response_time"]:.2f}с',
                'severity': 'medium'
            })
        
        # Проверка отсутствия активности
        if self.metrics['last_activity']:
            time_since_last = datetime.now() - self.metrics['last_activity']
            if time_since_last > timedelta(minutes=30):
                alerts.append({
                    'type': 'no_activity',
                    'message': f'Нет активности {time_since_last.total_seconds() / 60:.0f} минут',
                    'severity': 'low'
                })
        
        return alerts
    
    def send_email_alert(self, alert):
        """Отправка уведомления по email"""
        if not self.config['email_notifications']['enabled']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_notifications']['email']
            msg['To'] = ', '.join(self.config['email_notifications']['recipients'])
            msg['Subject'] = f'[L-PE4.3-Zero-TTS] {alert["type"].upper()}: {alert["message"]}'
            
            body = f"""
            <html>
            <body>
                <h2>Уведомление о проблеме</h2>
                <p><strong>Тип:</strong> {alert['type']}</p>
                <p><strong>Сообщение:</strong> {alert['message']}</p>
                <p><strong>Важность:</strong> {alert['severity']}</p>
                <p><strong>Время:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <p><small>L-PE4.3-Zero-TTS Monitoring System</small></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(
                self.config['email_notifications']['smtp_server'],
                self.config['email_notifications']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email_notifications']['email'],
                self.config['email_notifications']['password']
            )
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email уведомление отправлено: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки email уведомления: {e}")
    
    def send_telegram_alert(self, alert):
        """Отправка уведомления в Telegram"""
        if not self.config['telegram_notifications']['enabled']:
            return
        
        try:
            message = f"""
🚨 **Уведомление о проблеме**

**Тип:** {alert['type']}
**Сообщение:** {alert['message']}
**Важность:** {alert['severity']}
**Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
L-PE4.3-Zero-TTS Monitoring System
            """
            
            url = f"https://api.telegram.org/bot{self.config['telegram_notifications']['bot_token']}/sendMessage"
            data = {
                'chat_id': self.config['telegram_notifications']['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info(f"Telegram уведомление отправлено: {alert['message']}")
            else:
                logger.error(f"Ошибка отправки Telegram уведомления: {response.text}")
                
        except Exception as e:
            logger.error(f"Ошибка отправки Telegram уведомления: {e}")
    
    def send_alert(self, alert):
        """Отправка уведомления всеми способами"""
        self.alerts.append({
            **alert,
            'timestamp': datetime.now().isoformat()
        })
        
        # Отправляем уведомления
        self.send_email_alert(alert)
        self.send_telegram_alert(alert)
        
        logger.warning(f"Алерт: {alert['message']}")
    
    def get_metrics(self):
        """Получение текущих метрик"""
        return {
            **self.metrics,
            'uptime_percentage': self.calculate_uptime(),
            'error_rate': self.calculate_error_rate()
        }
    
    def calculate_uptime(self):
        """Расчет времени работы"""
        total = self.metrics['total_requests']
        if total == 0:
            return 100.0
        return (self.metrics['successful_generations'] / total) * 100
    
    def calculate_error_rate(self):
        """Расчет процента ошибок"""
        total = self.metrics['total_requests']
        if total == 0:
            return 0.0
        return (self.metrics['failed_generations'] / total) * 100
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        def monitor_loop():
            while self.monitoring_active:
                try:
                    alerts = self.check_alerts()
                    for alert in alerts:
                        self.send_alert(alert)
                    
                    time.sleep(self.config['monitoring_interval'])
                except Exception as e:
                    logger.error(f"Ошибка в цикле мониторинга: {e}")
                    time.sleep(60)
        
        monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitoring_thread.start()
        logger.info("Система мониторинга запущена")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_active = False
        logger.info("Система мониторинга остановлена")
    
    def generate_report(self):
        """Генерация отчета"""
        metrics = self.get_metrics()
        
        report = f"""
# Отчет мониторинга L-PE4.3-Zero-TTS

## Общая статистика
- **Всего запросов:** {metrics['total_requests']}
- **Успешных генераций:** {metrics['successful_generations']}
- **Ошибок:** {metrics['failed_generations']}
- **Время работы:** {metrics['uptime_percentage']:.2f}%
- **Среднее время ответа:** {metrics['average_response_time']:.2f}с

## Последние алерты
"""
        
        for alert in self.alerts[-10:]:  # Последние 10 алертов
            report += f"- **{alert['timestamp']}** [{alert['severity'].upper()}] {alert['message']}\n"
        
        return report

# Создаем глобальный экземпляр системы мониторинга
monitoring_system = MonitoringSystem()

def init_monitoring():
    """Инициализация системы мониторинга"""
    monitoring_system.start_monitoring()
    return monitoring_system

if __name__ == '__main__':
    # Тестирование системы мониторинга
    print("🧪 Тестирование системы мониторинга...")
    
    monitoring = init_monitoring()
    
    # Симулируем некоторые события
    monitoring.update_metrics('success', 2.5)
    monitoring.update_metrics('error', 15.0)
    monitoring.update_metrics('success', 1.8)
    
    print("📊 Метрики:")
    print(json.dumps(monitoring.get_metrics(), indent=2, ensure_ascii=False))
    
    print("\n📋 Отчет:")
    print(monitoring.generate_report())
    
    # Останавливаем мониторинг
    monitoring.stop_monitoring()
