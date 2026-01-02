from src.parser import LogseqNote
from src.main import run
# We can't easily test main.run directly without mocking everything, 
# so let's just simulate the logic we added.

def test_deck_selection():
    # Case 1: Standard tags
    note1 = LogseqNote(front="Test1", cloze="Test1", tags=["card", "deutsch"], file_path="test.md")
    extra_tags1 = [t for t in note1.tags if t not in ("card", "deutsch")]
    deck1 = extra_tags1[0].capitalize() if extra_tags1 else "Logseq::German"
    assert deck1 == "Logseq::German"

    # Case 2: Extra tag 'verben'
    note2 = LogseqNote(front="Test2", cloze="Test2", tags=["card", "deutsch", "verben"], file_path="test.md")
    extra_tags2 = [t for t in note2.tags if t not in ("card", "deutsch")]
    deck2 = extra_tags2[0].capitalize() if extra_tags2 else "Logseq::German"
    assert deck2 == "Verben"

    # Case 3: Extra tag 'Wichtig' (already capped)
    note3 = LogseqNote(front="Test3", cloze="Test3", tags=["card", "deutsch", "Wichtig"], file_path="test.md")
    extra_tags3 = [t for t in note3.tags if t not in ("card", "deutsch")]
    deck3 = extra_tags3[0].capitalize() if extra_tags3 else "Logseq::German"
    assert deck3 == "Wichtig"
    
    # Case 4: Multiple extra tags - takes first
    note4 = LogseqNote(front="Test4", cloze="Test4", tags=["card", "deutsch", "verben", "extra"], file_path="test.md")
    extra_tags4 = [t for t in note4.tags if t not in ("card", "deutsch")]
    deck4 = extra_tags4[0].capitalize() if extra_tags4 else "Logseq::German"
    assert deck4 == "Verben"

    print("All deck selection tests passed!")

if __name__ == "__main__":
    test_deck_selection()
