import json
import os
import time
from typing import List, Dict, Optional

HISTORY_DIR = "history"
HISTORY_FILE = os.path.join(HISTORY_DIR, "meetings.json")

os.makedirs(HISTORY_DIR, exist_ok=True)


def load_all_meetings() -> List[Dict]:
    """Load all saved meeting records from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading meeting history: {e}")
        return []


def save_meeting(meeting_data: Dict) -> Dict:
    """
    Save a meeting analysis result to history.
    If meeting has no ID, generate one based on timestamp.
    """
    meetings = load_all_meetings()
    
    if "id" not in meeting_data or not meeting_data["id"]:
        meeting_data["id"] = f"mtg_{int(time.time())}"
    
    if "timestamp" not in meeting_data:
        meeting_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # Store lightweight record (excluding non-serializable objects like rag_chain)
    record = {
        "id": meeting_data["id"],
        "timestamp": meeting_data.get("timestamp", ""),
        "source": meeting_data.get("source", ""),
        "language": meeting_data.get("language", "english"),
        "title": meeting_data.get("title", "Untitled Session"),
        "summary": meeting_data.get("summary", ""),
        "action_items": meeting_data.get("action_items", ""),
        "key_decisions": meeting_data.get("key_decisions", ""),
        "open_questions": meeting_data.get("open_questions", ""),
        "transcript": meeting_data.get("transcript", ""),
        "audio_path": meeting_data.get("audio_path", ""),
        "duration_sec": meeting_data.get("duration_sec", 0),
        "timestamped_topics": meeting_data.get("timestamped_topics", ""),
    }

    # Replace existing or append
    existing_idx = next((i for i, m in enumerate(meetings) if m["id"] == record["id"]), None)
    if existing_idx is not None:
        meetings[existing_idx] = record
    else:
        meetings.insert(0, record)  # Newest first

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(meetings, f, indent=2, ensure_ascii=False)

    return record


def get_meeting_by_id(meeting_id: str) -> Optional[Dict]:
    """Retrieve a single meeting record by ID."""
    meetings = load_all_meetings()
    for m in meetings:
        if m["id"] == meeting_id:
            return m
    return None


def delete_meeting(meeting_id: str) -> bool:
    """Delete a meeting record from history."""
    meetings = load_all_meetings()
    new_meetings = [m for m in meetings if m["id"] != meeting_id]
    if len(new_meetings) < len(meetings):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(new_meetings, f, indent=2, ensure_ascii=False)
        return True
    return False
