# Logseq to Anki (German)

This application automatically converts Logseq journal notes with cloze deletions into Anki flashcards.

## Features
- Scans `~/Sync/logseq/journals/*.md` for notes tagged with `#card #deutsch`.
- Supports Cloze deletions using the `{{cloze translation}}` syntax.
- Automatically extracts example sentences from Logseq sub-blocks.
- **AI-Powered:** Generates natural German example sentences using Gemini AI if none are provided in Logseq.
- Prevents duplicate cards in Anki.
- Beautiful CLI interface with progress tracking.

## Prerequisites
1. **Anki** must be running.
2. **AnkiConnect** add-on must be installed in Anki.
3. **Python 3.11+** installed.

### How to install AnkiConnect
AnkiConnect is required for this script to communicate with Anki.
1. Open **Anki**.
2. Go to **Tools** -> **Add-ons** in the top menu.
3. Click the **Get Add-ons...** button on the right.
4. Paste the following code into the text box: `2055492159`.
5. Click **OK** and restart Anki to complete the installation.

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
python3 -m src.main
```

## Note Format in Logseq
```markdown
- word {{cloze translation}} #card #deutsch
  - Example sentence 1.
  - Example sentence 2.
```
The application will pick up the word, the translation (as a cloze), and the example sentences. If no example sentences are found, it will generate one using AI.
