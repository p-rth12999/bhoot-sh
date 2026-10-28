import os
import json
import random
from pathlib import Path
import ollama
import sentry_sdk
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
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
        self.model = os.getenv("OLLAMA_MODEL", "gemma2:2b").strip()
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

        # Match pre-baked MP3s
        exact_audio = BASE_DIR / "assets" / "audio" / f"{self.lang}_{category}_{tier}_0.mp3"
        long_audio = BASE_DIR / "assets" / "audio" / f"{self.lang}_{category}_long_0.mp3"
        short_audio = BASE_DIR / "assets" / "audio" / f"{self.lang}_{category}_short_0.mp3"

        if use_llm:
            # Few-shot dynamic Gemma 2 generation using the JSON lines as style training data!
            ai_roast = self._generate_gemma_roast(category, tier, context, lines)
            # Play the creepy long/short audio sting alongside the custom text if available
            fallback_mp3 = str(long_audio) if long_audio.exists() else (str(short_audio) if short_audio.exists() else None)
            return ai_roast, fallback_mp3

        if lines:
            if exact_audio.exists():
                return lines[0], str(exact_audio)
            elif tier == "medium" and long_audio.exists():
                # Use medium text or long audio
                return random.choice(lines), str(short_audio) if short_audio.exists() else None
            elif short_audio.exists():
                return lines[0], str(short_audio)
            return random.choice(lines), None

        return self._generate_gemma_roast(category, tier, context, lines), None

    def _generate_gemma_roast(self, category: str, tier: str, context: str, examples: list) -> str:
        with sentry_sdk.start_span(op="ai.inference", description=f"gemma_roast_{category}") as span:
            span.set_data("language", self.lang)
            span.set_data("severity_tier", tier)
            span.set_data("model", self.model)
            try:
                style = (
                    "menacing, sarcastic Romanized Hinglish (mix Hindi & English naturally, use phrases like 'Bas kar bhai', 'Deploy karleeee')"
                    if self.lang == "hi"
                    else "menacing, sarcastic Indian-English senior developer humor"
                )
                few_shot_block = "\n".join([f"- {ex}" for ex in examples[:3]]) if examples else "- Bas kar bhai!"
                prompt = (
                    f"You are bhoot.sh, a dark, terrifying phantom of a dead senior developer haunting a coder's IDE.\n"
                    f"Trigger Event: {category} | Escalation Tier: {tier.upper()}\n"
                    f"Live User Context: '{context[:100]}'\n"
                    f"Here are examples of your exact tone and vocabulary:\n{few_shot_block}\n\n"
                    f"Write ONE new, creepy, cutting 1-2 sentence roast in {style}. Output ONLY the raw dialogue line, no quotes."
                )
                res = ollama.generate(model=self.model, prompt=prompt)
                reply = res.get("response", "").strip().strip('"').strip("'")
                return reply if reply else (examples[0] if examples else "Bas kar bhai!")
            except Exception as e:
                sentry_sdk.capture_exception(e)
                return examples[0] if examples else "Bas kar bhai, Ollama bhi dar gaya!"