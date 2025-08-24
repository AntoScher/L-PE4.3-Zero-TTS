#!/usr/bin/env python3
"""
Веб-интерфейс для управления L-PE4.3-Zero-TTS ботом
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os
import time
import threading
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotManager:
    """Менеджер для управления ботом"""
    
    def __init__(self):
        self.bot_process = None
        self.is_running = False
        self.stats = {
            'total_requests': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'active_users': 0,
            'start_time': None
        }
        self.recent_logs = []
    
    def start_bot(self):
        """Запуск бота"""
        if not self.is_running:
            try:
                import subprocess
                self.bot_process = subprocess.Popen(['python', 'main.py'])
                self.is_running = True
                self.stats['start_time'] = datetime.now()
                logger.info("Бот запущен")
                return True
            except Exception as e:
                logger.error(f"Ошибка запуска бота: {e}")
                return False
        return False
    
    def stop_bot(self):
        """Остановка бота"""
        if self.is_running and self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait()
                self.is_running = False
                logger.info("Бот остановлен")
                return True
            except Exception as e:
                logger.error(f"Ошибка остановки бота: {e}")
                return False
        return False
    
    def get_status(self):
        """Получение статуса бота"""
        return {
            'is_running': self.is_running,
            'stats': self.stats,
            'uptime': self.get_uptime()
        }
    
    def get_uptime(self):
        """Получение времени работы"""
        if self.stats['start_time']:
            delta = datetime.now() - self.stats['start_time']
            return str(delta).split('.')[0]
        return "Не запущен"
    
    def update_stats(self, event_type):
        """Обновление статистики"""
        self.stats['total_requests'] += 1
        if event_type == 'success':
            self.stats['successful_generations'] += 1
        elif event_type == 'error':
            self.stats['failed_generations'] += 1

# Создаем экземпляр менеджера
bot_manager = BotManager()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', status=bot_manager.get_status())

@app.route('/api/status')
def api_status():
    """API для получения статуса"""
    return jsonify(bot_manager.get_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """API для запуска бота"""
    success = bot_manager.start_bot()
    return jsonify({'success': success})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API для остановки бота"""
    success = bot_manager.stop_bot()
    return jsonify({'success': success})

@app.route('/api/logs')
def api_logs():
    """API для получения логов"""
    try:
        with open('bot.log', 'r', encoding='utf-8') as f:
            logs = f.readlines()[-100:]  # Последние 100 строк
        return jsonify({'logs': logs})
    except FileNotFoundError:
        return jsonify({'logs': []})

@app.route('/api/users')
def api_users():
    """API для получения пользователей"""
    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        return jsonify({'users': users})
    except FileNotFoundError:
        return jsonify({'users': {}})

@app.route('/dashboard')
def dashboard():
    """Панель управления"""
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    """Обработка подключения WebSocket"""
    emit('status_update', bot_manager.get_status())

@socketio.on('request_status')
def handle_status_request():
    """Обработка запроса статуса"""
    emit('status_update', bot_manager.get_status())

def create_templates():
    """Создание HTML шаблонов"""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Создаем базовый шаблон
    base_template = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}L-PE4.3-Zero-TTS{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-card { transition: all 0.3s ease; }
        .status-card:hover { transform: translateY(-2px); }
        .log-container { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-microphone"></i> L-PE4.3-Zero-TTS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">Панель управления</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Создаем главную страницу
    index_template = '''{% extends "base.html" %}

{% block title %}Главная - L-PE4.3-Zero-TTS{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card status-card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-robot"></i> Статус бота
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="d-flex align-items-center mb-3">
                            <div class="status-indicator me-3" id="status-indicator"></div>
                            <div>
                                <h6 class="mb-0">Статус</h6>
                                <small class="text-muted" id="status-text">Загрузка...</small>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Время работы</h6>
                            <p class="mb-0" id="uptime">-</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="d-grid gap-2">
                            <button class="btn btn-success" id="start-btn" onclick="startBot()">
                                <i class="fas fa-play"></i> Запустить
                            </button>
                            <button class="btn btn-danger" id="stop-btn" onclick="stopBot()">
                                <i class="fas fa-stop"></i> Остановить
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card status-card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-chart-bar"></i> Статистика
                </h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-6">
                        <h4 id="total-requests">0</h4>
                        <small class="text-muted">Запросов</small>
                    </div>
                    <div class="col-6">
                        <h4 id="successful">0</h4>
                        <small class="text-muted">Успешно</small>
                    </div>
                </div>
                <hr>
                <div class="row text-center">
                    <div class="col-6">
                        <h4 id="failed">0</h4>
                        <small class="text-muted">Ошибок</small>
                    </div>
                    <div class="col-6">
                        <h4 id="active-users">0</h4>
                        <small class="text-muted">Пользователей</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-terminal"></i> Последние логи
                </h5>
            </div>
            <div class="card-body">
                <div class="log-container" id="logs">
                    <p class="text-muted">Загрузка логов...</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
const socket = io();

socket.on('status_update', function(data) {
    updateStatus(data);
});

function updateStatus(data) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (data.is_running) {
        indicator.className = 'status-indicator bg-success';
        indicator.style.width = '20px';
        indicator.style.height = '20px';
        indicator.style.borderRadius = '50%';
        statusText.textContent = 'Работает';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        indicator.className = 'status-indicator bg-danger';
        indicator.style.width = '20px';
        indicator.style.height = '20px';
        indicator.style.borderRadius = '50%';
        statusText.textContent = 'Остановлен';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
    
    document.getElementById('uptime').textContent = data.uptime;
    document.getElementById('total-requests').textContent = data.stats.total_requests;
    document.getElementById('successful').textContent = data.stats.successful_generations;
    document.getElementById('failed').textContent = data.stats.failed_generations;
    document.getElementById('active-users').textContent = data.stats.active_users;
}

function startBot() {
    fetch('/api/start', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                socket.emit('request_status');
            }
        });
}

function stopBot() {
    fetch('/api/stop', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                socket.emit('request_status');
            }
        });
}

function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs');
            if (data.logs.length > 0) {
                logsContainer.innerHTML = data.logs.map(log => 
                    `<div class="log-entry"><small>${log}</small></div>`
                ).join('');
            } else {
                logsContainer.innerHTML = '<p class="text-muted">Логи не найдены</p>';
            }
        });
}

// Загружаем данные при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    socket.emit('request_status');
    loadLogs();
    
    // Обновляем логи каждые 10 секунд
    setInterval(loadLogs, 10000);
});
</script>
{% endblock %}'''
    
    # Создаем панель управления
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Панель управления - L-PE4.3-Zero-TTS{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h2><i class="fas fa-cogs"></i> Панель управления</h2>
        <hr>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-users"></i> Пользователи
                </h5>
            </div>
            <div class="card-body">
                <div id="users-list">
                    <p class="text-muted">Загрузка пользователей...</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-chart-line"></i> График активности
                </h5>
            </div>
            <div class="card-body">
                <canvas id="activity-chart"></canvas>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function loadUsers() {
    fetch('/api/users')
        .then(response => response.json())
        .then(data => {
            const usersList = document.getElementById('users-list');
            if (Object.keys(data.users).length > 0) {
                const usersHtml = Object.entries(data.users).map(([id, settings]) => 
                    `<div class="user-item mb-2">
                        <strong>ID: ${id}</strong><br>
                        <small class="text-muted">Голос: ${settings.selected_voice || 'Не выбран'}</small>
                    </div>`
                ).join('');
                usersList.innerHTML = usersHtml;
            } else {
                usersList.innerHTML = '<p class="text-muted">Пользователи не найдены</p>';
            }
        });
}

// Загружаем пользователей при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    
    // Обновляем каждые 30 секунд
    setInterval(loadUsers, 30000);
});
</script>
{% endblock %}'''
    
    # Сохраняем шаблоны
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(dashboard_template)

if __name__ == '__main__':
    # Создаем шаблоны при первом запуске
    create_templates()
    
    print("🌐 Запуск веб-интерфейса...")
    print("📱 Откройте http://localhost:5000 в браузере")
    
    # Запускаем Flask приложение
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
