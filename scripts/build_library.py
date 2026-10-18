#!/usr/bin/env python3
"""
scripts/build_library.py
=========================
Regenerates the auto-managed parts of content/library.en.md straight from
your Calibre library and your Audiobooks folder. Meant to run unattended
(cron/launchd) -- see com.gusguidry.library-sync.plist alongside this file.

WHAT IT TOUCHES
---------------
- "## Currently Reading" and "## To Read": never touched. Calibre only
  tracks a plain "have I read this" checkbox, not what's in progress or
  queued, so there's no reliable signal to auto-populate these from.
  They stay 100% hand-maintained.

- Each LC class section (A, B, C, ... Z, Unsorted): auto-managed, but only
  between these two marker lines:

      <!-- auto:begin -->
      ...generated entries...
      <!-- auto:end -->

  Anything you type AFTER "<!-- auto:end -->" and before the next "## "
  heading survives every regeneration untouched -- that's where physical
  copies and anything else not in Calibre belongs. If a section has no
  markers yet (first run), whatever's already there is treated as your
  manual content and kept below the new auto block, so nothing you've
  already typed gets deleted.

- "## Audiobooks": new section, same auto-marker convention, generated
  from ~/Audiobooks by reading each file's embedded tags (author/title)
  with ffprobe. No call numbers -- LC classification is for the print/
  ebook side of the collection.

CLASSIFICATION
---------------
Calibre has no LC call numbers for anything right now. This script tries
an Open Library lookup (openlibrary.org/isbn/{isbn}.json's
lc_classifications field) for any book with an ISBN or LCCN identifier,
caches the result (hit or miss) in data/library-lcc-cache.json so repeat
runs don't re-hit the API, and drops anything it can't classify into
"## Unsorted". Only a fraction of the library has an ISBN on file, so
Unsorted will start out large -- classify books by hand in Calibre (or
edit the Unsorted section directly) to shrink it over time; a book
already carrying its own catalog LCC lives in the *lcc custom column and
is used first if present.

USAGE
-----
    python3 scripts/build_library.py

Reads from "~/Calibre Library/metadata.db" and "~/Audiobooks" by default;
override with --calibre-db / --audiobooks-dir. Never runs `git add`,
`commit`, or `push` -- it only rewrites content/library.en.md on disk so
you can review the diff in your normal git flow.
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

AUTO_BEGIN = "<!-- auto:begin -->"
AUTO_END = "<!-- auto:end -->"

# Library of Congress top-level classes, official outline order.
# E and F are merged (both cover "History of the Americas").
# See https://www.loc.gov/catdir/cpso/lcco/
CLASSES = [
    ("A",  "A: General Works"),
    ("B",  "B: Philosophy, Psychology, Religion"),
    ("C",  "C: Auxiliary Sciences of History"),
    ("D",  "D: World History"),
    ("EF", "E-F: History of the Americas"),
    ("G",  "G: Geography, Anthropology, Recreation"),
    ("H",  "H: Social Sciences"),
    ("J",  "J: Political Science"),
    ("K",  "K: Law"),
    ("L",  "L: Education"),
    ("M",  "M: Music"),
    ("N",  "N: Fine Arts"),
    ("P",  "P: Language and Literature"),
    ("Q",  "Q: Science"),
    ("R",  "R: Medicine"),
    ("S",  "S: Agriculture"),
    ("T",  "T: Technology"),
    ("U",  "U: Military Science"),
    ("V",  "V: Naval Science"),
    ("Z",  "Z: Bibliography, Library Science, Information Resources"),
    ("_",  "Unsorted"),
]
LETTER_TO_KEY = {code: code for code, _ in CLASSES if code not in ("EF", "_")}
LETTER_TO_KEY["E"] = "EF"
LETTER_TO_KEY["F"] = "EF"
AUDIOBOOKS_HEADING = "Audiobooks"


# ---------------------------------------------------------------------------
# Calibre
# ---------------------------------------------------------------------------

def load_calibre_books(db_path):
    uri = f"file:{db_path}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Which custom column (if any) already holds an LC call number, typed
    # in by hand in Calibre. Prefer that over any looked-up value.
    lcc_table = None
    cur.execute("select id, label from custom_columns where datatype='text'")
    for row in cur.fetchall():
        if row["label"].lower() in ("lcc", "callnumber", "call_number"):
            lcc_table = f"custom_column_{row['id']}"

    books = {}
    for row in cur.execute("select id, title, author_sort from books"):
        books[row["id"]] = {
            "title": row["title"],
            "author_sort": row["author_sort"],
            "isbn": None,
            "lccn": None,
            "manual_lcc": None,
        }

    for row in cur.execute(
        "select book, type, val from identifiers where type in ('isbn', 'lccn')"
    ):
        if row["book"] in books:
            books[row["book"]][row["type"]] = row["val"]

    if lcc_table:
        for row in cur.execute(f"select book, value from {lcc_table}"):
            if row["book"] in books and row["value"]:
                books[row["book"]]["manual_lcc"] = row["value"]

    con.close()
    return list(books.values())


def format_author(author_sort):
    if not author_sort:
        return "Unknown"
    return author_sort.split(" & ")[0].strip()


# ---------------------------------------------------------------------------
# LC classification lookup (Open Library, cached)
# ---------------------------------------------------------------------------

def load_cache(cache_path):
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return {}


def save_cache(cache_path, cache):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")


def lookup_lcc(isbn, lccn, cache):
    key = f"isbn:{isbn}" if isbn else (f"lccn:{lccn}" if lccn else None)
    if key is None:
        return None
    if key in cache:
        return cache[key]  # may be None (a cached miss)

    if not isbn:
        return None  # nothing to look up without an ISBN yet

    url = f"https://openlibrary.org/isbn/{isbn}.json"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "gusguidry.com-library-sync/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        # Network hiccup, not a real "no classification on file" answer --
        # don't cache it, so the next run tries again instead of being
        # stuck with a false miss forever.
        return None

    values = data.get("lc_classifications") or []
    result = values[0].strip() if values else None
    cache[key] = result  # a real answer from Open Library, worth caching either way
    return result


def call_number_key(call_number):
    if not call_number:
        return "_"
    match = re.match(r"\s*([A-Za-z]+)", call_number)
    if not match:
        return "_"
    letter = match.group(1)[0].upper()
    return LETTER_TO_KEY.get(letter, "_")


# ---------------------------------------------------------------------------
# Audiobooks
# ---------------------------------------------------------------------------

def scan_audiobooks(folder):
    entries = []
    for path in sorted(Path(folder).glob("*.m4b")):
        try:
            out = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
                capture_output=True, text=True, timeout=30, check=True,
            )
            tags = json.loads(out.stdout).get("format", {}).get("tags", {})
        except Exception:
            tags = {}
        title = tags.get("title") or path.stem
        author_raw = tags.get("artist") or tags.get("album_artist") or "Unknown"
        author = format_author_freeform(author_raw)
        entries.append(f"- {author} – *{title}*")
    return sorted(set(entries))


def format_author_freeform(name):
    name = name.strip()
    if "," in name:
        return name  # already "Last, First"
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name


# ---------------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------------

def split_sections(text):
    """Return (preamble, {heading: body}) splitting on '## ' headings."""
    parts = re.split(r"(?m)^## (.+)$", text)
    preamble = parts[0]
    sections = {}
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections[heading] = body
    return preamble, sections


def manual_tail(body):
    """Whatever should survive regeneration for this section."""
    if body is None:
        return ""
    if AUTO_END in body:
        return body.split(AUTO_END, 1)[1].strip("\n")
    stripped = body.strip()
    if stripped in ("", "- Author, Last – *Title* (Call Number)", "- Author, Last – *Title*"):
        return ""
    return body.strip("\n")  # unmarked pre-existing content -- keep it all


def render_section(heading, auto_lines, tail):
    out = [f"## {heading}", "", AUTO_BEGIN]
    out.extend(auto_lines if auto_lines else ["*(none yet)*"])
    out.append(AUTO_END)
    if tail:
        out.append(tail)
    out.append("")
    return "\n".join(out)


def build(content_path, calibre_db, audiobooks_dir, cache_path):
    text = content_path.read_text()
    preamble, sections = split_sections(text)

    books = load_calibre_books(calibre_db)
    cache = load_cache(cache_path)

    by_class = defaultdict(list)
    unmatched = 0
    for book in books:
        lcc = book["manual_lcc"] or lookup_lcc(book["isbn"], book["lccn"], cache)
        author = format_author(book["author_sort"])
        title = book["title"]
        entry = f"- {author} – *{title}* ({lcc})" if lcc else f"- {author} – *{title}*"
        by_class[call_number_key(lcc)].append(entry)
        if not lcc:
            unmatched += 1
    save_cache(cache_path, cache)

    audiobook_entries = scan_audiobooks(audiobooks_dir)

    # Reassemble in fixed order: Currently Reading / To Read verbatim,
    # then each LC class, then Audiobooks.
    out = [preamble.rstrip("\n"), ""]

    for fixed_heading in ("Currently Reading", "To Read"):
        body = sections.get(fixed_heading, "\n- Author, Last – *Title* (Call Number)\n")
        out.append(f"## {fixed_heading}")
        out.append(body.strip("\n"))
        out.append("")

    for code, heading in CLASSES:
        entries = sorted(by_class.get(code, []))
        tail = manual_tail(sections.get(heading))
        out.append(render_section(heading, entries, tail))

    tail = manual_tail(sections.get(AUDIOBOOKS_HEADING))
    out.append(render_section(AUDIOBOOKS_HEADING, audiobook_entries, tail))

    content_path.write_text("\n".join(out).rstrip("\n") + "\n")

    total = sum(len(v) for v in by_class.values())
    print(
        f"Wrote {total} Calibre books ({unmatched} unclassified -> Unsorted) "
        f"and {len(audiobook_entries)} audiobooks to {content_path}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--calibre-db",
        default=str(Path.home() / "Calibre Library" / "metadata.db"),
    )
    parser.add_argument(
        "--audiobooks-dir",
        default=str(Path.home() / "Audiobooks"),
    )
    parser.add_argument(
        "--content",
        default=str(Path(__file__).resolve().parent.parent / "content" / "library.en.md"),
    )
    parser.add_argument(
        "--cache",
        default=str(Path(__file__).resolve().parent.parent / "data" / "library-lcc-cache.json"),
    )
    args = parser.parse_args()

    build(Path(args.content), Path(args.calibre_db), Path(args.audiobooks_dir), Path(args.cache))


if __name__ == "__main__":
    main()
