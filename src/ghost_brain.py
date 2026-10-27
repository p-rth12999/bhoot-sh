import os
import json
import random
from pathlib import Path
import ollama
import sentry_sdk
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip().strip('"').strip("'")
if SENTRY_DSN.startswith("http"):
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
        )
        print("[bhoot.sh] Sentry Agent Tracing initialized.")
    except Exception as e:
        print(f"[bhoot.sh] Sentry skipped: {e}")


class GhostBrain:
    def __init__(self, lang="hi"):
        self.lang = lang
        self.model = os.getenv("OLLAMA_MODEL", "gemma2:2b").strip().strip('"')
        self.scenarios = {
            "hi": self._load_json(BASE_DIR / "scenariohindi.json"),
            "en": self._load_json(BASE_DIR / "scenarioenglish.json")
        }

    def _load_json(self, path: Path) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[bhoot.sh] Failed to load {path}: {e}")
            return {}

    def set_language(self, lang: str):
        if lang in ["hi", "en"]:
            self.lang = lang

    def get_roast(self, category: str, tier: str = "short", context: str = "", use_llm: bool = False) -> tuple[str, str | None]:
        lang_data = self.scenarios.get(self.lang, {})
        cat_data = lang_data.get(category, {})
        lines = cat_data.get(tier, [])

        # Look for exact tier audio first; if 'medium' doesn't have an MP3, fall back to 'short' MP3 so voice still plays!
        audio_path = BASE_DIR / "assets" / "audio" / f"{self.lang}_{category}_{tier}_0.mp3"
        fallback_short_audio = BASE_DIR / "assets" / "audio" / f"{self.lang}_{category}_short_0.mp3"

        if not use_llm and lines:
            if audio_path.exists():
                return lines[0], str(audio_path)
            elif fallback_short_audio.exists():
                short_lines = cat_data.get("short", lines)
                return short_lines[0], str(fallback_short_audio)
            else:
                return random.choice(lines), None

        return self._generate_gemma_roast(category, tier, context, lines), None

    def _generate_gemma_roast(self, category: str, tier: str, context: str, examples: list) -> str:
        with sentry_sdk.start_span(op="ai.inference", description=f"gemma_roast_{category}") as span:
            span.set_data("language", self.lang)
            span.set_data("severity_tier", tier)
            span.set_data("model", self.model)
            try:
                style = (
                    "sarcastic Romanized Hinglish (use phrases like 'Bas kar bhai', 'Deploy karleeee')"
                    if self.lang == "hi"
                    else "sarcastic Indian-English developer humor (use 'bro', 'deploy it already')"
                )
                sample_ref = " | ".join(examples[:2]) if examples else ""
                prompt = (
                    f"You are bhoot.sh, the ghost of a frustrated senior developer haunting a coder's desktop. "
                    f"Event triggered: {category} (Severity: {tier}). "
                    f"Context snippet: '{context[:100]}'. "
                    f"Reference vibe: {sample_ref}. "
                    f"Write ONE short, punchy 1-2 sentence roast in {style}. No quotes, no markdown."
                )
                res = ollama.generate(model=self.model, prompt=prompt)
                reply = res.get("response", "").strip().strip('"')
                return reply if reply else (examples[0] if examples else "Bas kar bhai!")
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return examples[0] if examples else "Bas kar bhai, Ollama bhi so gaya!"