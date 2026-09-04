# Logseq to Anki (German)

This application automatically converts Logseq journal notes with cloze deletions into Anki flashcards.

## Features
- Scans `~/Sync/logseq/journals/*.md` for notes tagged with `#card #deutsch`.
- Supports Cloze deletions using the `{{cloze translation}}` syntax.
- Automatically extracts example sentences from Logseq sub-blocks.
- **AI-Powered:** Generates natural German example sentences using Gemini AI if none are provided in Logseq.
- Prevents duplicate cards in Anki.
- Works with Anki closed - writes to the collection file directly, no AnkiConnect.
- Beautiful CLI interface with progress tracking.

## Prerequisites
1. **Anki** installed (the app does **not** need to be running - see below).
2. **Python 3.11+** installed.

### Anki must be closed
The sync writes to your `collection.anki2` file directly through the official `anki`
library, so no add-on and no running Anki is needed. The collection is an exclusively
locked database, so **quit the Anki desktop app before syncing** - otherwise the script
stops with a clear "Quit the Anki application" message and changes nothing.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your [Gemini API Key](https://aistudio.google.com/app/apikey):
   ```bash
   cp .env.example .env
   ```

## Usage
Run the sync script:
```bash
make sync
```

The collection is found automatically: `$ANKI_COLLECTION` if set, otherwise the Anki
profile in the standard data directory (on macOS
`~/Library/Application Support/Anki2/User 1/collection.anki2`). Point it somewhere else
with:
```bash
python3 -m src.main --collection "/path/to/collection.anki2"
```

## Note Format in Logseq
```markdown
- word {{cloze translation}} #card #deutsch
  - Example sentence 1.
  - Example sentence 2.
```
The application will pick up the word, the translation (as a cloze), and the example sentences. If no example sentences are found, it will generate one using AI.
