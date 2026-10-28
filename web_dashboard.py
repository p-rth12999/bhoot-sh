import os
import json
import random
from pathlib import Path
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="bhoot.sh | Live Sin Graveyard", page_icon="👻", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #08080c; color: #e0f0ff; }
</style>
""", unsafe_allow_html=True)

st.title("💀 bhoot.sh — Live Coding Sin Graveyard & Web Playground")
st.caption("The cloud telemetry dashboard & browser voice tester for the bhoot.sh local desktop wraith.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎮 Test the Ghost in Your Browser")
    lang = st.radio("Select Ghost Persona:", ["hi (Hinglish - Daniel)", "en (English - Clyde)"])
    lang_code = "hi" if lang.startswith("hi") else "en"

    scenario_file = BASE_DIR / ("scenariohindi.json" if lang_code == "hi" else "scenarioenglish.json")
    with open(scenario_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    category = st.selectbox("Trigger a Coding Sin:", [
        "stack_overflow_copy", "deployment_error", "api_key_exposed",
        "terrible_git_commit", "distraction_tab", "app_launch"
    ])
    tier = st.select_slider("Escalation Tier:", options=["short", "medium", "long"], value="long")

    if st.button("👻 Summon Roast & Voice"):
        lines = scenarios.get(category, {}).get(tier, ["Bas kar bhai!"])
        st.error(f"**☠ BHOOT.SH [{lang_code.upper()} | {tier.upper()}]:** {lines[0]}")
        
        audio_file = BASE_DIR / "assets" / "audio" / f"{lang_code}_{category}_{tier}_0.mp3"
        fallback_file = BASE_DIR / "assets" / "audio" / f"{lang_code}_{category}_short_0.mp3"
        target_audio = audio_file if audio_file.exists() else fallback_file
        if target_audio.exists():
            st.audio(str(target_audio), format="audio/mp3", autoplay=True)

with col2:
    st.subheader("🪦 Live Telemetry from Desktop Agent (MongoDB Atlas)")
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2500)
            sins = list(client["bhoot_sh"]["coding_sins"].find({}, {"_id": 0}).sort("timestamp", -1).limit(15))
            if sins:
                st.dataframe(sins, use_container_width=True)
            else:
                st.info("No sins logged yet. Run `src/main.py` locally to populate!")
        except Exception as e:
            st.warning(f"Could not load live MongoDB feed: {e}")
    else:
        st.info("Add MONGO_URI to environment variables to view live desktop sin logs.")