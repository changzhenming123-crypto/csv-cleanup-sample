# Validation receipt

Executed locally on macOS with Python 3.9.6.

Nine acceptance tests passed, including real CLI execution, BOM/Unicode, quoted multiline records, malformed CSV rejection, and output/source preservation.

A separate 50,000-row smoke run accepted all 50,000 records and trimmed all 50,000 records in 0.151 seconds on this machine. This is a local measurement, not a delivery SLA.

Windows execution was not tested. No customer data was used. No customer acceptance or revenue is claimed.

```text
test_bom_unicode_commas_and_multiline_records (test_clean_csv.CleanupAcceptanceTests) ... ok
test_demo_counts_and_source_preservation (test_clean_csv.CleanupAcceptanceTests) ... ok
test_duplicate_headers_fail (test_clean_csv.CleanupAcceptanceTests) ... ok
test_existing_output_and_input_are_never_overwritten (test_clean_csv.CleanupAcceptanceTests) ... ok
test_header_only_is_valid (test_clean_csv.CleanupAcceptanceTests) ... ok
test_invalid_row_does_not_reserve_duplicate_key (test_clean_csv.CleanupAcceptanceTests) ... ok
test_missing_configured_column_rejected_without_outputs (test_clean_csv.CleanupAcceptanceTests) ... ok
test_real_cli (test_clean_csv.CleanupAcceptanceTests) ... ok
test_unterminated_quote_rejected_without_outputs (test_clean_csv.CleanupAcceptanceTests) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.090s

OK
```
