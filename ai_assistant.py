#!/usr/bin/env python3
"""
Простой ИИ-ассистент для терминала
Поддерживает беседу на любые темы через бесплатное API
"""

import json
import os
import requests
import sys
from pathlib import Path

class AIAssistant:
    def __init__(self):
        self.config_file = Path.home() / ".ai_assistant_config.json"
        self.history = []
        self.load_config()
        
    def load_config(self):
        """Загрузка конфигурации"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key', '')
                self.model = config.get('model', 'gpt-3.5-turbo')
        else:
            self.api_key = ''
            self.model = 'gpt-3.5-turbo'
            
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            'api_key': self.api_key,
            'model': self.model
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def setup(self):
        """Первоначальная настройка"""
        print("\n🔧 Первоначальная настройка")
        print("\nВыберите сервис:")
        print("1. OpenAI (требуется API ключ)")
        print("2. Бесплатный OpenRouter (рекомендуется)")
        
        choice = input("\nВаш выбор (1 или 2): ").strip()
        
        if choice == "1":
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.api_key = input("Введите ваш OpenAI API ключ: ").strip()
        else:
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            print("\n📝 Для OpenRouter:")
            print("1. Зарегистрируйтесь на https://openrouter.ai")
            print("2. Получите бесплатный API ключ в настройках")
            self.api_key = input("\nВведите ваш OpenRouter API ключ: ").strip()
            
        self.save_config()
        print("✅ Настройка завершена!")
        
    def chat(self, message):
        """Отправка сообщения в AI"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Добавляем контекст из истории
        messages = [{"role": "system", "content": "Вы полезный ассистент. Отвечайте кратко и по делу."}]
        messages.extend(self.history[-5:])  # Последние 5 сообщений для контекста
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            ai_message = result['choices'][0]['message']['content']
            
            # Сохраняем в историю
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_message})
            
            return ai_message
            
        except requests.exceptions.RequestException as e:
            return f"❌ Ошибка соединения: {str(e)}"
        except KeyError:
            return "❌ Ошибка в ответе API. Проверьте API ключ."
    
    def run(self):
        """Основной цикл программы"""
        print("\n🤖 Добро пожаловать в AI Ассистент!")
        print("=" * 50)
        
        if not self.api_key:
            self.setup()
        
        print("\nКоманды:")
        print("  /help   - показать помощь")
        print("  /config - изменить настройки")
        print("  /clear  - очистить историю")
        print("  /exit   - выход")
        print("\n" + "=" * 50)
        
        while True:
            try:
                user_input = input("\n💭 Вы: ").strip()
                
                if not user_input:
                    continue
                
                # Обработка команд
                if user_input.lower() == '/exit':
                    print("👋 До свидания!")
                    break
                elif user_input.lower() == '/help':
                    self.show_help()
                    continue
                elif user_input.lower() == '/config':
                    self.setup()
                    continue
                elif user_input.lower() == '/clear':
                    self.history = []
                    print("✅ История очищена")
                    continue
                
                # Отправка запроса
                print("🤔 Думаю...")
                response = self.chat(user_input)
                print(f"\n🤖 AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {str(e)}")
    
    def show_help(self):
        """Показать справку"""
        print("\n📚 Справка:")
        print("• Просто введите ваш вопрос для общения с AI")
        print("• AI помнит контекст последних сообщений")
        print("• Для смены темы используйте /clear")
        print("• Поддерживаются любые темы для обсуждения")
        print("\nДоступные модели через OpenRouter:")
        print("• GPT-3.5 Turbo (быстрый и эффективный)")
        print("• Claude 3 (хорош для анализа)")
        print("• Gemini Pro (от Google)")

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run()