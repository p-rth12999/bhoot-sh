import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from ui_overlay import GhostOverlay
from ghost_brain import GhostBrain
from memory import SinMemory
from watcher import SystemWatcher


class GemmaWorker(QThread):
    """Runs local Gemma 2 inference on a background thread so the 60FPS UI animation never freezes."""
    finished_roast = pyqtSignal(str, str, int, object, str)  # roast, tier, total_sins, audio_path, category

    def __init__(self, brain: GhostBrain, category: str, tier: str, context: str, total_sins: int):
        super().__init__()
        self.brain = brain
        self.category = category
        self.tier = tier
        self.context = context
        self.total_sins = total_sins

    def run(self):
        roast, audio = self.brain.get_roast(self.category, self.tier, self.context, use_llm=True)
        self.finished_roast.emit(roast, self.tier, self.total_sins, audio, self.category)


class BhootController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.memory = SinMemory()
        self.brain = GhostBrain(lang="hi")
        self.ui = GhostOverlay()
        self.watcher = SystemWatcher()
        self.active_workers = []

        self.watcher.event_detected.connect(self.handle_event)
        self.ui.manual_trigger.connect(self.handle_manual_trigger)
        self.ui.lang_changed.connect(self.handle_lang_change)

        roast, audio = self.brain.get_roast("app_launch", "short")
        self.ui.show_roast(roast, "short", 0, audio, category="app_launch")

    def handle_event(self, category: str, context: str):
        count, tier = self.memory.record_sin(category, context)
        use_llm = (count >= 4)
        self._dispatch_roast(category, tier, context, use_llm)

    def handle_manual_trigger(self, category: str, use_llm: bool):
        count, tier = self.memory.record_sin(category, "Manual demo trigger")
        self._dispatch_roast(category, tier, "Demo trigger", use_llm)

    def _dispatch_roast(self, category: str, tier: str, context: str, use_llm: bool):
        total_sins = self.memory.get_total_sins()
        if use_llm:
            # Show an eerie thinking indicator while Gemma generates in the background thread
            thinking_msg = (
                "Kundali khol raha hoon teri... ruk ja..."
                if self.brain.lang == "hi"
                else "Reading the sins in your codebase... wait..."
            )
            self.ui.show_roast(thinking_msg, "long", total_sins, None, category=category)

            worker = GemmaWorker(self.brain, category, tier, context, total_sins)
            worker.finished_roast.connect(self._on_worker_done)
            worker.finished.connect(lambda: self._cleanup_worker(worker))
            self.active_workers.append(worker)
            worker.start()
        else:
            roast, audio = self.brain.get_roast(category, tier, context, use_llm=False)
            self.ui.show_roast(roast, tier, total_sins, audio, category=category)

    def _on_worker_done(self, roast: str, tier: str, total_sins: int, audio: str | None, category: str):
        self.ui.show_roast(roast, tier, total_sins, audio, category=category)

    def _cleanup_worker(self, worker: QThread):
        if worker in self.active_workers:
            self.active_workers.remove(worker)

    def handle_lang_change(self, new_lang: str):
        self.brain.set_language(new_lang)
        # Play the baked app_launch audio in the newly selected language so the user immediately hears the switch!
        roast, audio = self.brain.get_roast("app_launch", "short", use_llm=False)
        prefix = "[ENGLISH - CLYDE] " if new_lang == "en" else "[HINGLISH - DANIEL] "
        self.ui.show_roast(prefix + roast, "short", self.memory.get_total_sins(), audio, category="app_launch")

    def run(self):
        self.ui.show()
        self.watcher.start()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = BhootController()
    controller.run()