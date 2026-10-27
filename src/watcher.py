import re
import time
from datetime import datetime
import pyperclip
import pygetwindow as gw
from PyQt6.QtCore import QThread, pyqtSignal

class SystemWatcher(QThread):
    event_detected = pyqtSignal(str, str)  # (category, snippet_context)

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_clipboard = ""
        try:
            self.last_clipboard = pyperclip.paste()
        except Exception:
            pass
        self.last_activity_time = time.time()
        self.last_window_title = ""
        self.last_trigger_time = 0

    def run(self):
        while self.running:
            now = time.time()

            # 1. Monitor Clipboard Changes
            try:
                current_clip = pyperclip.paste()
                if current_clip and current_clip != self.last_clipboard:
                    self.last_clipboard = current_clip
                    self.last_activity_time = now
                    category = self._classify_clipboard(current_clip)
                    self._emit_throttled(category, current_clip[:80], cooldown=3)
            except Exception:
                pass

            # 2. Monitor Active Window Title (Distraction / AI / Terminal)
            try:
                win = gw.getActiveWindow()
                if win and win.title and win.title != self.last_window_title:
                    self.last_window_title = win.title
                    self.last_activity_time = now
                    title_lower = win.title.lower()

                    if any(w in title_lower for w in ["youtube", "instagram", "netflix", "reddit", "twitter", "x.com"]):
                        self._emit_throttled("distraction_tab", win.title, cooldown=20)
                    elif any(w in title_lower for w in ["chatgpt", "claude", "copilot"]):
                        self._emit_throttled("ai_assistant_tab", win.title, cooldown=25)
            except Exception:
                pass

            # 3. Monitor Late Night Coding (Between 1 AM and 5 AM)
            hour = datetime.now().hour
            if 1 <= hour <= 4 and (now - self.last_trigger_time > 180):
                self._emit_throttled("late_night_coding", f"Coding at {hour}:00 AM", cooldown=180)

            # 4. Monitor Idle Time (No clipboard or window switch for 90 seconds)
            if now - self.last_activity_time > 90:
                self.last_activity_time = now
                self._emit_throttled("idle_warning", "User idle for 90s", cooldown=30)

            time.sleep(1.0)

    def _classify_clipboard(self, text: str) -> str:
        t_low = text.lower().strip()

        # Check for exposed API keys / tokens
        if re.search(r"(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|mongodb\+srv://|AIza[0-9A-Za-z-_]{30,}|api_key\s*=)", text):
            return "api_key_exposed"
        # Dangerous commands
        if any(cmd in t_low for cmd in ["rm -rf", "git reset --hard", "drop table"]):
            return "dangerous_command"
        # Force push
        if "push --force" in t_low or "push -f" in t_low:
            return "force_push"
        # Merge conflict markers
        if "<<<<<<<" in text or "=======" in text:
            return "merge_conflict"
        # Console log debugging
        if "console.log(" in t_low or "print(" in t_low:
            return "console_log_debugging"
        # TODO comments
        if "todo:" in t_low or "// todo" in t_low or "# todo" in t_low:
            return "todo_comment"
        # Traceback / Error copied
        if any(err in t_low for err in ["traceback", "exception", "error:", "failed", "exit code 1"]):
            return "deployment_error"
        # Default code copy
        return "stack_overflow_copy"

    def _emit_throttled(self, category: str, context: str, cooldown: int = 5):
        now = time.time()
        if now - self.last_trigger_time >= cooldown:
            self.last_trigger_time = now
            self.event_detected.emit(category, context)