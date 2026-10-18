import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from clean_csv import clean


class CleanupAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input.csv"
        self.output = self.root / "result"

    def write(self, text):
        self.input.write_text(text, encoding="utf-8")

    def test_demo_counts_and_source_preservation(self):
        self.input.write_bytes((Path(__file__).parent / "examples" / "messy_contacts.csv").read_bytes())
        before = self.input.read_bytes()
        report = clean(self.input, self.output, ["id", "email"], ["id"])
        self.assertEqual({k: report[k] for k in ["processed", "accepted", "invalid", "duplicates"]},
                         {"processed": 10, "accepted": 6, "invalid": 3, "duplicates": 1})
        self.assertEqual(before, self.input.read_bytes())
        self.assertEqual(report["input_sha256"], hashlib.sha256(before).hexdigest())
        with (self.output / "clean.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([r["id"] for r in rows], ["1", "2", "3", "5", "7", "8"])
        self.assertEqual(rows[0]["name"], "Alice")
        with (self.output / "rejected.csv").open(newline="") as handle:
            rejected = list(csv.DictReader(handle))
        self.assertEqual(len(rejected), 4)
        self.assertIn("EXTRA", json.loads(rejected[2]["_raw_fields"]))

    def test_bom_unicode_commas_and_multiline_records(self):
        self.write('\ufeffid,note\n1,"北京, 上海"\n2,"first\nsecond"\n')
        report = clean(self.input, self.output, ["id"], ["id"])
        with (self.output / "clean.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(report["accepted"], 2)
        self.assertEqual(rows[0]["note"], "北京, 上海")
        self.assertEqual(rows[1]["note"], "first\nsecond")

    def test_invalid_row_does_not_reserve_duplicate_key(self):
        self.write("id,email\n1,\n1,valid@example.com\n")
        report = clean(self.input, self.output, ["email"], ["id"])
        self.assertEqual((report["accepted"], report["invalid"], report["duplicates"]), (1, 1, 0))

    def test_existing_output_and_input_are_never_overwritten(self):
        self.write("id\n1\n")
        self.output.mkdir()
        sentinel = self.output / "clean.csv"
        sentinel.write_text("keep me", encoding="utf-8")
        with self.assertRaises(ValueError):
            clean(self.input, self.output)
        self.assertEqual(sentinel.read_text(), "keep me")
        self.assertEqual(self.input.read_text(), "id\n1\n")

    def test_missing_configured_column_rejected_without_outputs(self):
        self.write("id\n1\n")
        with self.assertRaisesRegex(ValueError, "Unknown configured columns"):
            clean(self.input, self.output, ["email"])
        self.assertFalse(self.output.exists())

    def test_unterminated_quote_rejected_without_outputs(self):
        self.write('id,note\n1,"unfinished\n2,hidden\n')
        with self.assertRaises(csv.Error):
            clean(self.input, self.output)
        self.assertFalse(self.output.exists())

    def test_header_only_is_valid(self):
        self.write("id,email\n")
        report = clean(self.input, self.output)
        self.assertEqual(report["processed"], 0)
        self.assertTrue((self.output / "summary.json").is_file())

    def test_duplicate_headers_fail(self):
        self.write("id, id\n1,2\n")
        with self.assertRaisesRegex(ValueError, "unique"):
            clean(self.input, self.output)

    def test_real_cli(self):
        self.write("id,email\n1,a@example.com\n1,a@example.com\n")
        command = [sys.executable, str(Path(__file__).parent / "clean_csv.py"), str(self.input),
                   "--out-dir", str(self.output), "--required", "email", "--unique-by", "id"]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 accepted", result.stdout)
        rerun = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(rerun.returncode, 2)
        self.assertIn("already exists", rerun.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
