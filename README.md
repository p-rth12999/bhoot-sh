# 👻 bhoot.sh

A reincarnated, highly judgmental senior developer haunting your desktop. Built for the **Hacktoberfest 2026: Ghost in the Machine** challenge, **bhoot.sh** is a frameless, transparent desktop wraith that monitors your clipboard and active windows 100% locally—roasting your bad coding habits in **Hinglish** and **English**.

If you copy-paste from Stack Overflow for the tenth time, accidentally copy a live API key, open Instagram Reels near a deadline, or push `"fix bug"` straight to `main`, this phantom glides across your screen, locks its glowing eyes onto your mouse cursor, dims your monitor blood-red, and yells at you.

---

## ✨ Key Features

- **Autonomous Stalker Roaming & Eye-Tracking:** Glides dynamically to specific IDE zones without blocking your active typing line—hovering along the right editor margin when you copy-paste, flying down to glare at your VS Code terminal on a crash, or creeping up beside your cursor when you open distraction tabs.
- **5-Mood Procedural Grim Wraith + Void Dimmer:** Built with 60 FPS `PyQt6` vector shaders featuring rising shadow smoke, cursor-tracking pupils, jagged fangs, and a full-screen click-through crimson vignette (`VoidDimmer`) when your sins hit the `LONG` escalation tier.
- **Poltergeist Mode (Anti-Poke Retaliation):** Spam-click the ghost 5 times in under 3 seconds (or trigger via menu) and it goes berserk—violently glitching, teleporting across your monitor to evade your cursor, flashing the red Void overlay, and firing off a fake `System32` / Git branch deletion scare.
- **Non-Blocking Local AI Brain (`Gemma 2` + `QThread`):** Uses `gemma2:2b` via **Ollama** inside an asynchronous `QThread` worker. It feeds bilingual synthetic JSON scenarios (`scenariohindi.json` and `scenarioenglish.json`) as few-shot style examples so the 60 FPS UI never freezes while generating fresh roasts.
- **Dual-Voice Offline ElevenLabs Audio Pack:** Pre-baked using **ElevenLabs** (`eleven_multilingual_v2` with low stability and high style exaggeration) using **Daniel** for Hinglish and **Clyde** for English, played natively via Windows MCI (`winmm.dll`) with zero runtime latency and zero internet dependency.
- **Persistent Sin Memory (`MongoDB Atlas`):** Tracks your recurring coding sins across `short` -> `medium` -> `long` escalation tiers in MongoDB Atlas (`bhoot_sh.coding_sins`) with an automatic offline fallback.
- **Observability (`Sentry Agent Tracing`):** Wraps local Gemma 2 inference spans in Sentry telemetry to track token latency, language tags, and severity tiers.

---

## 🛠️ System Architecture

```text
bhoot.sh/
├── assets/
│   └── audio/               # Pre-baked bilingual ElevenLabs MP3 voice packs (en_* & hi_*)
├── src/
│   ├── main.py              # Controller + Async GemmaWorker (QThread)
│   ├── ui_overlay.py        # 60FPS Grim Wraith renderer, VoidDimmer, & Poltergeist Mode
│   ├── watcher.py           # Offline clipboard, regex secret scanner, & window monitor
│   ├── ghost_brain.py       # Few-shot Gemma 2 prompt engine + Sentry Agent Tracing
│   ├── memory.py            # MongoDB Atlas sin counter & tier escalation logic
│   └── tts_baker.py         # Quota-safe ElevenLabs dual-voice generator script
├── scenariohindi.json       # Tiered Romanized Hinglish roast dataset (short/medium/long)
├── scenarioenglish.json     # Tiered Indian-English roast dataset (short/medium/long)
├── requirements.txt         # Project dependencies
└── .env                     # API keys (optional at runtime)
```

---

## 🚀 Prerequisites

1. **Python 3.10+** (Tested on Windows 11)
2. **[Ollama](https://ollama.com/)** installed and running locally.
3. Pull the local open-weight Gemma 2 model:

   ```powershell
   ollama pull gemma2:2b
   ```

---

## 📦 Installation

Clone the repository and set up your virtual environment in PowerShell:

```powershell
git clone [https://github.com/YOUR_USERNAME/bhoot.sh.git](https://github.com/YOUR_USERNAME/bhoot.sh.git)
cd bhoot.sh
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory (no quotes around values). Because the pre-baked MP3 voice packs are included in `assets/audio/`, the ghost works out-of-the-box offline, and uses these keys for MongoDB sin-logging, Sentry tracing, or re-baking voices:

```dotenv
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID_EN=2EiwWnXFnvU5JabPnv8n
ELEVENLABS_VOICE_ID_HI=onwK4e9ZLuTAKqWW03F9
SENTRY_DSN=your_sentry_dsn_url
MONGO_URI=your_mongodb_atlas_connection_string
OLLAMA_MODEL=gemma2:2b
```

---

## 🎮 Running the Ghost

### 1. Summon the Ghost (Default Offline Runtime)

```powershell
.\venv\Scripts\python.exe src\main.py
```

### 2. Re-Bake Audio Packs (Optional)

If you modify `scenariohindi.json` or `scenarioenglish.json` and want to regenerate the `.mp3` files using your own ElevenLabs free tier quota:

```powershell
.\venv\Scripts\python.exe src\tts_baker.py
```

---

## 🕹️ Controls & Demo Triggers

- **Left-Click & Drag:** Reposition the wraith anywhere on your desktop.
- **Spam Left-Click (5x rapidly):** Trigger **Poltergeist Mode**!
- **Right-Click Context Menu:**
  - 🌐 **Switch Language:** Toggle instantly between **Hinglish (Daniel)** and **English (Clyde)**.
  - 👻 **Stalker Roaming:** Toggle autonomous IDE roaming on/off.
  - 📋 / 💥 / 🔑 / 💩 / 📱 **Simulate Events:** Trigger instant demo scenarios (Stack Overflow copy, Terminal crash, API key leak, `'fix bug'` commit, Reels distraction).
  - 🧠 **Force Live Gemma-2 Few-Shot Roast:** Triggers an asynchronous `QThread` inference call traced by Sentry.
  - ⚡ **Trigger Poltergeist Mode:** Unleashes the screen-dimming teleportation scare on demand.

---

## 🔮 Architectural Trade-offs & Future Scope (Breaking the Cloud TTS Paywall)

During development, we hit an important real-world constraint that shaped `bhoot.sh`'s hybrid architecture:

1. **Why Pre-Baked Audio + Few-Shot Gemma 2?**
   A desktop agent that reacts to every clipboard copy, git commit, and terminal crash triggers dozens of times per hour. Streaming live TTS generation from cloud APIs on every single keystroke or error introduces 1.5–3s of network latency, breaks offline air-gapped privacy, and rapidly exhausts free-tier character quotas (and premium voice library paywalls). By baking core voice stings via `tts_baker.py` and using `scenariohindi.json` / `scenarioenglish.json` as few-shot context for local `gemma2:2b`, `bhoot.sh` achieves **0ms audio latency** and **zero runtime API cost**.
2. **Next Phase — 100% Local Open-Weight Neural TTS (`Kokoro-82M` / `Parler-TTS`):**
   Our immediate roadmap is replacing the pre-baked MP3 layer with an on-device, open-weight neural TTS engine running alongside Ollama. This will let `gemma2:2b` improvise 100% unscripted, context-aware roasts from your actual stack traces and synthesize the creepy voice locally on CPU/GPU—eliminating cloud TTS paywalls forever.
3. **Custom 3D / Sprite Sheet Drops:**
   `ui_overlay.py` already supports drop-in `assets/ghost.gif` or `assets/ghost.png` overrides, making it easy to swap the procedural wraith with custom Blender 3D renders or pixel-art horror sprites.