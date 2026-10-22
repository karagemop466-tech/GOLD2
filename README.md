# GOLD2 — verified gold engagement ring research

**No hallucinations. Every price, karat and width on the site was read from the retailer's own page on the stated retrieval date, and every row links to that page. If a value was not on the page it is left blank and listed on the "Flagged for Review" page — never estimated, averaged or converted.**

Live site: **https://karagemop466-tech.github.io/GOLD2/**

---

## What this is

A small, auditable research project for buying a **solid gold** engagement ring online. It collects
listings from reputable retailers, records only what their own pages actually state, and flags the
gaps that matter — because the three things that decide whether a ring is really solid gold are the
three things retailers rarely publish:

1. the words **"solid gold"** (not plated / vermeil / gold-filled / overlay / gold-tone),
2. a **karat stamp plus a maker's mark**,
3. the **gram weight**.

At the time of writing (2026-10-22) the dataset is **14 listings from 4 retailers** across five
categories. **0 of 14** listings state the words "solid gold", **0 of 14** state a hallmark or maker's
mark, and **1 of 14** publishes a gram weight. Those are the findings, not a data-entry problem.

## The site

| Page | What it holds |
|------|----------------|
| `index.html` | Dashboard: no-hallucination banner, counts, gold quote, checklist, top flags |
| `solitaire.html` | Solitaire settings |
| `halo-pave.html` | Halo & pavé settings |
| `three-stone-vintage.html` | Three-stone and vintage-style rings |
| `18k.html` | 18K / high-karat settings, incl. the only published gram weight |
| `budget.html` | 10K / lower-price complete rings |
| `retailers.html` | Return windows, exclusions, contact info, price basis per seller |
| `prices.html` | Live melt calculator + fine-gold quick reference |
| `flags.html` | **Flagged for Review** — everything unverified or irregular, with source links |
| `methods.html` | Method, source hierarchy, limitations and the latest QA audit |

## Repository layout

```
data/            machine-readable, verified facts (JSON)
  gold-price.json          one dated gold quote + limitations
  retailers.json           policies/contact, blanks where not stated
  listings/*.json          five categories, one row per listing
  flags.json               15 flags with sources and recommended actions
evidence/        the audit trail: URL + retrieval date + verbatim quotes
tools/build_site.py      renders docs/ from data/ (no invented values)
tools/qa.py              hallucination audit + link check
reports/qa-report.md     output of the last audit
docs/            the published GitHub Pages site (generated)
COORDINATION.md  shared task board for parallel sessions
```

## Run it

```bash
python3 tools/build_site.py   # regenerate docs/
python3 tools/qa.py           # audit data + built HTML
```

**Run the audit after every review pass.** It fails the build if a published number is not backed by a
verbatim quote in `evidence/`, if a source URL leaves the seller's own domain, if a rejected cached
value equals a published value, or if a blank cell has no flag explaining it.

## Source hierarchy

- **Product facts:** the retailer's own product page only — Blue Nile, Zales, VRAI, Brilliant Earth.
- **Policies:** the retailer's own return-policy page.
- **Gold price:** World Gold Council gold-spot page (market data: ICE Data Services), quoted with its date.
- **Rejected:** search-engine snippets, aggregators, blogs, coupon sites. Snippets disagreed with the
  live page three times in the first pass — each one is logged as a rejected value (F-004, F-005, F-006).

LBMA fix data is now behind an IBA licence, so the free World Gold Council quote is used instead (F-013).

## Using the shortlist safely

1. Open the row's **official listing** link and re-read the price and karat — a stale table is the most
   likely way a wrong number appears.
2. Ask the seller in writing: *is it solid gold, what is the gram weight, and what hallmark and maker's
   mark are stamped inside?* Keep the reply.
3. Prefer a **credit card** (card acceptance is not stated on any captured page — F-012).
4. Do not accept a resize before testing: Blue Nile excludes resized and custom items from returns (F-010).
5. On arrival, before wearing or resizing, have an **independent jeweller XRF-test the metal and weigh it**.
6. If the seller will not allow independent verification or a return, don't buy.

## Disclaimer

Melt value is not an appraisal and not a resale price. Prices change without notice; the retrieval date
on each row is the only date the figure is known to be valid. Nothing here is financial or legal advice.
