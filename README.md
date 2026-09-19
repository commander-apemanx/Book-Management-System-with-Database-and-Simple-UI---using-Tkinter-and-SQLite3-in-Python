# Personal Library Manager

Simple desktop app for managing a small personal book library: **Title**, **Author**, and **ISBN**, stored in a portable **SQLite** database with a **Tkinter** UI.

**Author:** [commander-apemanx](https://github.com/commander-apemanx)  
**License:** [Apache License 2.0](LICENSE)

## Features

- Add, view, search, update, and delete books
- **Lookup ISBN** — fills Title/Author from [Open Library](https://openlibrary.org/) (internet required; no API key)
- Search matches only the fields you fill in (AND); empty fields are ignored
- Update can change **Title**, **Author**, and **ISBN**
- Table view with column headers (not a raw tuple list)
- Database file `mybooks.db` is created **next to the script** (easy to copy/backup)
- Confirm before delete; Title and Author are required

## Requirements

| Item | Notes |
| --- | --- |
| Python | 3.10 or newer |
| tkinter | Standard library (`python3-tk` on Debian/Ubuntu/Mint) |
| sqlite3 | Standard library |

No pip packages are required.

```bash
# Debian / Ubuntu / Mint
sudo apt install python3 python3-tk
```

## Run

```bash
python3 book_manager.py
```

The SQLite file appears beside the script:

```text
Personal-Library-Manager/
  book_manager.py
  mybooks.db          ← created on first run
```

Copy `mybooks.db` with the app to move your library to another machine.

## Operations

| Button | Action |
| --- | --- |
| View all | Show every book |
| Search | Find by Title and/or Author (partial match) |
| Add entry | Insert a new row |
| Update selected | Save edits to the selected row (including ISBN) |
| Delete selected | Remove the selected row (asks for confirmation) |
| Clear fields | Empty the form and clear selection |
| Lookup ISBN | Fetch Title/Author from Open Library for the ISBN field |
| Close | Quit (asks for confirmation) |

Lookup fills the form only; click **Add entry** or **Update selected** to write to SQLite. Not every ISBN is in Open Library.

## Project layout

| File | Role |
| --- | --- |
| `book_manager.py` | Application |
| `requirements.txt` | Notes (stdlib only) |
| `LICENSE` | Apache-2.0 |
| `NOTICE` | Attribution |
| `README.md` | This file |

The older single-file script with spaces in the filename has been replaced by `book_manager.py`.

## Disclaimer

This is a small educational / personal library tool, not a multi-user library management suite.
