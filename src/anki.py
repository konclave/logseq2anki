import requests
import json
from typing import List, Dict, Any

class AnkiClient:
    def __init__(self, url: str = "http://localhost:8765"):
        self.url = url

    def invoke(self, action: str, **params) -> Any:
        response = requests.post(self.url, json={
            "action": action,
            "version": 6,
            "params": params
        })
        result = response.json()
        if len(result) != 2:
            raise Exception("response has an unexpected number of fields")
        if "error" not in result:
            raise Exception("response is missing required error field")
        if "result" not in result:
            raise Exception("response is missing required result field")
        if result["error"] is not None:
            raise Exception(result["error"])
        return result["result"]

    def add_note(self, deck_name: str, model_name: str, fields: Dict[str, str], tags: List[str]):
        return self.invoke("addNote", note={
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags,
            "options": {
                "allowDuplicate": False
            }
        })

    def get_notes_by_query(self, query: str) -> List[int]:
        return self.invoke("findNotes", query=query)

    def get_notes_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        return self.invoke("notesInfo", notes=note_ids)

    def check_if_exists(self, front_text: str, deck_name: str) -> bool:
        # Escape quotes for Anki query
        escaped_text = front_text.replace('"', '\\"')
        query = f'deck:"{deck_name}" "{escaped_text}"'
        note_ids = self.get_notes_by_query(query)
        return len(note_ids) > 0

    def create_deck(self, deck_name: str):
        return self.invoke("createDeck", deck=deck_name)

    def create_model(self, model_name: str):
        # We'll use a standard Cloze model usually, but let's check if it exists
        # Or better, create a custom one if needed.
        # For now, let's assume 'Cloze' model exists.
        pass

    def update_note_fields(self, note_id: int, fields: Dict[str, str]):
        return self.invoke("updateNoteFields", note={
            "id": note_id,
            "fields": fields
        })
