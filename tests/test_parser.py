from src.parser import parse_logseq_file
import os

def test_parser():
    # Create a dummy file for testing
    test_file = "test_note.md"
    content = """
- vorhanden sein {{cloze в наличие (на месте)}} #card #deutsch
	- Das Hotelpersonal war überhaupt nicht vorhanden.
- Kündigen {{cloze заявление об уходе}}#card #deutsch
  card-last-interval:: 267.62
- erledigen {{cloze выполнять работу}} #card #deutsch
  - Ich muss noch viel erledigen.
  - Erledigen Sie das bitte sofort!
"""
    with open(test_file, 'w') as f:
        f.write(content)
    
    notes = parse_logseq_file(test_file)
    
    print(f"Parsed {len(notes)} notes.")
    for note in notes:
        print(f"Front: {note.front}")
        print(f"Cloze: {note.cloze}")
        print(f"Tags: {note.tags}")
        print(f"Examples: {note.examples}")
        print("-" * 20)
    
    os.remove(test_file)

if __name__ == "__main__":
    test_parser()
