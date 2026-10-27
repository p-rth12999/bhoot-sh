import ctypes
import math
import random
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QApplication, QMenu
from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QAction, QCursor, QMovie, QPixmap, QRadialGradient
)

BASE_DIR = Path(__file__).resolve().parent.parent

CATEGORY_BEHAVIOR = {
    "stack_overflow_copy": ("mocking", "editor"),
    "deployment_error": ("enraged", "terminal"),
    "test_failure": ("enraged", "terminal"),
    "api_key_exposed": ("shocked", "cursor"),
    "dangerous_command": ("shocked", "terminal"),
    "force_push": ("shocked", "terminal"),
    "terrible_git_commit": ("mocking", "editor"),
    "distraction_tab": ("suspicious", "cursor"),
    "ai_assistant_tab": ("mocking", "cursor"),
    "endless_debugging": ("enraged", "terminal"),
    "late_night_coding": ("suspicious", "corner"),
    "idle_warning": ("suspicious", "cursor"),
}


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
        self.resize(450, 280)

        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_w = screen.width()
        self.screen_h = screen.height()
        self.move(self.screen_w - 470, self.screen_h - 320)

        self.angle = 0.0
        self.bob_offset = 0.0
        self.glitch_x = 0.0
        self.glitch_y = 0.0
        self.current_message = "Bhoot hazir hai... teri har line dekh raha hoon."
        self.current_tier = "short"
        self.mood = "suspicious"
        self.sin_count = 0
        self.lang = "hi"
        self.roaming_enabled = True
        self.drag_pos = None

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
        self.patrol_timer.start(18000)

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
        self.angle += 0.09
        self.bob_offset = math.sin(self.angle) * 9.0

        if self.mood == "enraged" or self.current_tier == "long":
            self.glitch_x = random.uniform(-3.5, 3.5)
            self.glitch_y = random.uniform(-3.5, 3.5)
        elif self.mood == "shocked":
            self.glitch_x = random.uniform(-2.0, 2.0)
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
        if not self.roaming_enabled or self.current_message:
            return
        target_x = random.randint(150, max(200, self.screen_w - 500))
        target_y = random.randint(120, max(200, self.screen_h - 340))
        self.roam_to(target_x, target_y, duration=3200)

    def roam_to(self, target_x: int, target_y: int, duration: int = 1400):
        if not self.roaming_enabled:
            return
        target_x = max(20, min(target_x, self.screen_w - self.width() - 20))
        target_y = max(20, min(target_y, self.screen_h - self.height() - 20))
        self.roam_anim.stop()
        self.roam_anim.setDuration(duration)
        self.roam_anim.setStartValue(self.pos())
        self.roam_anim.setEndValue(QPoint(int(target_x), int(target_y)))
        self.roam_anim.start()

    def roam_to_zone(self, zone: str):
        if zone == "terminal":
            self.roam_to(int(self.screen_w * 0.42), self.screen_h - 330, 1100)
        elif zone == "editor":
            self.roam_to(int(self.screen_w * 0.52), int(self.screen_h * 0.30), 1200)
        elif zone == "cursor":
            cursor = QCursor.pos()
            self.roam_to(cursor.x() - 350, cursor.y() - 110, 850)
        else:
            self.roam_to(self.screen_w - 470, self.screen_h - 320, 1400)

    def show_roast(self, message: str, tier: str = "short", sin_count: int = 0, audio_path: str | None = None, category: str = ""):
        self.current_message = message
        self.current_tier = tier
        self.sin_count = sin_count

        mood, zone = CATEGORY_BEHAVIOR.get(category, ("suspicious", "corner"))
        if tier == "long":
            mood = "enraged"
        self.mood = mood

        self.roam_to_zone(zone)
        self.update()
        self.hide_timer.start(8500)

        if audio_path:
            self._play_audio_native(audio_path)

    def _play_audio_native(self, audio_path: str):
        """Plays MP3 directly through Windows Native MCI (winmm.dll) with zero external tools."""
        try:
            if sys.platform == "win32":
                mci = ctypes.windll.winmm.mciSendStringW
                mci("close bhoot_voice", None, 0, 0)
                mci(f'open "{audio_path}" type mpegvideo alias bhoot_voice', None, 0, 0)
                mci("play bhoot_voice", None, 0, 0)
                print(f"[bhoot.sh] 🔊 Playing voice: {Path(audio_path).name}")
        except Exception as e:
            print(f"[bhoot.sh] Audio error: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gx = 315 + self.glitch_x
        gy = 85 + self.bob_offset + self.glitch_y

        grad = QRadialGradient(QPointF(gx + 50, gy + 55), 75)
        if self.mood == "enraged" or self.current_tier == "long":
            grad.setColorAt(0.0, QColor(255, 20, 40, 160))
            grad.setColorAt(0.6, QColor(140, 0, 20, 80))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            accent_col = QColor(255, 55, 75)
        elif self.mood == "shocked":
            grad.setColorAt(0.0, QColor(190, 0, 255, 150))
            grad.setColorAt(0.6, QColor(90, 0, 140, 70))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            accent_col = QColor(210, 90, 255)
        else:
            grad.setColorAt(0.0, QColor(0, 255, 200, 130))
            grad.setColorAt(0.6, QColor(0, 110, 120, 60))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            accent_col = QColor(0, 240, 200)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QRectF(gx - 25, gy - 20, 150, 155))

        if self.custom_movie is not None:
            frame = self.custom_movie.currentPixmap()
            if not frame.isNull():
                painter.drawPixmap(int(gx), int(gy), 105, 105, frame)
        elif self.custom_pixmap is not None:
            painter.drawPixmap(int(gx), int(gy), 105, 105, self.custom_pixmap)
        else:
            self._draw_spooky_phantom(painter, gx, gy, accent_col)

        for i in range(3):
            wisp_angle = self.angle * 1.6 + (i * 2.1)
            wx = gx + 48 + math.cos(wisp_angle) * 58
            wy = gy + 50 + math.sin(wisp_angle * 1.3) * 38
            wisp_grad = QRadialGradient(QPointF(wx, wy), 12)
            wisp_grad.setColorAt(0.0, QColor(255, 255, 255, 230))
            wisp_grad.setColorAt(0.4, accent_col)
            wisp_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(wisp_grad))
            painter.drawEllipse(QRectF(wx - 10, wy - 10, 20, 20))

        if self.current_message:
            bubble_rect = QRectF(10, 20, 285, 170)
            painter.setBrush(QBrush(QColor(12, 12, 18, 242)))
            painter.setPen(QPen(accent_col, 2.2))
            painter.drawRoundedRect(bubble_rect, 14, 14)

            tail = QPainterPath()
            tail.moveTo(295, 95)
            tail.lineTo(312, 105)
            tail.lineTo(295, 115)
            painter.fillPath(tail, QBrush(accent_col))

            painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            painter.setPen(accent_col)
            header = f"💀 BHOOT.SH [{self.lang.upper()}] | SINS:{self.sin_count} | {self.mood.upper()}"
            painter.drawText(QRectF(22, 28, 260, 18), Qt.AlignmentFlag.AlignLeft, header)

            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            painter.setPen(QColor(240, 245, 250))
            painter.drawText(
                QRectF(22, 50, 260, 130),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                self.current_message
            )

    def _draw_spooky_phantom(self, painter: QPainter, gx: float, gy: float, accent_col: QColor):
        painter.setPen(QPen(QColor(130, 140, 150, 180), 2.5, Qt.PenStyle.DashLine))
        string_path = QPainterPath()
        string_path.moveTo(gx + 50, gy + 108)
        string_path.cubicTo(
            gx + 35 + math.sin(self.angle * 1.5) * 10, gy + 135,
            gx + 65 - math.sin(self.angle * 1.5) * 10, gy + 155,
            gx + 50, gy + 175
        )
        painter.drawPath(string_path)

        shroud = QPainterPath()
        shroud.moveTo(gx + 10, gy + 50)
        shroud.cubicTo(gx + 10, gy - 5, gx + 90, gy - 5, gx + 90, gy + 50)
        shroud.lineTo(gx + 95, gy + 102)
        for step in range(4, -1, -1):
            wx = gx + 10 + (step * 21)
            wy = gy + 100 + math.sin(self.angle * 2 + step) * 7
            shroud.quadTo(wx - 10, wy + 12, wx - 21 if step > 0 else gx + 5, gy + 98)
        shroud.closeSubpath()

        body_grad = QRadialGradient(QPointF(gx + 45, gy + 35), 65)
        body_grad.setColorAt(0.0, QColor(45, 50, 62, 245))
        body_grad.setColorAt(0.7, QColor(22, 24, 32, 245))
        body_grad.setColorAt(1.0, QColor(10, 10, 15, 255))

        painter.setBrush(QBrush(body_grad))
        painter.setPen(QPen(accent_col, 2.2))
        painter.drawPath(shroud)

        left_eye_center = QPointF(gx + 34, gy + 44)
        right_eye_center = QPointF(gx + 66, gy + 44)

        painter.setBrush(QBrush(QColor(5, 5, 8)))
        painter.setPen(QPen(QColor(80, 90, 100), 1.5))
        eye_h = 22 if self.mood == "shocked" else 17
        painter.drawEllipse(left_eye_center, 11, eye_h / 2)
        painter.drawEllipse(right_eye_center, 11, eye_h / 2)

        cursor_global = QCursor.pos()
        ghost_screen_center = self.mapToGlobal(QPoint(int(gx + 50), int(gy + 44)))
        dx = cursor_global.x() - ghost_screen_center.x()
        dy = cursor_global.y() - ghost_screen_center.y()
        dist = math.hypot(dx, dy) or 1.0
        pupil_ox = (dx / dist) * 4.5
        pupil_oy = (dy / dist) * 3.5

        pupil_col = QColor(255, 30, 30) if self.mood == "enraged" else accent_col
        painter.setBrush(QBrush(pupil_col))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(left_eye_center.x() + pupil_ox, left_eye_center.y() + pupil_oy), 4.5, 4.5)
        painter.drawEllipse(QPointF(right_eye_center.x() + pupil_ox, right_eye_center.y() + pupil_oy), 4.5, 4.5)

        brow_pen = QPen(accent_col, 3.0)
        painter.setPen(brow_pen)
        if self.mood == "enraged":
            painter.drawLine(QPointF(gx + 22, gy + 29), QPointF(gx + 44, gy + 36))
            painter.drawLine(QPointF(gx + 78, gy + 29), QPointF(gx + 56, gy + 36))
        elif self.mood == "mocking":
            painter.drawLine(QPointF(gx + 22, gy + 34), QPointF(gx + 44, gy + 32))
            painter.drawLine(QPointF(gx + 56, gy + 35), QPointF(gx + 78, gy + 27))

        if self.mood == "shocked":
            painter.setBrush(QBrush(QColor(5, 5, 8)))
            painter.setPen(QPen(accent_col, 2))
            painter.drawEllipse(QPointF(gx + 50, gy + 74), 10, 14)
        else:
            mouth = QPainterPath()
            mouth.moveTo(gx + 24, gy + 68)
            mouth.quadTo(gx + 50, gy + 88 if self.mood == "enraged" else gy + 82, gx + 76, gy + 68)
            painter.setPen(QPen(accent_col, 2.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(mouth)

            stitch_pen = QPen(accent_col, 1.8)
            painter.setPen(stitch_pen)
            for sx in [34, 44, 56, 66]:
                painter.drawLine(QPointF(gx + sx, gy + 69), QPointF(gx + sx, gy + 79))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.roam_anim.stop()
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #0e0e14; color: #e0f0ff; border: 1px solid #00f0c8; font-family: Segoe UI; }"
            "QMenu::item:selected { background-color: #00f0c8; color: #000000; font-weight: bold; }"
        )

        lang_action = QAction(f"🌐 Language: {'Hinglish' if self.lang == 'hi' else 'English'} (Click to Switch)", self)
        lang_action.triggered.connect(self._toggle_lang)
        menu.addAction(lang_action)

        roam_action = QAction(f"👻 Stalker Roaming: {'ON' if self.roaming_enabled else 'OFF'}", self)
        roam_action.triggered.connect(self._toggle_roaming)
        menu.addAction(roam_action)

        menu.addSeparator()

        for cat, label in [
            ("stack_overflow_copy", "📋 Simulate StackOverflow Copy (Mocking -> Editor)"),
            ("deployment_error", "💥 Simulate Terminal Crash (Enraged -> Terminal)"),
            ("api_key_exposed", "🔑 Simulate API Key Leak (Shocked -> Cursor)"),
            ("terrible_git_commit", "💩 Simulate 'fix bug' Commit (Mocking -> Editor)"),
            ("distraction_tab", "📱 Simulate Reels Distraction (Suspicious -> Cursor)"),
        ]:
            act = QAction(label, self)
            act.triggered.connect(lambda checked, c=cat: self.manual_trigger.emit(c, False))
            menu.addAction(act)

        menu.addSeparator()
        llm_act = QAction("🧠 Force Live Gemma-2 AI Roast (Sentry Traced)", self)
        llm_act.triggered.connect(lambda: self.manual_trigger.emit("endless_debugging", True))
        menu.addAction(llm_act)

        menu.addSeparator()
        quit_act = QAction("❌ Exorcise Ghost (Quit)", self)
        quit_act.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_act)

        menu.exec(event.globalPos())