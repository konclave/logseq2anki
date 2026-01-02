import re
import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LogseqNote:
    front: str
    cloze: str
    tags: List[str]
    examples: List[str] = field(default_factory=list)
    file_path: str = ""

def parse_logseq_file(file_path: str) -> List[LogseqNote]:
    notes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_note = None
    
    for i, line in enumerate(lines):
        # Match a card line: - text {{cloze translation}} #card #deutsch
        # We look for the hyphen, then text, then cloze, then everything else.
        card_match = re.search(r'^\s*-\s+(.*?)\{\{cloze\s+(.*?)\}\}(.*)', line)
        
        if card_match and '#card' in card_match.group(3):
            front_text = card_match.group(1).strip()
            cloze_text = card_match.group(2).strip()
            rest = card_match.group(3)
            tags = re.findall(r'#(\w+)', rest)
            
            current_note = LogseqNote(
                front=front_text,
                cloze=cloze_text,
                tags=tags,
                file_path=file_path
            )
            notes.append(current_note)
            
            # Now look for examples in subsequent lines
            j = i + 1
            indent_level = len(line) - len(line.lstrip())
            
            while j < len(lines):
                next_line = lines[j]
                if not next_line.strip():
                    j += 1
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Check if it's a property (key:: value)
                if '::' in next_line and next_indent > indent_level:
                    j += 1
                    continue
                
                # Check if it's a child (example)
                if next_indent > indent_level and next_line.lstrip().startswith('-'):
                    example = next_line.lstrip()[1:].strip()
                    if example:
                        current_note.examples.append(example)
                    j += 1
                else:
                    # Not an example or property of this note
                    break
        
    return notes

def scan_journals(directory: str) -> List[LogseqNote]:
    all_notes = []
    expanded_path = os.path.expanduser(directory)
    if not os.path.exists(expanded_path):
        return []
        
    for filename in os.listdir(expanded_path):
        if filename.endswith(".md"):
            file_path = os.path.join(expanded_path, filename)
            all_notes.extend(parse_logseq_file(file_path))
    return all_notes
