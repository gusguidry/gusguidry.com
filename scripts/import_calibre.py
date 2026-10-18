#!/usr/bin/env python3
"""
scripts/import_calibre.py
==========================
Regenerates content/library.en.md from a Calibre metadata export.

WHY THIS EXISTS
---------------
Calibre doesn't know about Library of Congress call numbers or a
"currently reading / to read" status out of the box, so this script
expects two custom Calibre columns:

  1. A TEXT column for the LC call number.
       Preferences -> Add your own columns -> "+"
       Lookup name: lcc            Column heading: LCC
       Column type: Text

  2. An ENUMERATION column for reading status.
       Lookup name: readstatus     Column heading: Read Status
       Column type: Enumeration (values: reading, to-read, read, unsorted)

Calibre has no way to auto-assign real LC call numbers -- there's no
metadata source for that. Look each one up (worldcat.org or
catalog.loc.gov are fastest) and type it into the LCC column, same way
Luke Smith does by hand for his own shelves. This script just handles
the sorting/formatting/regeneration once the data exists.

EXPORTING FROM CALIBRE
-----------------------
Run this on the machine where your Calibre library lives:

    calibredb list \\
        --fields "title,author_sort,authors,*lcc,*readstatus" \\
        --for-machine \\
        --library-path "/path/to/Your Calibre Library" \\
        > calibre_export.json

(Omit --library-path to use Calibre's default library.)

REGENERATING content/library.en.md
------------------------------------
    python3 scripts/import_calibre.py calibre_export.json content/library.en.md

This OVERWRITES the auto-generated sections but keeps everything above
the first "## Currently Reading" heading (front matter + intro
paragraphs) untouched. Physical-only books that aren't in Calibre can
be added by hand afterward in the relevant section.

AUTOMATING THIS LATER
----------------------
This script only runs where it can reach your Calibre library and this
repo -- your own machine, not a cloud sandbox. Once the manual pipeline
is confirmed working, the next step is a cron job or macOS launchd
task that runs the calibredb export, then this script, then commits
and pushes the updated file.
"""

import sys
import re
import json
from collections import defaultdict

# ---------------------------------------------------------------------------
# CONFIG -- adjust if your Calibre custom column labels differ
# ---------------------------------------------------------------------------

LCC_FIELD_CANDIDATES = ["*lcc", "lcc", "#lcc"]
STATUS_FIELD_CANDIDATES = ["*readstatus", "readstatus", "#readstatus"]

STATUS_READING = {"reading", "currently reading"}
STATUS_TO_READ = {"to-read", "to read", "unread"}

# Library of Congress top-level classes, official outline order.
# E and F are merged (both cover "History of the Americas" --
# E = general/US, F = local/other regions).
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


def first_present(record, candidates):
    for key in candidates:
        if key in record and record[key]:
            return record[key]
    return None


def call_number_key(call_number):
    if not call_number:
        return "_"
    match = re.match(r"\s*([A-Za-z]+)", call_number)
    if not match:
        return "_"
    letter = match.group(1)[0].upper()
    return LETTER_TO_KEY.get(letter, "_")


def format_author(record):
    author_sort = record.get("author_sort")
    if author_sort:
        # author_sort is already "Last, First" -- Calibre's native format
        return author_sort.split(" & ")[0].strip()
    authors = record.get("authors")
    if isinstance(authors, list) and authors:
        authors = authors[0]
    if isinstance(authors, str) and authors:
        parts = authors.split()
        if len(parts) >= 2:
            return f"{parts[-1]}, {' '.join(parts[:-1])}"
        return authors
    return "Unknown"


def format_entry(record):
    author = format_author(record)
    title = record.get("title", "Untitled")
    call_number = first_present(record, LCC_FIELD_CANDIDATES)
    if call_number:
        return f"- {author} – *{title}* ({call_number})"
    return f"- {author} – *{title}*"


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} calibre_export.json content/library.en.md")
        sys.exit(1)

    export_path, output_path = sys.argv[1], sys.argv[2]

    with open(export_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    by_class = defaultdict(list)
    reading, to_read = [], []

    for record in records:
        key = call_number_key(first_present(record, LCC_FIELD_CANDIDATES))
        entry = format_entry(record)
        by_class[key].append(entry)

        status = (first_present(record, STATUS_FIELD_CANDIDATES) or "").strip().lower()
        if status in STATUS_READING:
            reading.append(entry)
        elif status in STATUS_TO_READ:
            to_read.append(entry)

    # Preserve everything above "## Currently Reading" (front matter + intro
    # paragraphs), then rebuild everything from there down.
    preamble = ""
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            existing = f.read()
        idx = existing.find("## Currently Reading")
        if idx != -1:
            preamble = existing[:idx]
    except FileNotFoundError:
        pass

    lines = []

    lines.append("## Currently Reading\n")
    lines.extend(reading if reading else ["- Author, Last – *Title* (Call Number)"])
    lines.append("")

    lines.append("## To Read\n")
    lines.extend(to_read if to_read else ["- Author, Last – *Title* (Call Number)"])
    lines.append("")

    for code, heading in CLASSES:
        lines.append(f"## {heading}\n")
        entries = sorted(by_class.get(code, []))
        lines.extend(entries if entries else ["- Author, Last – *Title* (Call Number)"])
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(preamble.rstrip("\n") + "\n\n" + "\n".join(lines))

    total = sum(len(v) for v in by_class.values())
    print(f"Wrote {total} books to {output_path} "
          f"({len(reading)} currently reading, {len(to_read)} to read).")


if __name__ == "__main__":
    main()
