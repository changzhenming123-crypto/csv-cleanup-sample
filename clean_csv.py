#!/usr/bin/env python3
"""A small, dependency-free CSV cleanup sample. Python 3.9+."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

MAX_BYTES = 25 * 1024 * 1024


def split_columns(value):
    return [part.strip() for part in value.split(",") if part.strip()]


def clean(source, destination, required=(), unique_by=()):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if not source.is_file():
        raise ValueError("Input must be a file.")
    if source.stat().st_size > MAX_BYTES:
        raise ValueError("Sample scope: input must be at most 25 MiB.")
    if destination.exists():
        raise ValueError("Output directory already exists; choose a new directory.")

    # Read a single snapshot: the report hash describes exactly the parsed data.
    raw = source.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError("Sample scope: input must be at most 25 MiB.")
    import io
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    try:
        original_header = next(reader)
    except StopIteration:
        raise ValueError("Input is empty; a header row is required.")
    header = [name.strip() for name in original_header]
    if not header or any(not name for name in header):
        raise ValueError("Every column needs a nonempty name.")
    if len(set(header)) != len(header):
        raise ValueError("Column names must be unique after whitespace trimming.")
    if "_source_record" in header or "_reason" in header or "_raw_fields" in header:
        raise ValueError("Input uses a reserved report column name.")
    unknown = sorted((set(required) | set(unique_by)) - set(header))
    if unknown:
        raise ValueError("Unknown configured columns: " + ", ".join(unknown))
    key_indices = [header.index(name) for name in unique_by] if unique_by else list(range(len(header)))
    required_indices = [header.index(name) for name in required]
    kept, rejected, seen = [], [], set()
    report = {
        "input_file": source.name,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "columns": header,
        "required_columns": list(required),
        "unique_by": list(unique_by) or header,
        "processed": 0,
        "accepted": 0,
        "invalid": 0,
        "duplicates": 0,
        "blank_records": 0,
        "trimmed_records": 0,
    }
    for record_number, fields in enumerate(reader, start=2):
        # A blank physical line is ignored by the business count, but recorded.
        if not fields:
            report["blank_records"] += 1
            continue
        report["processed"] += 1
        values = [value.strip() for value in fields]
        if values != fields:
            report["trimmed_records"] += 1
        reason = None
        if len(values) != len(header):
            reason = "column_count: expected {}, received {}".format(len(header), len(values))
        else:
            missing = [header[i] for i in required_indices if not values[i]]
            if missing:
                reason = "missing_required: " + ", ".join(missing)
        if reason:
            report["invalid"] += 1
        else:
            key = tuple(values[i] for i in key_indices)
            if key in seen:
                reason = "duplicate"
                report["duplicates"] += 1
            else:
                seen.add(key)
                kept.append(values)
                report["accepted"] += 1
        if reason:
            # Store the original fields, including extra columns and whitespace.
            rejected.append([record_number, reason, json.dumps(fields, ensure_ascii=False)])

    assert report["processed"] == report["accepted"] + report["invalid"] + report["duplicates"]
    if not destination.parent.is_dir():
        raise ValueError("The parent of the output directory must already exist.")
    # Parse everything before making outputs; syntax errors leave no output folder.
    with tempfile.TemporaryDirectory(prefix=".csv-cleanup-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        with (staging / "clean.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(kept)
        with (staging / "rejected.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["_source_record", "_reason", "_raw_fields"])
            writer.writerows(rejected)
        (staging / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # mkdir is exclusive, so an existing output is never overwritten.
        destination.mkdir()
        for name in ("clean.csv", "rejected.csv", "summary.json"):
            os.replace(staging / name, destination / name)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 CSV input (an optional BOM is supported)")
    parser.add_argument("--out-dir", required=True, help="New output directory")
    parser.add_argument("--required", default="", help="Comma-separated columns that may not be blank")
    parser.add_argument("--unique-by", default="", help="Comma-separated duplicate key; default: every column")
    args = parser.parse_args()
    try:
        result = clean(args.input, args.out_dir, split_columns(args.required), split_columns(args.unique_by))
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 2
    print("Processed {processed}: {accepted} accepted, {invalid} invalid, {duplicates} duplicates.".format(**result))
    print("Output: {}".format(Path(args.out_dir).absolute()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
