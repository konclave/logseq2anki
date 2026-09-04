import argparse
import os
from typing import List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from src.anki_client import AnkiClient, AnkiError
from src.llm import LLMClient
from src.parser import LogseqNote, scan_journals

load_dotenv()

console = Console()


def run(collection_path: Optional[str] = None):
    console.print(
        Panel.fit(
            "[bold blue]Logseq to Anki Sync[/bold blue]", subtitle="German Edition"
        )
    )

    journals_dir = os.path.expanduser("~/Sync/logseq/journals/")

    # 1. Scan files
    with console.status("[bold green]Scanning Logseq journals..."):
        all_notes = scan_journals(journals_dir)
        notes = [n for n in all_notes if "card" in n.tags and "deutsch" in n.tags]

    if not notes:
        console.print("[yellow]No notes found with #card #deutsch tags.[/yellow]")
        return

    console.print(f"Found [bold]{len(notes)}[/bold] notes in Logseq.")

    # 2. Initialize clients
    anki = AnkiClient(collection_path)
    llm = LLMClient()

    if not llm.is_configured:
        console.print(
            "[yellow]Warning: No LLM API keys found (GEMINI_API_KEY or OPENROUTER_API_KEY). Example generation will be skipped.[/yellow]"
        )

    # 3. Open the Anki collection
    try:
        anki.open()
    except AnkiError as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(f"Using collection [dim]{anki.collection_path}[/dim]")

    try:
        sync_notes(anki, llm, notes)
    finally:
        anki.close()


def sync_notes(anki: AnkiClient, llm: LLMClient, notes: List[LogseqNote]) -> None:
    model_name = "Cloze"  # Standard Anki Cloze model

    # Ensure deck exists
    default_deck_prefix = "Logseq::"
    default_deck_name = default_deck_prefix + "German"
    anki.create_deck(default_deck_name)
    created_decks = {default_deck_name}

    # Process notes
    new_notes_added = 0
    skipped_notes = 0

    table = Table(title="Sync Progress")
    table.add_column("Word", style="cyan")
    table.add_column("Deck", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Example", style="green")

    with Progress() as progress:
        task = progress.add_task("[cyan]Syncing to Anki...", total=len(notes))

        for note in notes:
            # Determine deck name based on extra tags
            extra_tags = [t for t in note.tags if t not in ("card", "deutsch")]
            if extra_tags:
                # Use the first extra tag as the deck name, capitalized
                target_deck = default_deck_prefix + extra_tags[0].capitalize()
            else:
                target_deck = default_deck_name

            # Ensure the target deck exists if we haven't seen it yet
            if target_deck not in created_decks:
                anki.create_deck(target_deck)
                created_decks.add(target_deck)

            # Check if exists
            escaped_text = note.front.replace('"', '\\"')
            query = f'deck:"{target_deck}" "{escaped_text}"'
            note_ids = anki.get_notes_by_query(query)
            existing_note_id = note_ids[0] if note_ids else None

            should_update = False
            if existing_note_id:
                # Check if it has an example
                try:
                    info = anki.get_notes_info([existing_note_id])[0]
                    current_text = info.get('fields', {}).get('Text', {}).get('value', "")
                    # Heuristic: check if example is already present (indicated by <i> or <br>)
                    if "<i>" in current_text or "<br>" in current_text:
                        skipped_notes += 1
                        progress.update(task, advance=1)
                        continue
                    else:
                        should_update = True
                except Exception:
                    # Fallback if info fetch fails
                    skipped_notes += 1
                    progress.update(task, advance=1)
                    continue

            # Handle missing examples
            example_text = ""
            is_generated = False
            if not note.examples:
                if llm.is_configured:
                    example_text = llm.generate_example(note.front, note.cloze)
                    is_generated = True
                else:
                    example_text = "(No example generated)"
            else:
                example_text = "\n".join(note.examples)

            # Prepare fields for Cloze model
            # Standard Cloze model usually has 'Text' and 'Back Extra'
            # We'll format it as: word {{c1::translation}} <br> examples
            fields = {
                "Text": f"{note.front} {{{{c1::{note.cloze}}}}}"
                + (f"<br><br><i>{example_text}</i>" if example_text else ""),
                "Back Extra": "",
            }

            try:
                if should_update and existing_note_id:
                    anki.update_note_fields(existing_note_id, fields)
                    status_str = "[blue]Updated[/blue]"
                else:
                    anki.add_note(target_deck, model_name, fields, note.tags)
                    new_notes_added += 1
                    status_str = "[green]Added[/green]"

                display_example = example_text
                if is_generated:
                    display_example = f"[blue][AI][/blue] {example_text}"

                # Truncate for display
                max_len = 80
                if len(display_example) > max_len:
                    display_example = display_example[:max_len] + "..."

                table.add_row(
                    note.front, target_deck, status_str, display_example
                )
            except Exception as e:
                table.add_row(note.front, target_deck, f"[red]Error: {e}[/red]", "")

            progress.update(task, advance=1)

    console.print(table)
    console.print(
        f"\n[bold green]Success![/bold green] Added {new_notes_added} new cards. Skipped {skipped_notes} duplicates."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sync Logseq journal notes into an Anki collection."
    )
    parser.add_argument(
        "--collection",
        default=None,
        help=(
            "Path to collection.anki2. Defaults to $ANKI_COLLECTION, "
            "then the Anki profile in the standard data directory."
        ),
    )
    args = parser.parse_args()
    run(args.collection)


if __name__ == "__main__":
    main()
