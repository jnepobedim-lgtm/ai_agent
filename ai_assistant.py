#!/usr/bin/env python3
import json, os, requests, sys, subprocess, shutil, re
from pathlib import Path

DEFAULT_API_KEY = ""

class UniversalAssistant:
    def __init__(self):
        self.config_file = Path.home() / ".ai_assistant_config.json"
        self.history = []
        self.workspace = Path.cwd()
        self.mode = "chat"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.load_config()
        self.ensure_gitignore()

    def ensure_gitignore(self):
        gitignore = self.workspace / ".gitignore"
        entries = [".ai_assistant_config.json", "*.key", "*_key*", "*secret*", "config.local.json"]
        existing = set()
        if gitignore.exists():
            existing = set(gitignore.read_text().splitlines())
        with open(gitignore, 'a') as f:
            for entry in entries:
                if entry not in existing:
                    f.write(f"\n{entry}")

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
        config = {'api_key': self.api_key, 'model': self.model, 'api_url': self.api_url}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.ensure_gitignore()

    def setup(self):
        print("\n🔧 Настройка API")
        print("1. OpenAI\n2. OpenRouter (бесплатно)")
        choice = input("\nВыбор (1/2): ").strip()
        if choice == "1":
            self.api_url = "https://api.openai.com/v1/chat/completions"
        else:
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        key = input("API ключ (Enter - пропустить): ").strip()
        if key:
            self.api_key = key
        self.save_config()
        print("✅ Готово")

    def execute_shell(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.workspace, timeout=60)
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr
            return output if output else "✅ Выполнено"
        except subprocess.TimeoutExpired:
            return "⏰ Таймаут"
        except Exception as e:
            return f"❌ {str(e)}"

    def resolve_path(self, path_str):
        if not path_str:
            return self.workspace
        path_str = path_str.strip()
        if path_str.startswith('~'):
            path_str = str(Path.home()) + path_str[1:]
        if path_str.startswith('/'):
            return Path(path_str).resolve()
        return (self.workspace / path_str).resolve()

    def change_directory(self, path_str):
        if not path_str:
            return f"📂 {self.workspace}"
        target = self.resolve_path(path_str)
        if target.is_dir():
            self.workspace = target
            items = list(self.workspace.iterdir())
            files = sum(1 for i in items if i.is_file())
            dirs = sum(1 for i in items if i.is_dir())
            return f"📂 {self.workspace}\n   📁 {dirs} папок, 📄 {files} файлов"
        elif target.is_file():
            return f"❌ Это файл: {target.name}\n   📂 {target.parent}"
        else:
            return f"❌ Не найден: {target}"

    def analyze_intent(self, user_input):
        text = user_input.lower().strip()
        if text in ['..', 'назад', 'вверх', 'up']:
            return {"action": "change_dir", "params": {"path": ".."}}
        if text.startswith(('перейди в ', 'cd ', 'зайди в ')):
            return {"action": "change_dir", "params": {"path": text.split(maxsplit=2)[-1].strip()}}
        if text in ['статус', 'status']:
            return {"action": "git_status", "params": {}}
        if text in ['отправь', 'push', 'пуш']:
            return {"action": "git_push", "params": {}}
        if text in ['скачай', 'pull', 'пул']:
            return {"action": "git_pull", "params": {}}
        if text in ['список', 'файлы', 'ls', 'что тут']:
            return {"action": "list_files", "params": {}}
        if text in ['где я', 'папка', 'pwd']:
            return {"action": "show_dir", "params": {}}
        if text.startswith('создай файл '):
            parts = text[12:].strip().split(" с ", 1)
            name = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            return {"action": "file_create", "params": {"path": name, "content": content}}
        if text.startswith(('создай папку ', 'mkdir ')):
            return {"action": "folder_create", "params": {"path": text.split(maxsplit=2)[-1].strip()}}
        if text.startswith(('прочитай ', 'read ', 'cat ')):
            return {"action": "file_read", "params": {"path": text.split(maxsplit=1)[-1].strip()}}
        if text.startswith(('удали ', 'delete ', 'rm ')):
            return {"action": "file_delete", "params": {"path": text.split(maxsplit=1)[-1].strip()}}
        if text.startswith(('коммит ', 'commit ')):
            return {"action": "git_commit", "params": {"message": text.split(maxsplit=1)[-1].strip()}}
        if text.startswith('!'):
            return {"action": "shell", "params": {"command": text[1:].strip()}}
        if text.startswith(('найди ', 'search ')):
            return {"action": "search", "params": {"content": text.split(maxsplit=1)[-1].strip()}}
        if text.startswith(('установи ', 'install ')):
            return {"action": "install", "params": {"content": text.split(maxsplit=1)[-1].strip()}}
        return None

    def execute_action(self, action, params):
        try:
            if action == "shell":
                return self.execute_shell(params.get("command", ""))
            elif action == "file_create":
                path = self.resolve_path(params.get("path", "file.txt"))
                content = params.get("content", "")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return f"✅ Создан: {path}"
            elif action == "file_read":
                path = self.resolve_path(params.get("path", ""))
                if path.exists():
                    content = path.read_text()
                    if len(content) > 2000:
                        content = content[:2000] + "\n... (обрезано)"
                    return f"📄 {path.name}:\n{content}"
                return f"❌ Не найден: {path}"
            elif action == "file_edit":
                path = self.resolve_path(params.get("path", ""))
                if path.exists():
                    path.write_text(params.get("content", ""))
                    return f"✅ Обновлён: {path}"
                return f"❌ Не найден: {path}"
            elif action == "file_delete":
                path = self.resolve_path(params.get("path", ""))
                if path.exists():
                    path.unlink()
                    return f"✅ Удалён: {path}"
                return f"❌ Не найден: {path}"
            elif action == "folder_create":
                path = self.resolve_path(params.get("path", ""))
                path.mkdir(parents=True, exist_ok=True)
                return f"✅ Папка: {path}"
            elif action == "folder_delete":
                path = self.resolve_path(params.get("path", ""))
                if path.exists() and path.is_dir():
                    shutil.rmtree(path)
                    return f"✅ Удалена: {path}"
                return f"❌ Не найдена: {path}"
            elif action == "list_files":
                items = sorted(self.workspace.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                lines = []
                for item in items:
                    if item.is_dir():
                        lines.append(f"📁 {item.name}/")
                    else:
                        s = item.stat().st_size
                        if s < 1024:
                            size = f"{s}B"
                        elif s < 1024*1024:
                            size = f"{s/1024:.1f}KB"
                        else:
                            size = f"{s/1024/1024:.1f}MB"
                        lines.append(f"📄 {item.name} ({size})")
                return "\n".join(lines) if lines else "📭 Пусто"
            elif action == "git_status":
                return self.execute_shell("git status --short")
            elif action == "git_add":
                return self.execute_shell(f"git add {params.get('path', '.')}")
            elif action == "git_commit":
                return self.execute_shell(f'git commit -m "{params.get("message", "update")}"')
            elif action == "git_push":
                return self.execute_shell("git push")
            elif action == "git_pull":
                return self.execute_shell("git pull")
            elif action == "change_dir":
                return self.change_directory(params.get("path", ""))
            elif action == "show_dir":
                return f"📂 {self.workspace}"
            elif action == "search":
                return self.execute_shell(f'find . -name "*{params.get("content", "")}*" 2>/dev/null | head -20')
            elif action == "install":
                return self.execute_shell(f"pip install {params.get('content', '')}")
            elif action == "system":
                return self.execute_shell("uname -a")
            return None
        except Exception as e:
            return f"❌ {str(e)}"

    def chat_with_ai(self, message, mode="chat"):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if mode == "work":
            system_prompt = f"""Ты помощник. Текущая папка: {self.workspace}
Если пользователь просит действие — ВЫПОЛНЯЙ в формате:
ACTION: действие
PARAM1: значение
PARAM2: значение
Действия: file_create, file_read, file_edit, file_delete, folder_create, folder_delete, git_status, git_add, git_commit, git_push, git_pull, shell, list_files, change_dir, search, install"""
        else:
            system_prompt = f"Ты AI-ассистент. Папка: {self.workspace}. Отвечай на вопросы."
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.history[-20:])
        messages.append({"role": "user", "content": message})
        data = {"model": self.model, "messages": messages, "temperature": 0.7, "max_tokens": 3000}
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            ai_msg = result['choices'][0]['message']['content']
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_msg})
            if mode == "work" and "ACTION:" in ai_msg:
                action_match = re.search(r'ACTION:\s*(\w+)', ai_msg)
                if action_match:
                    action = action_match.group(1)
                    params = {}
                    m1 = re.search(r'PARAM1:\s*(.+)', ai_msg)
                    if m1:
                        params['path'] = m1.group(1).strip()
                    m2 = re.search(r'PARAM2:\s*(.+)', ai_msg)
                    if m2:
                        params['content'] = m2.group(1).strip()
                    if params:
                        exec_result = self.execute_action(action, params)
                        if exec_result:
                            return f"{ai_msg}\n\n📎 Результат:\n{exec_result}"
            return ai_msg
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def get_short_path(self):
        full = str(self.workspace)
        home = str(Path.home())
        if full.startswith(home):
            return "~" + full[len(home):]
        return full

    def run(self):
        print("\n🤖 AI АССИСТЕНТ")
        print("/work - работа  /chat - общение")
        if not self.api_key:
            print("⚠️ API ключ не задан!")
            if input("Настроить? (y/n): ").strip().lower() == 'y':
                self.setup()
            else:
                print("Оффлайн-режим")
        print(f"\n📂 {self.get_short_path()}")
        print(f"🔵 {self.mode.upper()}")
        while True:
            try:
                short_path = self.get_short_path()
                if len(short_path) > 30:
                    short_path = "..." + short_path[-27:]
                prompt = "🔧" if self.mode == "work" else "💬"
                user_input = input(f"\n{prompt} {short_path}> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['/exit', 'exit', 'выход']:
                    print("👋 Пока!")
                    break
                elif user_input.lower() == '/config':
                    self.setup()
                    continue
                elif user_input.lower() == '/clear':
                    self.history = []
                    print("✅ Очищено")
                    continue
                elif user_input.lower() == '/work':
                    self.mode = "work"
                    print(f"🔧 WORK | 📂 {self.get_short_path()}")
                    continue
                elif user_input.lower() == '/chat':
                    self.mode = "chat"
                    print(f"💬 CHAT | 📂 {self.get_short_path()}")
                    continue
                if self.mode == "work":
                    intent = self.analyze_intent(user_input)
                    if intent:
                        result = self.execute_action(intent["action"], intent.get("params", {}))
                        if result:
                            print(f"\n{result}")
                            continue
                    if self.api_key:
                        print("🤔 ...")
                        print(f"\n🤖 {self.chat_with_ai(user_input, mode='work')}")
                    else:
                        print("❌ Нужен API ключ")
                else:
                    intent = self.analyze_intent(user_input)
                    if intent:
                        print("\n💡 Это команда. /work для выполнения.")
                    if self.api_key:
                        print("🤔 ...")
                        print(f"\n🤖 {self.chat_with_ai(user_input, mode='chat')}")
                    else:
                        print("❌ Нужен API ключ")
            except KeyboardInterrupt:
                print("\n👋 Пока!")
                break
            except Exception as e:
                print(f"❌ {str(e)}")

if __name__ == "__main__":
    UniversalAssistant().run()
