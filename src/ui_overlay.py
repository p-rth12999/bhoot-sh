import ctypes
import math
import random
import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QApplication, QMenu
from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QAction, QCursor, QMovie, QPixmap, QRadialGradient, QLinearGradient
)

BASE_DIR = Path(__file__).resolve().parent.parent

CATEGORY_BEHAVIOR = {
    "stack_overflow_copy": ("mocking", "side_margin"),
    "deployment_error": ("enraged", "terminal"),
    "test_failure": ("enraged", "terminal"),
    "api_key_exposed": ("shocked", "cursor_side"),
    "dangerous_command": ("enraged", "terminal"),
    "force_push": ("shocked", "terminal"),
    "terrible_git_commit": ("mocking", "side_margin"),
    "distraction_tab": ("suspicious", "cursor_side"),
    "ai_assistant_tab": ("mocking", "side_margin"),
    "endless_debugging": ("enraged", "terminal"),
    "late_night_coding": ("suspicious", "side_margin"),
    "idle_warning": ("suspicious", "cursor_side"),
}


class VoidDimmer(QWidget):
    """Full-screen click-through dark horror vignette that flashes when the ghost is ENRAGED or in Poltergeist Mode."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.opacity_level = 0
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._fade_step)

    def trigger_void(self, intensity: int = 165):
        self.opacity_level = intensity
        self.show()
        self.update()
        self.fade_timer.start(45)

    def _fade_step(self):
        self.opacity_level -= 4
        if self.opacity_level <= 0:
            self.opacity_level = 0
            self.fade_timer.stop()
            self.hide()
        self.update()

    def paintEvent(self, event):
        if self.opacity_level <= 0:
            return
        painter = QPainter(self)
        w, h = self.width(), self.height()
        grad = QRadialGradient(QPointF(w / 2, h / 2), max(w, h) * 0.65)
        grad.setColorAt(0.0, QColor(0, 0, 0, int(self.opacity_level * 0.25)))
        grad.setColorAt(0.7, QColor(25, 0, 5, int(self.opacity_level * 0.75)))
        grad.setColorAt(1.0, QColor(90, 0, 15, self.opacity_level))
        painter.fillRect(0, 0, w, h, QBrush(grad))


class GhostOverlay(QWidget):
    manual_trigger = pyqtSignal(str, bool)
    lang_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(460, 290)

        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_w = screen.width()
        self.screen_h = screen.height()
        self.move(self.screen_w - 475, int(self.screen_h * 0.30))

        self.void_dimmer = VoidDimmer()

        self.angle = 0.0
        self.bob_offset = 0.0
        self.glitch_x = 0.0
        self.glitch_y = 0.0
        self.current_message = "Aa gaya mera shikaar..."
        self.current_tier = "short"
        self.mood = "suspicious"
        self.sin_count = 0
        self.lang = "hi"
        self.roaming_enabled = True
        self.drag_pos = None

        # Audio alias counter to prevent winmm.dll caching locks
        self.audio_counter = 0
        self.active_alias = None

        # Poltergeist rapid-click tracking
        self.click_timestamps = []
        self.poltergeist_steps = 0
        self.poltergeist_timer = QTimer(self)
        self.poltergeist_timer.timeout.connect(self._poltergeist_teleport_step)

        self.smoke_particles = [
            {"x": random.uniform(-35, 35), "y": random.uniform(0, 90), "r": random.uniform(6, 16), "speed": random.uniform(0.6, 1.5)}
            for _ in range(12)
        ]

        self.custom_movie = None
        self.custom_pixmap = None
        self._load_custom_sprite()

        self.roam_anim = QPropertyAnimation(self, b"pos")
        self.roam_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate)
        self.anim_timer.start(25)

        self.patrol_timer = QTimer(self)
        self.patrol_timer.timeout.connect(self._autonomous_patrol)
        self.patrol_timer.start(14000)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._clear_bubble)

    def _load_custom_sprite(self):
        gif_path = BASE_DIR / "assets" / "ghost.gif"
        png_path = BASE_DIR / "assets" / "ghost.png"
        if gif_path.exists():
            self.custom_movie = QMovie(str(gif_path))
            self.custom_movie.start()
        elif png_path.exists():
            self.custom_pixmap = QPixmap(str(png_path))

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "hi" else "hi"
        self.lang_changed.emit(self.lang)

    def _toggle_roaming(self):
        self.roaming_enabled = not self.roaming_enabled

    def _animate(self):
        self.angle += 0.08
        self.bob_offset = math.sin(self.angle) * 8.0

        for p in self.smoke_particles:
            p["y"] -= p["speed"]
            if p["y"] < -25:
                p["y"] = 95
                p["x"] = random.uniform(-35, 35)

        if self.poltergeist_steps > 0:
            self.glitch_x = random.uniform(-9.0, 9.0)
            self.glitch_y = random.uniform(-9.0, 9.0)
        elif self.mood == "enraged" or self.current_tier == "long":
            self.glitch_x = random.uniform(-4.5, 4.5)
            self.glitch_y = random.uniform(-4.5, 4.5)
        elif self.mood == "shocked":
            self.glitch_x = random.uniform(-2.5, 2.5)
            self.glitch_y = 0.0
        else:
            self.glitch_x = 0.0
            self.glitch_y = 0.0

        self.update()

    def _clear_bubble(self):
        self.current_message = ""
        self.mood = "suspicious"
        self.update()

    def _autonomous_patrol(self):
        if not self.roaming_enabled or self.current_message or self.poltergeist_steps > 0:
            return
        spots = [
            (self.screen_w - 475, int(self.screen_h * 0.22)),
            (self.screen_w - 475, int(self.screen_h * 0.50)),
            (int(self.screen_w * 0.55), self.screen_h - 320),
        ]
        tx, ty = random.choice(spots)
        self.roam_to(tx, ty, duration=2800)

    def roam_to(self, target_x: int, target_y: int, duration: int = 1200):
        if not self.roaming_enabled and self.poltergeist_steps == 0:
            return
        target_x = max(20, min(target_x, self.screen_w - self.width() - 15))
        target_y = max(20, min(target_y, self.screen_h - self.height() - 15))
        self.roam_anim.stop()
        self.roam_anim.setDuration(duration)
        self.roam_anim.setStartValue(self.pos())
        self.roam_anim.setEndValue(QPoint(int(target_x), int(target_y)))
        self.roam_anim.start()

    def roam_to_zone(self, zone: str):
        if zone == "terminal":
            self.roam_to(int(self.screen_w * 0.48), self.screen_h - 325, 950)
        elif zone == "side_margin":
            self.roam_to(self.screen_w - 475, int(self.screen_h * 0.34), 1100)
        elif zone == "cursor_side":
            cursor = QCursor.pos()
            offset_x = cursor.x() + 40 if cursor.x() < self.screen_w - 520 else cursor.x() - 480
            self.roam_to(offset_x, cursor.y() - 90, 800)
        else:
            self.roam_to(self.screen_w - 475, self.screen_h - 320, 1200)

    def show_roast(self, message: str, tier: str = "short", sin_count: int = 0, audio_path: str | None = None, category: str = ""):
        self.current_message = message
        self.current_tier = tier
        self.sin_count = sin_count

        mood, zone = CATEGORY_BEHAVIOR.get(category, ("suspicious", "side_margin"))
        if tier == "long":
            mood = "enraged"
            self.void_dimmer.trigger_void(165)
        self.mood = mood

        self.roam_to_zone(zone)
        self.update()
        self.hide_timer.start(9000)

        if audio_path:
            self._play_audio_native(audio_path)

    def _play_audio_native(self, audio_path: str):
        """Plays MP3 using a unique MCI alias per playback so Windows never drops English or Hinglish files."""
        try:
            resolved = Path(audio_path).resolve()
            if not resolved.exists():
                print(f"[bhoot.sh] ⚠️ Audio file missing: {resolved}")
                return

            if sys.platform == "win32":
                mci = ctypes.windll.winmm.mciSendStringW
                if self.active_alias:
                    mci(f"stop {self.active_alias}", None, 0, 0)
                    mci(f"close {self.active_alias}", None, 0, 0)

                self.audio_counter += 1
                self.active_alias = f"bhoot_snd_{self.audio_counter}"

                cmd_open = f'open "{str(resolved)}" type mpegvideo alias {self.active_alias}'
                err = mci(cmd_open, None, 0, 0)
                if err != 0:
                    # Fallback without type specifier if codec wrapper prefers auto-detect
                    mci(f'open "{str(resolved)}" alias {self.active_alias}', None, 0, 0)

                mci(f"play {self.active_alias}", None, 0, 0)
                print(f"[bhoot.sh] 🔊 Playing [{self.active_alias}]: {resolved.name}")
        except Exception as e:
            print(f"[bhoot.sh] Audio error: {e}")

    def _trigger_poltergeist_mode(self):
        """Harmless UI-only chaos when the user spam-clicks the ghost 5 times rapidly."""
        self.mood = "enraged"
        self.current_tier = "long"
        self.void_dimmer.trigger_void(210)

        if self.lang == "hi":
            self.current_message = (
                "⚠️ [POLTERGEIST OVERRIDE] System32 deletion initiated... 48%...\n"
                "Mazaak kar raha hoon! Par mujhe baar baar poke mat kar, developer babu!"
            )
            snd = BASE_DIR / "assets" / "audio" / "hi_deployment_error_long_0.mp3"
        else:
            self.current_message = (
                "⚠️ [POLTERGEIST OVERRIDE] Deleting unsaved git branches... 64%...\n"
                "Just kidding, bro. Stop poking me and go fix your code!"
            )
            snd = BASE_DIR / "assets" / "audio" / "en_deployment_error_long_0.mp3"

        if snd.exists():
            self._play_audio_native(str(snd))

        self.poltergeist_steps = 6
        self.poltergeist_timer.start(280)
        self.hide_timer.start(9500)

    def _poltergeist_teleport_step(self):
        if self.poltergeist_steps <= 0:
            self.poltergeist_timer.stop()
            self.roam_to_zone("side_margin")
            return

        self.poltergeist_steps -= 1
        rand_x = random.randint(40, max(100, self.screen_w - self.width() - 40))
        rand_y = random.randint(40, max(100, self.screen_h - self.height() - 60))
        self.move(rand_x, rand_y)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gx = 315 + self.glitch_x
        gy = 75 + self.bob_offset + self.glitch_y

        if self.mood == "enraged" or self.current_tier == "long" or self.poltergeist_steps > 0:
            glow_inner = QColor(220, 0, 30, 175)
            glow_outer = QColor(90, 0, 10, 75)
            accent_col = QColor(255, 35, 55)
        elif self.mood == "shocked":
            glow_inner = QColor(160, 0, 240, 155)
            glow_outer = QColor(60, 0, 110, 65)
            accent_col = QColor(200, 75, 255)
        else:
            glow_inner = QColor(0, 190, 165, 130)
            glow_outer = QColor(0, 60, 70, 55)
            accent_col = QColor(0, 230, 195)

        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.smoke_particles:
            alpha = int(max(0, min(140, (p["y"] + 25) * 1.2)))
            painter.setBrush(QBrush(QColor(12, 12, 18, alpha)))
            painter.drawEllipse(QPointF(gx + 55 + p["x"], gy + 45 + p["y"]), p["r"], p["r"])

        grad = QRadialGradient(QPointF(gx + 55, gy + 60), 82)
        grad.setColorAt(0.0, glow_inner)
        grad.setColorAt(0.55, glow_outer)
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QRectF(gx - 25, gy - 20, 160, 165))

        if self.custom_movie is not None:
            frame = self.custom_movie.currentPixmap()
            if not frame.isNull():
                painter.drawPixmap(int(gx), int(gy), 115, 115, frame)
        elif self.custom_pixmap is not None:
            painter.drawPixmap(int(gx), int(gy), 115, 115, self.custom_pixmap)
        else:
            self._draw_grim_wraith(painter, gx, gy, accent_col)

        if self.current_message:
            bubble_rect = QRectF(8, 22, 290, 175)
            painter.setBrush(QBrush(QColor(8, 8, 12, 246)))
            painter.setPen(QPen(accent_col, 2.2))
            painter.drawRoundedRect(bubble_rect, 10, 10)

            tail = QPainterPath()
            tail.moveTo(298, 92)
            tail.lineTo(318, 104)
            tail.lineTo(298, 114)
            painter.fillPath(tail, QBrush(accent_col))

            painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            painter.setPen(accent_col)
            header = f"☠ BHOOT.SH [{self.lang.upper()}] | SINS:{self.sin_count} | {self.current_tier.upper()}"
            painter.drawText(QRectF(20, 30, 265, 18), Qt.AlignmentFlag.AlignLeft, header)

            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            painter.setPen(QColor(235, 240, 245))
            painter.drawText(
                QRectF(20, 52, 265, 132),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                self.current_message
            )

    def _draw_grim_wraith(self, painter: QPainter, gx: float, gy: float, accent_col: QColor):
        cloak = QPainterPath()
        cloak.moveTo(gx + 55, gy - 8)
        cloak.cubicTo(gx + 95, gy + 5, gx + 108, gy + 45, gx + 105, gy + 110)

        for i in range(5):
            tx = gx + 105 - (i * 20)
            ty = gy + 115 + math.sin(self.angle * 2.2 + i * 1.4) * 10
            cloak.lineTo(tx - 10, ty + 14)
            cloak.lineTo(tx - 20, ty - 4)

        cloak.cubicTo(gx + 2, gy + 45, gx + 15, gy + 5, gx + 55, gy - 8)
        cloak.closeSubpath()

        cloak_grad = QLinearGradient(QPointF(gx + 55, gy - 8), QPointF(gx + 55, gy + 130))
        cloak_grad.setColorAt(0.0, QColor(28, 30, 38, 252))
        cloak_grad.setColorAt(0.6, QColor(12, 13, 18, 248))
        cloak_grad.setColorAt(1.0, QColor(5, 5, 8, 180))

        painter.setBrush(QBrush(cloak_grad))
        painter.setPen(QPen(accent_col, 2.0))
        painter.drawPath(cloak)

        void_face = QPainterPath()
        void_face.addEllipse(QRectF(gx + 20, gy + 18, 70, 76))
        painter.setBrush(QBrush(QColor(3, 3, 5, 250)))
        painter.setPen(QPen(QColor(40, 45, 55), 1.2))
        painter.drawPath(void_face)

        left_eye = QPointF(gx + 39, gy + 46)
        right_eye = QPointF(gx + 71, gy + 46)

        cursor_global = QCursor.pos()
        ghost_screen_center = self.mapToGlobal(QPoint(int(gx + 55), int(gy + 46)))
        dx = cursor_global.x() - ghost_screen_center.x()
        dy = cursor_global.y() - ghost_screen_center.y()
        dist = math.hypot(dx, dy) or 1.0
        px = (dx / dist) * 5.0
        py = (dy / dist) * 3.8

        eye_col = QColor(255, 15, 30) if (self.mood == "enraged" or self.current_tier == "long" or self.poltergeist_steps > 0) else accent_col
        for ec in (left_eye, right_eye):
            eye_glow = QRadialGradient(QPointF(ec.x() + px, ec.y() + py), 12)
            eye_glow.setColorAt(0.0, QColor(255, 255, 255, 255))
            eye_glow.setColorAt(0.35, eye_col)
            eye_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(eye_glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(ec.x() + px, ec.y() + py), 11, 8 if self.mood != "shocked" else 12)

        painter.setPen(QPen(QColor(3, 3, 5), 5.0))
        if self.mood == "enraged" or self.current_tier == "long":
            painter.drawLine(QPointF(gx + 25, gy + 34), QPointF(gx + 50, gy + 43))
            painter.drawLine(QPointF(gx + 85, gy + 34), QPointF(gx + 60, gy + 43))
        elif self.mood == "mocking":
            painter.drawLine(QPointF(gx + 25, gy + 40), QPointF(gx + 48, gy + 37))
            painter.drawLine(QPointF(gx + 62, gy + 41), QPointF(gx + 85, gy + 32))

        if self.mood == "shocked":
            painter.setBrush(QBrush(QColor(15, 0, 25)))
            painter.setPen(QPen(eye_col, 2.0))
            painter.drawEllipse(QPointF(gx + 55, gy + 74), 9, 13)
        else:
            maw = QPainterPath()
            maw.moveTo(gx + 28, gy + 70)
            maw.lineTo(gx + 37, gy + 78)
            maw.lineTo(gx + 45, gy + 71)
            maw.lineTo(gx + 55, gy + 81)
            maw.lineTo(gx + 65, gy + 71)
            maw.lineTo(gx + 73, gy + 78)
            maw.lineTo(gx + 82, gy + 70)
            painter.setPen(QPen(eye_col, 2.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(maw)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            now = time.time()
            # Keep only clicks within the last 2.8 seconds
            self.click_timestamps = [t for t in self.click_timestamps if now - t < 2.8]
            self.click_timestamps.append(now)

            if len(self.click_timestamps) >= 5:
                self.click_timestamps.clear()
                self._trigger_poltergeist_mode()
                event.accept()
                return

            self.roam_anim.stop()
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None and self.poltergeist_steps == 0:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #0b0b10; color: #e0f0ff; border: 1px solid #ff2337; font-family: Segoe UI; }"
            "QMenu::item:selected { background-color: #ff2337; color: #ffffff; font-weight: bold; }"
        )

        lang_action = QAction(f"🌐 Language: {'Hinglish (Daniel)' if self.lang == 'hi' else 'English (Clyde)'} — Click to Switch", self)
        lang_action.triggered.connect(self._toggle_lang)
        menu.addAction(lang_action)

        roam_action = QAction(f"👻 Stalker Roaming: {'ON' if self.roaming_enabled else 'OFF'}", self)
        roam_action.triggered.connect(self._toggle_roaming)
        menu.addAction(roam_action)

        menu.addSeparator()

        for cat, label in [
            ("stack_overflow_copy", "📋 Simulate StackOverflow Copy (Side Margin Glare)"),
            ("deployment_error", "💥 Simulate Terminal Crash (Enraged + Terminal Roam)"),
            ("api_key_exposed", "🔑 Simulate API Key Leak (Shocked + Cursor Stalk)"),
            ("terrible_git_commit", "💩 Simulate 'fix bug' Commit (Mocking Glare)"),
            ("distraction_tab", "📱 Simulate Reels Distraction (Cursor Stalk)"),
        ]:
            act = QAction(label, self)
            act.triggered.connect(lambda checked, c=cat: self.manual_trigger.emit(c, False))
            menu.addAction(act)

        menu.addSeparator()
        llm_act = QAction("🧠 Force Live Gemma-2 Few-Shot Roast (Async QThread + Sentry)", self)
        llm_act.triggered.connect(lambda: self.manual_trigger.emit("endless_debugging", True))
        menu.addAction(llm_act)

        poltergeist_act = QAction("⚡ Trigger Poltergeist Mode (Or Spam-Click Ghost 5x)", self)
        poltergeist_act.triggered.connect(self._trigger_poltergeist_mode)
        menu.addAction(poltergeist_act)

        menu.addSeparator()
        quit_act = QAction("❌ Exorcise Ghost (Quit)", self)
        quit_act.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_act)

        menu.exec(event.globalPos())