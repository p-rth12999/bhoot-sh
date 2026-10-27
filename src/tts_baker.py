import os
import json
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip().strip('"')
# Defaulting to Callum (N2lVS1w4EtoT3dr4eOWO) - gravelly, creepy character voice
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "N2lVS1w4EtoT3dr4eOWO").strip().strip('"')

CORE_CATEGORIES = [
    "app_launch",
    "stack_overflow_copy",
    "deployment_error",
    "api_key_exposed",
    "terrible_git_commit",
    "distraction_tab"
]

def make_dramatic(text: str) -> str:
    """Injects natural sighs, creepy pauses (...), and emphasis for ElevenLabs."""
    text = text.replace(". ", "... ")
    text = text.replace(", ", " — ")
    text = text.replace("?", "...?")
    return f"Hmm... {text}"

def bake_audio():
    if not API_KEY:
        print("[!] Missing ELEVENLABS_API_KEY in .env")
        return

    client = ElevenLabs(api_key=API_KEY)

    for lang, filename in [("hi", "scenariohindi.json"), ("en", "scenarioenglish.json")]:
        with open(BASE_DIR / filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        for cat in CORE_CATEGORIES:
            for tier in ["short", "long"]:
                lines = data.get(cat, {}).get(tier, [])
                if not lines:
                    continue
                
                raw_text = lines[0]
                dramatic_text = make_dramatic(raw_text)
                out_file = AUDIO_DIR / f"{lang}_{cat}_{tier}_0.mp3"

                print(f"[Baking Creepy Voice] {out_file.name} -> '{dramatic_text}'")
                try:
                    audio_gen = client.text_to_speech.convert(
                        voice_id=VOICE_ID,
                        output_format="mp3_44100_128",
                        text=dramatic_text,
                        model_id="eleven_multilingual_v2",
                        voice_settings=VoiceSettings(
                            stability=0.28,          # Low stability = creepy, emotional, raspy inflection
                            similarity_boost=0.85,
                            style=0.75,              # High style exaggeration
                            use_speaker_boost=True
                        )
                    )
                    with open(out_file, "wb") as f_out:
                        for chunk in audio_gen:
                            if chunk:
                                f_out.write(chunk)
                except Exception as e:
                    print(f"[Error] {out_file.name}: {e}")

    print("\n✅ Re-baked creepy voice pack in assets/audio/!")

if __name__ == "__main__":
    bake_audio()