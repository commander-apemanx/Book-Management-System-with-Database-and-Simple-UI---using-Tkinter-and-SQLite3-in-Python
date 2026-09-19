#!/usr/bin/env python3
"""
Book Management System — Tkinter UI + SQLite database.

Simple local library CRUD: add, view, search, update, delete books.
Database file: mybooks.db (stored next to this script).

Copyright 2026 commander-apemanx
Licensed under the Apache License, Version 2.0
"""

from __future__ import annotations

import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Optional


def database_path() -> Path:
    """SQLite file lives beside the app so it stays portable and predictable."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent
    return base / "mybooks.db"


class BookDB:
    """Thin SQLite wrapper for the book table."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else database_path()
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT
            )
            """
        )
        self.conn.commit()

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None  # type: ignore[assignment]

    def view(self) -> list[sqlite3.Row]:
        self.cur.execute(
            "SELECT id, title, author, isbn FROM book ORDER BY id"
        )
        return list(self.cur.fetchall())

    def insert(self, title: str, author: str, isbn: str) -> None:
        self.cur.execute(
            "INSERT INTO book (title, author, isbn) VALUES (?, ?, ?)",
            (title, author, isbn),
        )
        self.conn.commit()

    def update(self, book_id: int, title: str, author: str, isbn: str) -> None:
        self.cur.execute(
            "UPDATE book SET title=?, author=?, isbn=? WHERE id=?",
            (title, author, isbn, book_id),
        )
        self.conn.commit()

    def delete(self, book_id: int) -> None:
        self.cur.execute("DELETE FROM book WHERE id=?", (book_id,))
        self.conn.commit()

    def search(self, title: str = "", author: str = "") -> list[sqlite3.Row]:
        """Match only fields the user filled in (AND). Empty fields are ignored."""
        title = title.strip()
        author = author.strip()
        clauses: list[str] = []
        params: list[str] = []
        if title:
            clauses.append("title LIKE ?")
            params.append(f"%{title}%")
        if author:
            clauses.append("author LIKE ?")
            params.append(f"%{author}%")
        if not clauses:
            return self.view()
        sql = (
            "SELECT id, title, author, isbn FROM book WHERE "
            + " AND ".join(clauses)
            + " ORDER BY id"
        )
        self.cur.execute(sql, params)
        return list(self.cur.fetchall())


class BookApp:
    """Main window: form fields, Treeview list, action buttons."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.db = BookDB()
        self.selected_id: Optional[int] = None

        self.root.title("Book Management System")
        self.root.minsize(720, 480)
        self.root.geometry("820x520")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_style()
        self._build_ui()
        self.refresh_list(self.db.view())
        self.set_status(f"Database: {self.db.path}")

    def _build_style(self) -> None:
        style = ttk.Style(self.root)
        for name in ("clam", "vista", "xpnative"):
            if name in style.theme_names():
                style.theme_use(name)
                break
        style.configure("TButton", padding=(10, 4))
        style.configure("Treeview", rowheight=24)
        style.configure("Status.TLabel", foreground="#444444")

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        # --- form ---
        form = ttk.LabelFrame(main, text="Book details", padding=8)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.isbn_var = tk.StringVar()

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.title_entry = ttk.Entry(form, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(form, text="Author").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.author_entry = ttk.Entry(form, textvariable=self.author_var)
        self.author_entry.grid(row=0, column=3, sticky="ew")

        ttk.Label(form, text="ISBN").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0))
        self.isbn_entry = ttk.Entry(form, textvariable=self.isbn_var)
        self.isbn_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(6, 0))

        # --- list + buttons ---
        body = ttk.Frame(main)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(body)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("id", "title", "author", "isbn")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("isbn", text="ISBN")
        self.tree.column("id", width=50, minwidth=40, stretch=False, anchor="center")
        self.tree.column("title", width=260, minwidth=120)
        self.tree.column("author", width=180, minwidth=100)
        self.tree.column("isbn", width=140, minwidth=80)

        yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        btns = ttk.Frame(body)
        btns.grid(row=0, column=1, sticky="ns")
        button_specs = [
            ("View all", self.view_all),
            ("Search", self.search_books),
            ("Add entry", self.add_book),
            ("Update selected", self.update_book),
            ("Delete selected", self.delete_book),
            ("Clear fields", self.clear_fields),
            ("Close", self.on_close),
        ]
        for i, (label, cmd) in enumerate(button_specs):
            ttk.Button(btns, text=label, width=16, command=cmd).grid(
                row=i, column=0, sticky="ew", pady=3
            )

        self.status_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.status_var, style="Status.TLabel").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )

    # --- helpers ---

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def clear_fields(self) -> None:
        self.title_var.set("")
        self.author_var.set("")
        self.isbn_var.set("")
        self.selected_id = None
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.set_status("Fields cleared.")

    def form_values(self) -> tuple[str, str, str]:
        return (
            self.title_var.get().strip(),
            self.author_var.get().strip(),
            self.isbn_var.get().strip(),
        )

    def require_title_author(self) -> Optional[tuple[str, str, str]]:
        title, author, isbn = self.form_values()
        if not title or not author:
            messagebox.showwarning(
                "Missing data",
                "Title and Author are required.",
                parent=self.root,
            )
            return None
        return title, author, isbn

    def refresh_list(self, rows: list[Any]) -> None:
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(row["id"], row["title"], row["author"], row["isbn"] or ""),
            )
        self.selected_id = None

    def on_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return
        self.selected_id = int(values[0])
        self.title_var.set(values[1])
        self.author_var.set(values[2])
        self.isbn_var.set(values[3])

    # --- commands ---

    def view_all(self) -> None:
        rows = self.db.view()
        self.refresh_list(rows)
        self.set_status(f"Showing all books ({len(rows)}).")

    def search_books(self) -> None:
        title, author, _isbn = self.form_values()
        if not title and not author:
            messagebox.showinfo(
                "Search",
                "Enter a Title and/or Author to search.\n"
                "Empty fields are ignored; both filled → match both (AND).",
                parent=self.root,
            )
            return
        rows = self.db.search(title=title, author=author)
        self.refresh_list(rows)
        self.set_status(f"Search found {len(rows)} book(s).")

    def add_book(self) -> None:
        values = self.require_title_author()
        if values is None:
            return
        title, author, isbn = values
        self.db.insert(title, author, isbn)
        self.refresh_list(self.db.view())
        self.clear_fields()
        self.set_status("Book added.")

    def update_book(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning(
                "No selection",
                "Select a book in the list to update.",
                parent=self.root,
            )
            return
        values = self.require_title_author()
        if values is None:
            return
        title, author, isbn = values
        self.db.update(self.selected_id, title, author, isbn)
        self.refresh_list(self.db.view())
        self.set_status(f"Updated book id={self.selected_id}.")
        self.selected_id = None

    def delete_book(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning(
                "No selection",
                "Select a book in the list to delete.",
                parent=self.root,
            )
            return
        title = self.title_var.get().strip() or f"id={self.selected_id}"
        if not messagebox.askyesno(
            "Confirm delete",
            f"Delete this book?\n\n{title}",
            parent=self.root,
        ):
            return
        book_id = self.selected_id
        self.db.delete(book_id)
        self.refresh_list(self.db.view())
        self.clear_fields()
        self.set_status(f"Deleted book id={book_id}.")

    def on_close(self) -> None:
        if messagebox.askokcancel("Quit", "Do you want to quit?", parent=self.root):
            self.db.close()
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    BookApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
