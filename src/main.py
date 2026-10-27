import sys
from PyQt6.QtWidgets import QApplication
from ui_overlay import GhostOverlay
from ghost_brain import GhostBrain
from memory import SinMemory
from watcher import SystemWatcher


class BhootController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.memory = SinMemory()
        self.brain = GhostBrain(lang="hi")
        self.ui = GhostOverlay()
        self.watcher = SystemWatcher()

        self.watcher.event_detected.connect(self.handle_event)
        self.ui.manual_trigger.connect(self.handle_manual_trigger)
        self.ui.lang_changed.connect(self.handle_lang_change)

        roast, audio = self.brain.get_roast("app_launch", "short")
        self.ui.show_roast(roast, "short", 0, audio, category="app_launch")

    def handle_event(self, category: str, context: str):
        count, tier = self.memory.record_sin(category, context)
        use_llm = (count >= 4)
        roast, audio = self.brain.get_roast(category, tier, context, use_llm=use_llm)
        self.ui.show_roast(roast, tier, self.memory.get_total_sins(), audio, category=category)

    def handle_manual_trigger(self, category: str, use_llm: bool):
        count, tier = self.memory.record_sin(category, "Manual demo trigger")
        roast, audio = self.brain.get_roast(category, tier, "Demo trigger", use_llm=use_llm)
        self.ui.show_roast(roast, tier, self.memory.get_total_sins(), audio, category=category)

    def handle_lang_change(self, new_lang: str):
        self.brain.set_language(new_lang)
        msg = "Switched to English, bro. I'm still watching." if new_lang == "en" else "Wapas Hinglish mein aa gaye, developer babu!"
        self.ui.show_roast(msg, "short", self.memory.get_total_sins(), None, category="app_launch")

    def run(self):
        self.ui.show()
        self.watcher.start()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = BhootController()
    controller.run()