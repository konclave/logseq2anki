import os
import shutil
import tempfile

from anki.collection import Collection

from src.anki_client import (
    AnkiClient,
    AnkiError,
    CollectionLockedError,
    CollectionNotFoundError,
)

DECK = "Logseq::German"


def make_collection(directory: str) -> str:
    """Create an empty collection file and return its path."""
    path = os.path.join(directory, "collection.anki2")
    col = Collection(path)
    col.close()
    return path


def test_add_find_and_update():
    tmp = tempfile.mkdtemp()
    try:
        path = make_collection(tmp)
        with AnkiClient(path) as anki:
            anki.create_deck(DECK)
            fields = {"Text": "Haus {{c1::house}}", "Back Extra": ""}
            note_id = anki.add_note(DECK, "Cloze", fields, ["card", "deutsch"])
            assert isinstance(note_id, int)

            found = anki.get_notes_by_query(f'deck:"{DECK}" "Haus"')
            assert found == [note_id], found
            assert anki.check_if_exists("Haus", DECK)
            assert not anki.check_if_exists("Baum", DECK)

            info = anki.get_notes_info([note_id])[0]
            assert info["noteId"] == note_id
            assert info["modelName"] == "Cloze"
            assert info["tags"] == ["card", "deutsch"]
            assert info["fields"]["Text"]["value"] == "Haus {{c1::house}}"

            anki.update_note_fields(
                note_id, {"Text": "Haus {{c1::house}}<br><i>Das Haus ist gross.</i>"}
            )
            updated = anki.get_notes_info([note_id])[0]
            assert "<i>" in updated["fields"]["Text"]["value"]

        # Changes survive closing and reopening the collection.
        with AnkiClient(path) as anki:
            assert anki.check_if_exists("Haus", DECK)
    finally:
        shutil.rmtree(tmp)

    print("add/find/update tests passed!")


def test_duplicates_and_bad_input():
    tmp = tempfile.mkdtemp()
    try:
        path = make_collection(tmp)
        with AnkiClient(path) as anki:
            fields = {"Text": "Baum {{c1::tree}}", "Back Extra": ""}
            anki.add_note(DECK, "Cloze", fields, ["card"])

            try:
                anki.add_note(DECK, "Cloze", fields, ["card"])
                raise AssertionError("duplicate note should have been rejected")
            except AnkiError as e:
                assert "duplicate" in str(e)

            # Explicitly allowed duplicates still go through.
            assert anki.add_note(DECK, "Cloze", fields, ["card"], allow_duplicate=True)

            try:
                anki.add_note(DECK, "NoSuchModel", fields, [])
                raise AssertionError("unknown note type should have been rejected")
            except AnkiError as e:
                assert "does not exist" in str(e)

            try:
                anki.add_note(DECK, "Cloze", {"Nope": "x"}, [])
                raise AssertionError("unknown field should have been rejected")
            except AnkiError as e:
                assert "no field" in str(e)
    finally:
        shutil.rmtree(tmp)

    print("duplicate/bad input tests passed!")


def test_locked_collection():
    tmp = tempfile.mkdtemp()
    try:
        path = make_collection(tmp)
        holder = AnkiClient(path)
        holder.open()
        try:
            try:
                AnkiClient(path).open()
                raise AssertionError("second open should have been refused")
            except CollectionLockedError as e:
                assert "Quit the Anki application" in str(e)
        finally:
            holder.close()

        # Once released, the collection opens again.
        with AnkiClient(path):
            pass
    finally:
        shutil.rmtree(tmp)

    print("lock guard test passed!")


def test_missing_collection():
    tmp = tempfile.mkdtemp()
    try:
        missing = os.path.join(tmp, "nope.anki2")
        try:
            AnkiClient(missing).open()
            raise AssertionError("missing collection should have been reported")
        except CollectionNotFoundError as e:
            assert "nope.anki2" in str(e)
        # An accidental typo must not create a collection.
        assert not os.path.exists(missing)
    finally:
        shutil.rmtree(tmp)

    print("missing collection test passed!")


if __name__ == "__main__":
    test_add_find_and_update()
    test_duplicates_and_bad_input()
    test_locked_collection()
    test_missing_collection()
    print("All Anki client tests passed!")
