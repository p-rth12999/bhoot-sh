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

API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "2EiwWnXFnvU5JabPnv8n").strip()  # Clyde
VOICE_ID_HI = os.getenv("ELEVENLABS_VOICE_ID_HI", "onwK4e9ZLuTAKqWW03F9").strip()  # Daniel (Multilingual Hindi/Hinglish)

CORE_CATEGORIES = [
    "app_launch",
    "stack_overflow_copy",
    "deployment_error",
    "api_key_exposed",
    "terrible_git_commit",
    "distraction_tab"
]

def make_dramatic(text: str, tier: str) -> str:
    """Adds eerie pauses, sighs, and punctuation so ElevenLabs sounds emotional and menacing."""
    text = text.replace(". ", "... ")
    text = text.replace(", ", " — ")
    text = text.replace("?", "...?")
    if tier == "long":
        return f"Hmph... {text}"
    return text

def bake_audio():
    if not API_KEY:
        print("[!] Missing ELEVENLABS_API_KEY in .env")
        return

    client = ElevenLabs(api_key=API_KEY)

    configs = [
        ("hi", "scenariohindi.json", VOICE_ID_HI),
        ("en", "scenarioenglish.json", VOICE_ID_EN),
    ]

    for lang, filename, voice_id in configs:
        with open(BASE_DIR / filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        for cat in CORE_CATEGORIES:
            for tier in ["short", "long"]:
                lines = data.get(cat, {}).get(tier, [])
                if not lines:
                    continue

                dramatic_text = make_dramatic(lines[0], tier)
                out_file = AUDIO_DIR / f"{lang}_{cat}_{tier}_0.mp3"

                # Enraged 'long' lines get lower stability (more unhinged/emotional)
                stability_val = 0.25 if tier == "long" else 0.32
                style_val = 0.85 if tier == "long" else 0.70

                print(f"[Baking {lang.upper()} | Voice:{voice_id[:6]}] {out_file.name} -> '{dramatic_text}'")
                try:
                    audio_gen = client.text_to_speech.convert(
                        voice_id=voice_id,
                        output_format="mp3_44100_128",
                        text=dramatic_text,
                        model_id="eleven_multilingual_v2",
                        voice_settings=VoiceSettings(
                            stability=stability_val,
                            similarity_boost=0.85,
                            style=style_val,
                            use_speaker_boost=True
                        )
                    )
                    with open(out_file, "wb") as f_out:
                        for chunk in audio_gen:
                            if chunk:
                                f_out.write(chunk)
                except Exception as e:
                    print(f"[!] Voice {voice_id} failed ({e}). Falling back to Clyde ({VOICE_ID_EN})...")
                    try:
                        audio_gen = client.text_to_speech.convert(
                            voice_id=VOICE_ID_EN,
                            output_format="mp3_44100_128",
                            text=dramatic_text,
                            model_id="eleven_multilingual_v2",
                            voice_settings=VoiceSettings(
                                stability=stability_val,
                                similarity_boost=0.85,
                                style=style_val,
                                use_speaker_boost=True
                            )
                        )
                        with open(out_file, "wb") as f_out:
                            for chunk in audio_gen:
                                if chunk:
                                    f_out.write(chunk)
                    except Exception as e2:
                        print(f"[Error] Fallback also failed: {e2}")

    print("\n✅ Dual-voice creepy audio packs baked in assets/audio/!")

if __name__ == "__main__":
    bake_audio()