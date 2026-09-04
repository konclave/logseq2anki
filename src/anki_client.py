import os
import sys
from typing import Any, Dict, List, Optional

# anki.collection must be imported before anki.notes to avoid a circular import.
from anki.collection import Collection
from anki.errors import DBError
from anki.notes import NoteFieldsCheckResult


class AnkiError(Exception):
    """Base error for collection access problems."""


class CollectionNotFoundError(AnkiError):
    """Raised when no Anki collection file could be located."""


class CollectionLockedError(AnkiError):
    """Raised when the collection is already open, usually by the Anki desktop app."""


class CollectionClosedError(AnkiError):
    """Raised when the client is used before open() or after close()."""


def _data_dir() -> str:
    """
    Return the platform specific Anki2 data directory.

    Returns:
        Absolute path to the directory holding Anki profile folders.
    """
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Anki2")
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA") or os.path.expanduser("~/AppData/Roaming")
        return os.path.join(appdata, "Anki2")
    xdg_data = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(xdg_data, "Anki2")


def find_collection() -> str:
    """
    Locate the collection file to use when none was given explicitly.

    Honours the ANKI_COLLECTION environment variable, then falls back to
    scanning the Anki2 data directory for profile folders.

    Returns:
        Absolute path to a collection.anki2 file.

    Raises:
        CollectionNotFoundError: If no collection exists, or several profiles
            are present and none of them is the default "User 1".
    """
    override = os.getenv("ANKI_COLLECTION")
    if override:
        return os.path.expanduser(override)

    data_dir = _data_dir()
    if not os.path.isdir(data_dir):
        raise CollectionNotFoundError(
            f"No Anki data directory at {data_dir}. "
            "Pass --collection with the path to your collection.anki2 file."
        )

    profiles = {}
    for entry in sorted(os.listdir(data_dir)):
        candidate = os.path.join(data_dir, entry, "collection.anki2")
        if os.path.isfile(candidate):
            profiles[entry] = candidate

    if not profiles:
        raise CollectionNotFoundError(
            f"No collection.anki2 found under {data_dir}. "
            "Pass --collection with the path to your collection.anki2 file."
        )
    if len(profiles) == 1:
        return next(iter(profiles.values()))
    if "User 1" in profiles:
        return profiles["User 1"]

    names = ", ".join(profiles)
    raise CollectionNotFoundError(
        f"Multiple Anki profiles found ({names}). "
        "Pass --collection to choose one."
    )


class AnkiClient:
    """
    Reads and writes an Anki collection file directly, without the Anki app.

    The collection is an exclusively locked SQLite database, so Anki desktop
    must be closed while this client holds it open.
    """

    def __init__(self, collection_path: Optional[str] = None):
        self.collection_path = (
            os.path.expanduser(collection_path) if collection_path else None
        )
        self.col: Optional[Collection] = None

    def open(self) -> None:
        """
        Open the collection, resolving the default path if none was given.

        Raises:
            CollectionNotFoundError: If the collection file does not exist.
            CollectionLockedError: If Anki (or another process) holds the collection.
        """
        if self.col is not None:
            return

        if self.collection_path is None:
            self.collection_path = find_collection()

        if not os.path.isfile(self.collection_path):
            raise CollectionNotFoundError(
                f"No collection file at {self.collection_path}."
            )

        try:
            self.col = Collection(self.collection_path)
        except DBError as e:
            raise CollectionLockedError(
                f"Cannot open {self.collection_path}: {e} "
                "Quit the Anki application and try again."
            ) from e

    def close(self) -> None:
        """Close the collection and release the lock. Safe to call twice."""
        if self.col is not None:
            self.col.close()
            self.col = None

    def __enter__(self) -> "AnkiClient":
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    @property
    def _collection(self) -> Collection:
        if self.col is None:
            raise CollectionClosedError("Collection is not open. Call open() first.")
        return self.col

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: Dict[str, str],
        tags: List[str],
        allow_duplicate: bool = False,
    ) -> int:
        """
        Create a note in the given deck.

        Args:
            deck_name: Deck to add the note to; created if missing.
            model_name: Note type name, e.g. "Cloze".
            fields: Field name to value mapping.
            tags: Tags to attach to the note.
            allow_duplicate: Add even if the first field duplicates an existing note.

        Returns:
            The id of the created note.

        Raises:
            AnkiError: If the note type is unknown, a field name does not exist,
                the note is empty, or it is a duplicate.
        """
        col = self._collection
        note_type = col.models.by_name(model_name)
        if note_type is None:
            raise AnkiError(f"Note type '{model_name}' does not exist in the collection.")

        note = col.new_note(note_type)
        for name, value in fields.items():
            if name not in note:
                raise AnkiError(f"Note type '{model_name}' has no field '{name}'.")
            note[name] = value
        note.tags = list(tags)

        check = note.fields_check()
        if check == NoteFieldsCheckResult.EMPTY:
            raise AnkiError("Cannot create note because it is empty.")
        if check == NoteFieldsCheckResult.DUPLICATE and not allow_duplicate:
            raise AnkiError("Cannot create note because it is a duplicate.")

        deck_id = col.decks.id(deck_name)
        col.add_note(note, deck_id)
        return note.id

    def get_notes_by_query(self, query: str) -> List[int]:
        """
        Find note ids matching an Anki browser search query.

        Args:
            query: Search string using Anki's own query syntax.

        Returns:
            Matching note ids.
        """
        return list(self._collection.find_notes(query))

    def get_notes_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Fetch note details for the given ids.

        Args:
            note_ids: Note ids to look up.

        Returns:
            One dict per note with 'noteId', 'modelName', 'tags' and a 'fields'
            mapping of field name to {'value', 'order'}.
        """
        col = self._collection
        infos = []
        for note_id in note_ids:
            note = col.get_note(note_id)
            infos.append(
                {
                    "noteId": note.id,
                    "modelName": note.note_type()["name"],
                    "tags": list(note.tags),
                    "fields": {
                        name: {"value": value, "order": order}
                        for order, (name, value) in enumerate(note.items())
                    },
                }
            )
        return infos

    def check_if_exists(self, front_text: str, deck_name: str) -> bool:
        """
        Report whether a note containing the given text already lives in a deck.

        Args:
            front_text: Text to search for.
            deck_name: Deck to restrict the search to.

        Returns:
            True if at least one note matches.
        """
        escaped_text = front_text.replace('"', '\\"')
        query = f'deck:"{deck_name}" "{escaped_text}"'
        return len(self.get_notes_by_query(query)) > 0

    def create_deck(self, deck_name: str) -> int:
        """
        Create a deck if it does not exist.

        Args:
            deck_name: Deck name, "::" separated for sub-decks.

        Returns:
            The deck id.
        """
        return self._collection.decks.id(deck_name)

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        """
        Overwrite fields of an existing note.

        Args:
            note_id: Id of the note to update.
            fields: Field name to new value mapping; other fields are untouched.

        Raises:
            AnkiError: If a field name does not exist on the note.
        """
        col = self._collection
        note = col.get_note(note_id)
        for name, value in fields.items():
            if name not in note:
                raise AnkiError(f"Note {note_id} has no field '{name}'.")
            note[name] = value
        col.update_note(note)
