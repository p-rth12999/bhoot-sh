# 👻 bhoot.sh

A reincarnated, highly judgmental senior developer living on your desktop. Built for the Hacktoberfest 2026 "Ghost in the Machine" challenge, **bhoot.sh** is a frameless, transparent desktop overlay that monitors your clipboard and active windows offline, roasting your bad coding habits in Hinglish and English.

If you copy-paste from Stack Overflow, leak an API key, or push directly to `main`, this ghost will fly across your screen, stare at your cursor, and yell at you.

## Features

- **Stalker Mode & Eye-Tracking:** Glides dynamically across your screen to target specific IDE zones (e.g., flies to your terminal on a crash, or creeps up to your mouse cursor if you open Instagram).
- **Local AI Brain:** Uses `gemma2:2b` via Ollama for dynamic, offline roasts when you repeat a mistake too many times.
- **Pre-Baked ElevenLabs TTS:** Uses the native Windows MCI (`winmm.dll`) to play dramatic, raspy voice lines with zero latency and zero API calls during runtime.
- **Persistent Memory:** Logs your coding sins to a free MongoDB Atlas cluster to track your escalation from `short` warnings to `long` existential meltdowns.
- **Sentry Agent Tracing:** Wraps the Ollama inference calls in Sentry spans to monitor token latency.

## Prerequisites

1. Python 3.10+
2. [Ollama](https://ollama.com/) installed and running.
3. Pull the local model:

   ```powershell
   ollama pull gemma2:2b
   ```

## Installation

Clone the repository and set up your virtual environment in PowerShell:

```powershell
git clone https://github.com/YOUR_USERNAME/bhoot.sh.git
cd bhoot.sh
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory and add your keys. ElevenLabs and Sentry offer free tiers:

```dotenv
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=N2lVS1w4EtoT3dr4eOWO
SENTRY_DSN=your_sentry_dsn_here
MONGO_URI=your_mongodb_cluster_uri_here
OLLAMA_MODEL=gemma2:2b
```

## Running the Ghost

### Bake the Audio (Optional)

To regenerate the MP3 voice pack using your own ElevenLabs quota, run:

```powershell
python src\tts_baker.py
```

### Summon the Ghost

```powershell
python src\main.py
```

## Controls

- **Left-click and drag:** Move the ghost manually.
- **Right-click:** Open the Ghost Control Menu to switch languages, trigger demo events (API leaks, crashes), or force a live Sentry-traced Gemma 2 roast.
