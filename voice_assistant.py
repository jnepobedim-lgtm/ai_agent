#!/usr/bin/env python3
"""
AI Ассистент с голосовым выводом и управлением приложениями
Текстовый ввод + голосовой ответ
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

try:
    import requests
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

DEFAULT_API_KEY = ""

class VoiceAssistant:
    def __init__(self):
        self.config_file = Path.home() / ".ai_assistant_config.json"
        self.workspace = Path.cwd()
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.load_config()
        
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key', DEFAULT_API_KEY)
                self.model = config.get('model', 'gpt-3.5-turbo')
        else:
            self.api_key = DEFAULT_API_KEY
            self.model = 'gpt-3.5-turbo'
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'api_key': self.api_key, 'model': self.model, 'api_url': self.api_url}, f, indent=2)
    
    def setup(self):
        print("\n🔧 Настройка API")
        print("1. OpenAI\n2. OpenRouter (бесплатно)")
        choice = input("\nВыбор (1/2): ").strip()
        if choice == "1":
            self.api_url = "https://api.openai.com/v1/chat/completions"
        key = input("API ключ: ").strip()
        if key:
            self.api_key = key
        self.save_config()
        print("✅ Готово")
    
    def speak(self, text):
        print(f"🤖 {text}")
        if TTS_AVAILABLE:
            try:
                tts = gTTS(text=text, lang='ru')
                tts.save('/tmp/voice.mp3')
                os.system('termux-media-player play /tmp/voice.mp3 2>/dev/null &')
            except:
                pass
    
    def open_app(self, app_name):
        app_name = app_name.lower().strip()
        
        apps = {
            'youtube': 'com.google.android.youtube',
            'ютуб': 'com.google.android.youtube',
            'chrome': 'com.android.chrome',
            'браузер': 'com.android.chrome',
            'хром': 'com.android.chrome',
            'настройки': 'com.android.settings',
            'камера': 'com.android.camera',
            'галерея': 'com.android.gallery3d',
            'калькулятор': 'com.android.calculator2',
            'календарь': 'com.android.calendar',
            'контакты': 'com.android.contacts',
            'телефон': 'com.android.dialer',
            'сообщения': 'com.android.mms',
            'файлы': 'com.android.documentsui',
            'термукс': 'com.termux',
            'telegram': 'org.telegram.messenger',
            'телеграм': 'org.telegram.messenger',
            'whatsapp': 'com.whatsapp',
            'ватсап': 'com.whatsapp',
            'spotify': 'com.spotify.music',
            'instagram': 'com.instagram.android',
            'инстаграм': 'com.instagram.android',
            'vk': 'com.vkontakte.android',
            'вк': 'com.vkontakte.android',
            'яндекс': 'ru.yandex.searchplugin',
            'карты': 'com.google.android.apps.maps',
            'диск': 'com.google.android.apps.docs',
            'почта': 'com.google.android.gm',
            'gmail': 'com.google.android.gm',
            'переводчик': 'com.google.android.apps.translate',
            'погода': 'com.google.android.apps.weather',
        }
        
        for key, package in apps.items():
            if key in app_name:
                try:
                    subprocess.run(f'monkey -p {package} -c android.intent.category.LAUNCHER 1', 
                                 shell=True, capture_output=True, timeout=3)
                    return f"✅ Открыто: {key}"
                except:
                    try:
                        subprocess.run(f'am start -n {package}/.MainActivity', 
                                     shell=True, capture_output=True, timeout=3)
                        return f"✅ Открыто: {key}"
                    except:
                        return f"❌ Не удалось: {key}"
        
        return f"❌ Не найдено: {app_name}"
    
    def close_app(self, app_name):
        app_name = app_name.lower().strip()
        
        processes = {
            'youtube': 'com.google.android.youtube',
            'ютуб': 'com.google.android.youtube',
            'chrome': 'com.android.chrome',
            'браузер': 'com.android.chrome',
            'telegram': 'org.telegram.messenger',
            'whatsapp': 'com.whatsapp',
            'spotify': 'com.spotify.music',
            'instagram': 'com.instagram.android',
            'vk': 'com.vkontakte.android',
            'камера': 'com.android.camera',
            'галерея': 'com.android.gallery3d',
        }
        
        for key, package in processes.items():
            if key in app_name:
                try:
                    subprocess.run(f'am force-stop {package}', shell=True, capture_output=True, timeout=3)
                    return f"✅ Закрыто: {key}"
                except:
                    return f"❌ Не удалось: {key}"
        
        return f"❌ Не найдено: {app_name}"
    
    def home_screen(self):
        os.system('input keyevent 3 2>/dev/null')
        return "🏠 Домой"
    
    def back(self):
        os.system('input keyevent 4 2>/dev/null')
        return "⬅️ Назад"
    
    def recent_apps(self):
        os.system('input keyevent 187 2>/dev/null')
        return "📱 Недавние"
    
    def take_screenshot(self):
        os.system('screencap -p /sdcard/screenshot.png 2>/dev/null')
        return "📸 Скриншот сохранён"
    
    def volume_up(self):
        os.system('input keyevent 24 2>/dev/null')
        return "🔊 +"
    
    def volume_down(self):
        os.system('input keyevent 25 2>/dev/null')
        return "🔉 -"
    
    def toggle_flashlight(self):
        os.system('termux-torch on 2>/dev/null || termux-torch off 2>/dev/null')
        return "🔦 Переключён"
    
    def get_time(self):
        from datetime import datetime
        now = datetime.now()
        return f"Сейчас {now.hour} часов {now.minute} минут"
    
    def get_date(self):
        from datetime import datetime
        now = datetime.now()
        months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        return f"Сегодня {now.day} {months[now.month-1]} {now.year} года"
    
    def process_command(self, text):
        t = text.lower().strip()
        
        # Открытие приложений
        if any(t.startswith(w) for w in ['открой', 'запусти', 'open', 'launch', 'включи']):
            app = t.split(maxsplit=1)[-1].strip()
            return self.open_app(app)
        
        # Закрытие приложений
        if any(t.startswith(w) for w in ['закрой', 'выйди', 'close', 'убей', 'выключи']):
            app = t.split(maxsplit=1)[-1].strip()
            return self.close_app(app)
        
        # Навигация
        if t in ['домой', 'home', 'на главный']:
            return self.home_screen()
        if t in ['назад', 'back']:
            return self.back()
        if t in ['недавние', 'recent', 'приложения']:
            return self.recent_apps()
        
        # Скриншот
        if t in ['скриншот', 'скрин', 'screenshot']:
            return self.take_screenshot()
        
        # Звук
        if t in ['громче', 'звук +', 'volume up', 'громкость больше']:
            return self.volume_up()
        if t in ['тише', 'звук -', 'volume down', 'громкость меньше']:
            return self.volume_down()
        
        # Фонарик
        if t in ['фонарик', 'flashlight', 'вспышка']:
            return self.toggle_flashlight()
        
        # Время и дата
        if t in ['время', 'час', 'time', 'сколько времени', 'который час']:
            return self.get_time()
        if t in ['дата', 'число', 'date', 'какое число', 'какой день']:
            return self.get_date()
        
        # Поиск в Google
        if t.startswith(('найди ', 'поиск ', 'search ', 'гугл ')):
            query = t.split(maxsplit=1)[-1].strip()
            query_enc = query.replace(' ', '+')
            os.system(f'am start -a android.intent.action.VIEW -d "https://google.com/search?q={query_enc}" 2>/dev/null')
            return f"🔍 Ищу: {query}"
        
        # Приветствие
        if any(w in t for w in ['привет', 'hi', 'hello', 'здравствуй']):
            return "Привет! Я твой голосовой ассистент. Скажи Открой YouTube или Который час."
        
        if t in ['помощь', 'help', 'что ты умеешь', 'команды']:
            return """Я умею:
• Открыть/закрыть приложения
• Громче/тише
• Скриншот
• Домой/назад
• Время/дата
• Найди в Google
• Фонарик"""
        
        return None
    
    def ask_ai(self, message):
        if not API_AVAILABLE or not self.api_key:
            return None
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты голосовой ассистент. Отвечай кратко (1-2 предложения), на русском языке."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except:
            return None
    
    def run(self):
        print("""
╔══════════════════════════════════╗
║    🎤 AI АССИСТЕНТ            ║
║  Текст + Голосовой ответ      ║
╚══════════════════════════════════╝
        """)
        
        if not self.api_key:
            choice = input("Настроить API? (y/n): ").strip().lower()
            if choice == 'y':
                self.setup()
        
        print("""
📱 КОМАНДЫ:
  Открой YouTube/Chrome/Telegram...
  Закрой браузер
  Громче | Тише
  Скриншот | Домой | Назад
  Время | Дата
  Найди в Google запрос
  Фонарик
  Помощь
  /exit - выход
==============================
        """)
        
        while True:
            try:
                cmd = input("💬 > ").strip()
                if not cmd:
                    continue
                
                if cmd.lower() in ['/exit', 'exit', 'выход']:
                    self.speak("До свидания!")
                    break
                
                # Обработка локальных команд
                result = self.process_command(cmd)
                
                if result:
                    self.speak(result)
                elif self.api_key:
                    ai_resp = self.ask_ai(cmd)
                    if ai_resp:
                        self.speak(ai_resp)
                    else:
                        print("❌ Не поняла. Скажите Помощь для списка команд.")
                else:
                    print("❌ Не поняла. Скажите Помощь.")
                
            except KeyboardInterrupt:
                print("\n👋 Пока!")
                break
            except Exception as e:
                print(f"❌ {e}")

if __name__ == "__main__":
    VoiceAssistant().run()
