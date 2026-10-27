import os
import time
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class SinMemory:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.local_counts = {}
        self.collection = None
        
        if self.mongo_uri:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2500)
                self.db = self.client["bhoot_sh"]
                self.collection = self.db["coding_sins"]
                # Ping quick check
                self.client.admin.command('ping')
                print("[bhoot.sh] Connected to MongoDB Atlas (bhoot_sh.coding_sins)")
            except Exception as e:
                print(f"[bhoot.sh] MongoDB offline/unreachable, using local memory: {e}")
                self.collection = None

    def record_sin(self, category: str, context_snippet: str = "") -> tuple[int, str]:
        """Increments sin count, logs to MongoDB Atlas, and returns (count, severity_tier)."""
        self.local_counts[category] = self.local_counts.get(category, 0) + 1
        count = self.local_counts[category]

        # Escalation logic based on your JSON structure!
        if count == 1:
            tier = "short"
        elif count == 2:
            tier = "medium"
        else:
            tier = "long"

        if self.collection is not None:
            try:
                self.collection.insert_one({
                    "category": category,
                    "tier": tier,
                    "occurrence_number": count,
                    "snippet": context_snippet[:120],
                    "timestamp": datetime.utcnow()
                })
            except Exception:
                pass

        return count, tier

    def get_total_sins(self) -> int:
        return sum(self.local_counts.values())