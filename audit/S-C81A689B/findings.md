# Findings & Irregularities — Session `S-C81A689B` (2026-11-11 UTC)

**Rule applied:** nothing here changes stored data. Stored rows are dated snapshots (retrieved 2026-10-23 unless noted); live re-reads are recorded separately. Blank/null = unverified, never zero or estimated. No price, weight, karat, or policy value was inferred, averaged, or filled in.

## F-C81-01 (advisory) — Brilliant Earth BE-121H6 official URL now serves a different variant

- **Stored row:** `ext-be-121h6` / `BE-121H6`, "Classic Six-Prong Solitaire Ring in 14K Yellow Gold", style `BE121H6-14KY`, `$890(Setting Only)`, USD confirmed via site selector, retrieved `2026-10-23`. Official URL recorded: `https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/`. Evidence: `evidence/listings/be-121h6.md`; root `solitaire.html` row.
- **Live re-read (2026-11-11):** that official URL now canonicalizes to/serves `https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-Gold-BE121H6-1151507/`, titled "Classic Six-Prong Solitaire Ring in **18K Yellow Gold**", `$1,090(Setting Only)`, style `BE121H6-18KY`, Metal `18K Yellow Gold`, Prong metal `14K White Gold`, Width `2.5 mm`.
- **Assessment:** variant drift on the official product URL between the two retrieval dates (14K/$890 on 2026-10-23; 18K/$1,090 on 2026-11-11). Neither value is "current"; both are dated observations. The stored row is **not** edited. The row's structured price remains as stored (dated), and the root table keeps the dated $890 display tied to its retrieval date.
- **Recommendation:** manual review — re-open both variant URLs, capture each variant's own dated evidence, and decide whether the root row should carry variant-scoped entries or remain as-is with this flag linked.
- **Sources:** live fetch 2026-11-11 (chunks 0, 4); stored evidence `evidence/listings/be-121h6.md` (retrieved 2026-10-23, chunks 0, 4, 5).

## F-C81-02 (advisory, informational only) — World Gold Council moving header moved since last stored snapshot

- **Stored root reference:** `$3,995.47 / troy oz`, retrieved `2026-10-23`, `quote_date: null` (`F-026`), chart stated `Data as of 22 October, 2026` (ICE Data Services).
- **Live re-read (2026-11-11):** page dated `10 November, 2026`; header `USD /oz - 4,059.49`; `Data as of 10 November, 2026`; `Updated weekly.` (ICE Data Services).
- **Assessment:** expected movement of a weekly moving reference; not an error in stored data. Root `index.html` continues to label `$3,995.47` as a dated snapshot. No write-back; calculator arithmetic remains conditional and labeled nominal.
- **Sources:** `https://www.gold.org/goldhub/data/gold-prices` (2026-11-11); `audit/86379ca7/live_verification_2026-10-23.md` (2026-10-23).

## F-C81-03 (informational) — FTC / NIST / GIA guidance re-confirmed

- FTC `consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry` (Nov 2024): karat = parts of 24; "solid gold" means not hollow plus a karat mark; require the name/U.S. registered trademark standing behind the mark; plated/filled/overlay/vermeil/electroplate/flashed/washed definitions; written return policies; ReportFraud.ftc.gov. Consistent with `data/requirements.json` and root `index.html` checklist.
- NIST Precious Metals Conversion Information: 1 troy oz = 31.1034768 g; 24K = 99.9%, 18K = 75%, 12K = 50% gold. Consistent with calculator basis.
- GIA Gems & Gemology Summer 2025 Lab Notes "Gold-Plated Gold": XRF can read inaccurately high on gold-plated gold (same-element coating); visual microscopy essential. Consistent with repo's "on arrival"/XRF cautions.
- **No stored-data impact.**

## Open items carried from prior sessions (not re-opened, not edited)

- PR #19 (`arena/70b76800-gold2`) remains `needs review` (non-blocking), per `COORDINATION.md`; not merged or closed by this session.
- `dashboard/**` ownership belongs to prior companion-dashboard sessions; this session did not read or edit it.
- `data/flags.json` / `flags.html` ownership belongs to prior flag sessions; this session adds advisory flags `F-C81-01`/`F-C81-02` only in its own audit folder (`audit/S-C81A689B/`).

## Hallucination scan posture

- Automated PASS = stated controls passed only; not proof of source truth, purity, or future return eligibility.
- Recommended after every review: re-open official primary pages and re-run repository checks.
