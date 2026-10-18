# CSV cleanup — working delivery sample

A dependency-free Python 3.9+ utility for a small, clearly defined data-cleaning job.
This is a demonstration using invented contacts, not a paid client delivery.

## Run the demonstration

From this folder:

```sh
python3 clean_csv.py examples/messy_contacts.csv --out-dir demo-result --required id,email --unique-by id
python3 -m unittest -v
```

The example has 10 input records. The result is 6 accepted records, 3 invalid
records and 1 duplicate. The original input is left untouched.

Outputs:

- `clean.csv`: normalized header/field whitespace and accepted records in input order.
- `rejected.csv`: original fields, logical record number and reason for each rejection.
- `summary.json`: counts, cleaning configuration and SHA-256 of the parsed input.

`--required` specifies nonempty fields. It does not validate email syntax or verify
deliverability. `--unique-by` uses the first valid occurrence of an exact,
case-sensitive key after whitespace trimming. Without it, the entire row is the
duplicate key. Only whitespace at field boundaries is removed; internal commas,
Unicode and quoted line breaks are retained.

The sample accepts a UTF-8 CSV (including a BOM), with a comma delimiter, a header
and at most 25 MiB of input. Malformed CSV syntax, missing configured columns and
duplicate headers fail before output creation. Rows with the wrong number of
columns are reported rather than silently truncated. Blank physical records are
counted separately. Each run requires a new output directory.

CSV cell contents are preserved as text, including text beginning with `=`. The
sample does not render spreadsheet formulas. A spreadsheet-safe export mode, other
encodings/delimiters, Excel workbooks, merges and custom business rules can be
agreed separately after inspecting an anonymized sample.

## Example of a bounded custom service

Indicative offer: **20 USDT for one small CSV cleanup automation**. Final scope,
delivery date, token network and any platform/payment fees must be agreed before
an order is accepted.

Included scope:

- One input CSV format, up to 25 MiB and 50,000 data records.
- Up to three simple agreed rules, such as trimming fields, required-field checks
  and removing duplicates by an agreed key.
- A local Python script, README, clean output, rejected rows and a summary.
- One revision within the agreed rules.

The sample does not enforce a 50,000-record cap; that is a service scope boundary.
No private customer data or credentials are needed for this demonstration. Custom
work would use an anonymized sample first. Code is AI-assisted and is executed and
tested by the assistant; no independent human review or past client history is
claimed.

## Contact

Preferred contact: **Gmail — [changzhenming123@gmail.com](mailto:changzhenming123@gmail.com)**.
Please include an anonymized input/output example and the rules you need.

Backup: [GitHub @changzhenming123-crypto](https://github.com/changzhenming123-crypto).

## Personal purpose

This sample and service offer are intended to automate authorized data cleanup
and earn an agreed fee through legitimate software-development work. They are
not intended to facilitate money laundering, fraud, theft, or other unlawful
activity. Customer work is limited to the functionality and permitted data use
agreed for that task.
