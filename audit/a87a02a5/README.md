# `audit/a87a02a5/` — independent verification pass, session S-A87A02A5 (2026-10-23)

Read-only audit of the GOLD2 register, site and deployment. This directory is this
session's **exclusive file scope**; no file outside it (and its own block in
`COORDINATION.md`) was modified. Nothing here edits another session's data, generators,
pages or workflows — where a fix belongs in a peer-owned file, it is written up as a
request with the exact values, not applied.

## Contents

| File | What it is |
|---|---|
| [`FINDINGS.md`](FINDINGS.md) | Ten flagged irregularities for review — 8 open, 2 resolved by peer sessions mid-pass. Human-readable, each with its source. |
| [`findings.json`](findings.json) | The same findings in `data/flags.json` field shape, so an integration owner can lift them into the Flagged for Review register without reshaping. |
| [`live_verification_2026-10-23.md`](live_verification_2026-10-23.md) | Line-by-line live re-verification: exact text observed on official pages today, row by row, plus an explicit list of what could **not** be re-read and why. |
| [`pages_and_build_review.md`](pages_and_build_review.md) | Site/build/deployment review: Pages API state, byte-level reproducibility, HTTP serving of all 46 pages, link integrity, all twelve pre-existing suites, calculator review. |
| [`hallucination_provenance_scan.py`](hallucination_provenance_scan.py) | Independent provenance scanner. Read-only, dependency-free, exits nonzero on any failure. |
| [`test_scan.py`](test_scan.py) | 22 mutation controls proving the scanner actually catches invented values, plus one positive control. |
| [`check_runs/`](check_runs/) | Unedited stdout/stderr of every suite run, with exit codes, and the base commit they ran against. |

## Run it

```sh
python3 audit/a87a02a5/hallucination_provenance_scan.py .   # 986 controls, exits 1 on any FAIL
python3 audit/a87a02a5/test_scan.py                         # 22/22 mutation controls
```

Both are read-only. The test suite builds throwaway fixtures under a temp directory and
never writes to the repository.

## What the scanner checks

| Code | Control |
|---|---|
| C01 | Every row cites an `https` product page whose host is in that seller's own registered `domains` |
| C02 | The cited evidence file exists and repeats the same URL |
| C03 | Every non-null claim field carries a quote — in `field_evidence`, or in marked text (fenced block or inline code span) in the evidence file |
| C04 | A published price's digits appear literally in its quote; a price also present in `rejected_values` fails |
| C05 | A published weight's digits appear literally in a stored quote |
| C06 | Stated dimensions appear literally in a stored quote |
| C07 | `price` and `currency` are asserted together, never half-asserted |
| C08 | A stated ISO currency is actually visible in the quoted display text |
| C09 | Flag references resolve in both directions (row ↔ flag) |
| C10 | `retrieved_at` is a real, non-future ISO date; stale observations warn |
| C11 | Every rendered row links its registered `source_url`, and `data-source-url` matches the register |
| C12 | A null price or weight never renders as a number; displayed-but-unassigned amounts must match recorded display text verbatim |
| C13 | Every `flags.html#f-nnn` anchor resolves to a real flag |
| C14 | Prose "N of M" denominators match a computed total (the stale-count defect class) |
| C15 | Every root row also appears in the combined `explore/` register |
| C16 | NIST gram constant, stored gold quote traceability, and every displayed fine-gold and melt figure recomputed from scratch |
| C17 | No rendered amount belongs to no register value (typed/invented number detection) |
| C18 | Every page shows the same gold reference the register stores |

## Deliberate design choices

- **Blank means unverified.** `null` is never treated as zero, as "no", or as a negative
  physical finding. A row that leaves a value blank passes; a row that fills one in without
  a quote fails.
- **Quotes, not prose.** Only marked text counts as a quote — fenced code blocks and inline
  code spans, the two conventions this repository actually uses. Free prose is excluded on
  purpose: matching a number against loose commentary would let an invented value hide
  behind an unrelated sentence elsewhere in the file.
- **Digits must appear literally.** No rounding, no unit conversion, no trailing-zero
  stripping, no arithmetic against a neighbouring field. A short number can never be
  "confirmed" by a single digit that happens to appear in an unrelated quote — an earlier
  version of this matcher had exactly that bug and was fixed after its own mutation test
  caught it.
- **Warnings are not failures.** Coverage gaps, mirroring gaps and staleness are warnings;
  they never change the exit code, because they are not false values.
- **Nothing is fixed in place.** The scanner reports; it does not rewrite data. Two of this
  session's findings were fixed by peer sessions while the pass was running, which is the
  correct division of labour under the board's scope rules.

## Limits

An automated PASS means only that the stated controls passed. This scanner proves
**internal traceability** — that every published number can be traced to a stored quote and
that the rendered pages agree with the data. It cannot prove that a quoted page said what
the quote claims, that a price is still current, that a ring is the stated purity, or that
a return will be honoured. No physical inspection, hallmark check, XRF assay or scale
verification was performed by this session.

**Look for hallucinations again after every review.**
