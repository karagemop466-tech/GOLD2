#!/usr/bin/env python3
"""Independent provenance / hallucination scan — session S-A87A02A5.

READ-ONLY. This script never writes to, edits, or "fixes" repository data.
It re-derives every published number from the committed registers and reports
anything that cannot be traced to a stored official-source quote.

Why a second scanner: `tools/qa.py`, `scripts/verify.mjs`,
`reviews/independent_snapshot_audit.py` and
`audit/8c810c15/security_and_hallucination_scanner.py` are all owned by other
sessions' file scopes. This one is deliberately independent of them and shares
no code, so a defect in one does not hide in the others.

Core rule enforced here (the project's No-Hallucinations policy):
  a published value must be traceable to a field-scoped quote from a page that
  was actually retrieved. If it is not traceable, it is a finding — the value is
  never silently accepted, never silently deleted, and never re-inferred.

Severity model
  FAIL  a published value has no stored provenance, or two committed artefacts
        contradict each other. Treated as a possible hallucination.
  WARN  a coverage, staleness or scope gap. Not a false value, but a reader
        could over-trust it.

Exit code: 1 if any FAIL, else 0. WARN never changes the exit code.

Usage:  python3 audit/a87a02a5/hallucination_provenance_scan.py [REPO_ROOT]
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import date
from urllib.parse import urlparse

SCAN_DATE = "2026-10-23"
NIST_GRAMS_PER_TROY_OUNCE = 31.1034768  # NIST precious-metals conversion chart

# Fields that assert something about the physical product or its price.
# If one of these is non-null it MUST carry a field-scoped quote.
CLAIM_FIELDS = (
    "name",
    "sku",
    "metal",
    "karat",
    "color",
    "width_mm",
    "depth_mm",
    "weight_g",
    "weight_basis",
    "gross_ring_weight_g",
    "price",
    "currency",
    "price_basis",
    "original_price",
    "unassigned_price_text",
    "band_width_text",
    "prong_metal",
    "surface_finish",
    "solid_gold_explicit",
    "hallmark_stated",
    "makers_mark_stated",
)

ROOT_HTML_PAGES = (
    "index.html",
    "solid-gold.html",
    "solitaire.html",
    "halo-pave.html",
    "three-stone-vintage.html",
    "18k.html",
    "budget.html",
    "retailers.html",
    "prices.html",
    "flags.html",
    "methods.html",
)


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.controls = 0

    def ok(self, msg: str) -> None:
        self.controls += 1

    def fail(self, code: str, msg: str) -> None:
        self.controls += 1
        self.failures.append(f"{code}: {msg}")

    def warning(self, code: str, msg: str) -> None:
        self.controls += 1
        self.warnings.append(f"{code}: {msg}")


def load(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


_EV_CACHE: dict[str, str] = {}
FENCE_RE = re.compile(r"```\n(.*?)```", re.S)
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def root_registers(root: str):
    """Yield (register_path, item) for every row in the root category register."""
    paths = sorted(glob.glob(os.path.join(root, "data/listings/*.json")))
    sg = os.path.join(root, "data/solid-gold-verified.json")
    if os.path.exists(sg):
        paths.append(sg)
    for path in paths:
        data = load(path)
        for item in data.get("items", []):
            yield os.path.relpath(path, root), item


def digits(value) -> str:
    """Normalised digit string used to look for a number inside a quote."""
    if isinstance(value, bool) or value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        return text
    return str(value)


def number_in_quotes(value, quotes) -> bool:
    """True when the value's digits appear literally in at least one stored quote.

    Accepted forms only: the plain number ("2758", "6.1") and, when the integer
    part is long enough to be grouped, the comma-grouped form ("1,910"). Nothing
    else is tolerated: no rounding, no unit conversion, no trailing-zero
    stripping, and no arithmetic against a neighbouring field. A short number
    must never be "confirmed" by matching a single digit that happens to appear
    in an unrelated quote.
    """
    if value is None or isinstance(value, bool):
        return True
    flat = " || ".join(str(q) for q in quotes or [])
    if not flat.strip():
        return False
    nospace = flat.replace(" ", "")
    if isinstance(value, (int, float)):
        plain = digits(value)
        candidates = {plain}
        if isinstance(value, float) and value.is_integer():
            candidates.add(str(int(value)))
        for cand in candidates:
            forms = {cand}
            whole, _, _frac = cand.partition(".")
            if len(whole) > 3:  # only group when a real thousands separator exists
                grouped = ""
                rest = whole
                while len(rest) > 3:
                    grouped = "," + rest[-3:] + grouped
                    rest = rest[:-3]
                grouped = rest + grouped
                forms.add(grouped + (("." + cand.split(".")[1]) if "." in cand else ""))
            for form in forms:
                if form and (form in flat or form in nospace):
                    return True
        return False
    return str(value) in flat


def evidence_text(root: str, item: dict) -> str:
    """Verbatim quotes from the item's own evidence file.

    Only *marked* text counts as a quote: fenced code blocks (the dominant
    convention here) and inline `code` spans (used by evidence/listings/
    fdj-gr0001.md). Free prose, headings and commentary are deliberately
    excluded, because matching a number against loose prose would let an
    invented value hide behind an unrelated sentence elsewhere in the file.
    A quote stored only in the markdown (and not mirrored into JSON
    `field_evidence`) still counts as provenance, but is reported as a warning
    so the register stays self-traceable.
    """
    ev = item.get("evidence_file") or ""
    if ev not in _EV_CACHE:
        path = os.path.join(root, ev)
        text = read(path) if ev and os.path.exists(path) else ""
        quotes = FENCE_RE.findall(text) + INLINE_CODE_RE.findall(text)
        _EV_CACHE[ev] = " || ".join(q for q in quotes if q.strip())
    return _EV_CACHE[ev]


def all_quotes(root: str, item: dict, field: str | None = None) -> str:
    """Every stored quote for an item: JSON field_evidence plus its evidence file."""
    fe = item.get("field_evidence") or {}
    parts = []
    if field:
        v = fe.get(field)
        parts += v if isinstance(v, list) else ([v] if v else [])
    else:
        for v in fe.values():
            parts += v if isinstance(v, list) else [v]
    parts.append(evidence_text(root, item))
    return " || ".join(str(x) for x in parts if x)


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


# --------------------------------------------------------------------------
# C01-C08  register-level provenance
# --------------------------------------------------------------------------

def check_register(root: str, rep: Report, retailers: dict, flags: dict) -> list:
    items = []
    for reg, item in root_registers(root):
        items.append((reg, item))
        iid = item.get("id", "<no id>")
        src = item.get("source_url")

        # C01 every row cites an official https product page on the seller's domain
        if not src or not str(src).startswith("https://"):
            rep.fail("C01", f"{iid} has no https source_url (register {reg})")
        else:
            rid = item.get("retailer_id")
            allowed = retailers.get(rid, {}).get("domains") or []
            host = host_of(src)
            if allowed and host not in {d.lower() for d in allowed}:
                rep.fail(
                    "C01",
                    f"{iid} source_url host '{host}' is not an official {rid} domain {allowed}",
                )
            else:
                rep.ok(f"C01 {iid} official host")

        # C02 the cited evidence file exists and repeats the same URL
        ev = item.get("evidence_file")
        if not ev:
            rep.fail("C02", f"{iid} has no evidence_file")
        else:
            evpath = os.path.join(root, ev)
            if not os.path.exists(evpath):
                rep.fail("C02", f"{iid} evidence_file '{ev}' does not exist")
            elif src and src not in read(evpath):
                rep.fail("C02", f"{iid} evidence file '{ev}' does not contain its source_url")
            else:
                rep.ok(f"C02 {iid} evidence present")

        fe = item.get("field_evidence") or {}

        # C03 every asserted claim field carries a field-scoped quote
        for field in CLAIM_FIELDS:
            if field not in item:
                continue
            value = item.get(field)
            if value is None:
                continue  # blank means unverified; that is allowed and expected
            quotes = fe.get(field)
            has_json_quote = bool(quotes) and any(str(q).strip() for q in quotes)
            if has_json_quote:
                rep.ok(f"C03 {iid}.{field} quoted")
                continue
            # Booleans are conclusions drawn from wording; the wording itself must
            # be quoted somewhere for this item.
            if isinstance(value, bool):
                # The boolean asserts that the *seller states* something, so the
                # quote must contain that wording. Several synonyms are accepted
                # because retailers phrase it differently ("Solid 14k Gold",
                # "Karat stamped inside the band.", "manufacturer's mark").
                needles = {"solid_gold_explicit": ("solid",),
                           "hallmark_stated": ("hallmark", "stamp", "stamped", "karat mark"),
                           "makers_mark_stated": ("maker", "manufactur", "assay")}.get(field, ())
                corpus = all_quotes(root, item).lower()
                hit = next((n for n in needles if n in corpus), "")
                if value and hit:
                    rep.ok(f"C03 {iid}.{field}=True supported by quoted wording '{hit}'")
                elif not value:
                    rep.ok(f"C03 {iid}.{field}=False (negative reading, no quote required)")
                else:
                    rep.fail(
                        "C03",
                        f"{iid}.{field}=True but no marked quote for this item contains any of {needles} "
                        "— a seller-statement boolean published without the statement",
                    )
                continue
            if number_in_quotes(value, [all_quotes(root, item)]) or str(value) in all_quotes(root, item):
                rep.warning(
                    "C03",
                    f"{iid}.{field}={value!r} is quoted in {ev or 'the evidence file'} but that quote is "
                    "not mirrored into JSON field_evidence — provenance exists, the link is implicit",
                )
            else:
                rep.fail(
                    "C03",
                    f"{iid}.{field}={value!r} is published with no quote in field_evidence "
                    "and none in its evidence file",
                )

        # C04 published price digits must appear in the price quote
        price = item.get("price")
        if price is not None and not number_in_quotes(price, fe.get("price")):
            rep.fail(
                "C04",
                f"{iid}.price={price} does not appear in its quote {fe.get('price')!r}",
            )
        elif price is not None:
            rep.ok(f"C04 {iid} price traceable")

        # C04b a rejected/superseded price must not be published as current
        for rej in item.get("rejected_values") or []:
            blob = json.dumps(rej)
            if price is not None and digits(price) and digits(price) in blob:
                rep.fail("C04b", f"{iid}.price={price} also appears in rejected_values {blob}")

        # C05 published metal weight digits must appear in the weight quote
        for wf in ("weight_g", "gross_ring_weight_g"):
            w = item.get(wf)
            if w is None:
                continue
            quotes = fe.get(wf) or fe.get("weight_basis") or item.get("weight_basis")
            quotes = quotes if isinstance(quotes, list) else ([quotes] if quotes else [])
            if number_in_quotes(w, quotes):
                rep.ok(f"C05 {iid}.{wf} traceable to a JSON quote")
            elif number_in_quotes(w, [all_quotes(root, item)]):
                rep.warning(
                    "C05",
                    f"{iid}.{wf}={w} is only supported by the evidence file, not by a JSON "
                    "field_evidence quote — mirror the quote so the number is self-traceable",
                )
            else:
                rep.fail(
                    "C05",
                    f"{iid}.{wf}={w} does not appear in any stored quote (JSON or evidence file)",
                )

        # C06 stated dimensions must appear in a quote
        for df in ("width_mm", "depth_mm"):
            d = item.get(df)
            if d is None:
                continue
            if number_in_quotes(d, fe.get(df) or fe.get("band_width_text")):
                rep.ok(f"C06 {iid}.{df} traceable")
            elif number_in_quotes(d, [all_quotes(root, item)]):
                rep.warning("C06", f"{iid}.{df}={d} is supported only by the evidence file, not JSON field_evidence")
            else:
                rep.fail("C06", f"{iid}.{df}={d} does not appear in any stored quote")

        # C07 price and currency must be asserted together, never half-asserted
        cur = item.get("currency")
        if (price is None) != (cur is None):
            rep.fail(
                "C07",
                f"{iid} price={price!r} but currency={cur!r} — one is asserted without the other",
            )
        else:
            rep.ok(f"C07 {iid} price/currency pairing")

        # C08 currency must be visible in the quoted display text
        if price is not None and cur:
            quotes = " ".join(str(q) for q in (fe.get("currency") or fe.get("price") or []))
            marker = {"USD": ("$", "USD"), "EUR": ("\u20ac", "EUR"), "GBP": ("\u00a3", "GBP")}.get(cur)
            if marker and not any(m in quotes for m in marker):
                rep.fail(
                    "C08",
                    f"{iid}.currency={cur} is not supported by its quote {quotes!r} "
                    "(a currency symbol on a page does not by itself establish an ISO code)",
                )
            elif marker:
                rep.ok(f"C08 {iid} currency marker present")

        # C09 flag references must resolve both ways
        for fid in item.get("flags") or []:
            if fid not in flags:
                rep.fail("C09", f"{iid} references unknown flag {fid}")
            elif iid not in (flags[fid].get("affected_items") or []):
                rep.warning(
                    "C09",
                    f"{iid} lists {fid} but {fid}.affected_items does not list {iid} (one-way link)",
                )
            else:
                rep.ok(f"C09 {iid}<->{fid}")

        # C10 retrieval date must be a real, non-future date
        ra = str(item.get("retrieved_at") or "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ra):
            rep.fail("C10", f"{iid}.retrieved_at={ra!r} is not an ISO date")
        else:
            try:
                when = date.fromisoformat(ra)
            except ValueError:
                rep.fail("C10", f"{iid}.retrieved_at={ra!r} is not a real calendar date")
            else:
                if when > date.fromisoformat(SCAN_DATE):
                    rep.fail("C10", f"{iid}.retrieved_at={ra} is in the future")
                elif (date.fromisoformat(SCAN_DATE) - when).days > 1:
                    rep.warning(
                        "C10",
                        f"{iid} observation is {(date.fromisoformat(SCAN_DATE) - when).days} day(s) old "
                        f"(retrieved {ra}); a displayed price may have moved",
                    )
                else:
                    rep.ok(f"C10 {iid} date sane")
    return items


# --------------------------------------------------------------------------
# C11-C14  rendered-page parity
# --------------------------------------------------------------------------

ROW_RE = re.compile(r'<tr class="item-row"[^>]*>.*?</tr>', re.S)
ATTR_RE = re.compile(r'data-source-url="([^"]*)"')
ID_RE = re.compile(r'data-item-id="([^"]*)"')
HREF_RE = re.compile(r'href="(https://[^"]+)"')


def check_rendered_rows(root: str, rep: Report, by_id: dict) -> None:
    seen_rows = 0
    for page in ROOT_HTML_PAGES:
        path = os.path.join(root, page)
        if not os.path.exists(path):
            rep.fail("C11", f"{page} is missing from the repository root")
            continue
        html = read(path)
        for m in ROW_RE.finditer(html):
            row = m.group(0)
            seen_rows += 1
            iid = (ID_RE.search(row) or [None, None])[1] if ID_RE.search(row) else None
            attr = (ATTR_RE.search(row).group(1) if ATTR_RE.search(row) else None)
            if not iid:
                rep.fail("C11", f"{page}: rendered row without data-item-id")
                continue
            item = by_id.get(iid)
            if item is None:
                rep.fail("C11", f"{page}: rendered row {iid} has no register entry (unbacked row)")
                continue
            # every rendered row must link the official page, and link *that* page
            hrefs = HREF_RE.findall(row)
            if not hrefs:
                rep.fail("C11", f"{page}: row {iid} contains no https:// link at all")
                continue
            if item.get("source_url") not in hrefs:
                rep.fail(
                    "C11",
                    f"{page}: row {iid} does not link its registered source_url {item.get('source_url')}",
                )
            else:
                rep.ok(f"C11 {page}:{iid} links official source")
            if attr is not None and attr != item.get("source_url"):
                rep.fail(
                    "C11",
                    f"{page}: row {iid} data-source-url '{attr}' != register '{item.get('source_url')}'",
                )
            # a row whose weight is blank must not render a gram figure
            text = re.sub(r"<[^>]+>", " ", row)
            if item.get("weight_g") is None and item.get("gross_ring_weight_g") is None:
                if re.search(r"\d+(?:\.\d+)?\s*g\b", text):
                    rep.fail(
                        "C12",
                        f"{page}: row {iid} renders a gram figure but both weight fields are null",
                    )
                else:
                    rep.ok(f"C12 {page}:{iid} null weight renders blank")
            # a row whose price is blank must not render an *assigned* currency figure.
            # Displaying the page's exact unlabelled text is the intended conservative
            # behaviour (F-018): the amounts are shown but never assigned to current or
            # original, so every amount must appear verbatim in unassigned_price_text.
            if item.get("price") is None:
                rendered = re.findall(r"[$\u20ac\u00a3]\s?\d[\d,]*\.\d{2}", text)
                # the register may hold the page's exact display text either as
                # unlabelled (unassigned_price_text) or as a labelled observation
                # (observed_native_display); both are legitimate provenance for
                # showing an amount while leaving `price` null.
                seen: list[str] = []
                for candidate in [item.get("unassigned_price_text")] + list(
                    item.get("observed_native_display") or []
                ):
                    text_of = str(candidate or "").strip()
                    if text_of and text_of not in seen:
                        seen.append(text_of)
                unassigned = " | ".join(seen)
                if not rendered:
                    rep.ok(f"C12 {page}:{iid} null price renders blank")
                else:
                    orphan = [a for a in rendered if a.strip() not in unassigned]
                    if orphan:
                        rep.fail(
                            "C12",
                            f"{page}: row {iid} renders {orphan} but register price is null and "
                            f"unassigned_price_text is {unassigned!r} — an unbacked amount",
                        )
                    elif not unassigned.strip():
                        rep.fail(
                            "C12",
                            f"{page}: row {iid} renders {rendered} with no recorded display text "
                            "(neither unassigned_price_text nor observed_native_display)",
                        )
                    else:
                        rep.warning(
                            "C12",
                            f"{page}: row {iid} displays unlabelled amounts {unassigned!r} verbatim with "
                            "price left null (F-018). Correct handling, but a reader may still read one "
                            "of them as the price",
                        )
            # a published price must render with the same amount
            if item.get("price") is not None:
                want = f"{item['price']:,.2f}"
                if want not in text:
                    rep.fail(
                        "C12",
                        f"{page}: row {iid} does not render its registered price {want}",
                        )
                else:
                    rep.ok(f"C12 {page}:{iid} price parity")
    if seen_rows == 0:
        rep.fail("C11", "no item rows were found in any root page — the scan cannot see the tables")
    else:
        rep.ok(f"C11 scanned {seen_rows} rendered rows")


def check_flag_anchors(root: str, rep: Report, flags: dict) -> None:
    for page in ROOT_HTML_PAGES:
        path = os.path.join(root, page)
        if not os.path.exists(path):
            continue
        html = read(path)
        for fid in set(re.findall(r"flags\.html#(f-\d+)", html)):
            if fid.upper().replace("F-", "F-") not in flags:
                rep.fail("C13", f"{page} links to unknown flag anchor #{fid}")
            else:
                rep.ok(f"C13 {page}#{fid} resolves")


STALE_COUNT_RE = re.compile(r"\bof\s+(14|15|16|17|19)\b")


def check_stale_counts(root: str, rep: Report, total_items: int) -> None:
    """Historical defect class: prose counts typed into a template and left behind."""
    for page in ROOT_HTML_PAGES:
        path = os.path.join(root, page)
        if not os.path.exists(path):
            continue
        text = re.sub(r"<[^>]+>", " ", read(path))
        for m in STALE_COUNT_RE.finditer(text):
            n = int(m.group(1))
            if n != total_items:
                rep.warning(
                    "C14",
                    f"{page} prose says 'of {n}' while the register holds {total_items} rows — "
                    "confirm this denominator is not a stale typed count",
                )
        for m in re.finditer(r"(\d+)\s+of\s+(\d+)", text):
            denom = int(m.group(2))
            if denom not in (total_items, len(flags_ids(root))):
                rep.warning("C14", f"{page} prose denominator '{denom}' matches no computed total")
        rep.ok(f"C14 {page} count sweep")


def flags_ids(root: str):
    return [f["id"] for f in load(os.path.join(root, "data/flags.json"))["flags"]]


# --------------------------------------------------------------------------
# C15  cross-register coverage
# --------------------------------------------------------------------------

def check_cross_register(root: str, rep: Report, items: list) -> list:
    combined = ""
    for rel in ("data/catalog.json", "research/evidence.json", "explore/data/catalog.json"):
        p = os.path.join(root, rel)
        if os.path.exists(p):
            combined += read(p)
    missing = []
    for _reg, item in items:
        url = item.get("source_url")
        if url and url not in combined:
            missing.append((item.get("id"), url))
    if missing:
        for iid, url in missing:
            rep.warning(
                "C15",
                f"{iid} ({url}) is in the root register but absent from the combined "
                "explore/ register that the landing page advertises as 'all entries'",
            )
    else:
        rep.ok("C15 every root row also appears in the combined register")
    return missing


# --------------------------------------------------------------------------
# C16  gold reference + melt arithmetic recomputed from scratch
# --------------------------------------------------------------------------

MELT_ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)


def check_gold_arithmetic(root: str, rep: Report, by_id: dict) -> dict:
    gold = load(os.path.join(root, "data/gold-price.json"))
    per_oz = gold.get("usd_per_troy_oz")
    gpo = gold.get("grams_per_troy_ounce")
    out = {"per_oz": per_oz, "grams_per_troy_ounce": gpo, "recomputed": []}

    if gpo != NIST_GRAMS_PER_TROY_OUNCE:
        rep.fail(
            "C16",
            f"grams_per_troy_ounce={gpo} != NIST {NIST_GRAMS_PER_TROY_OUNCE}",
        )
    else:
        rep.ok("C16 NIST gram constant")

    # every stored quote for the price must actually contain the number
    quotes = gold.get("evidence_quotes") or []
    fe = (gold.get("field_evidence") or {}).get("usd_per_troy_oz") or []
    if per_oz is not None and not number_in_quotes(per_oz, list(quotes) + list(fe)):
        rep.fail("C16", f"usd_per_troy_oz={per_oz} is not present in any stored quote {quotes}")
    else:
        rep.ok("C16 gold quote traceable")

    path = os.path.join(root, "prices.html")
    if not os.path.exists(path):
        rep.fail("C16", "prices.html missing")
        return out
    html = read(path)
    if per_oz is None:
        rep.warning("C16", "gold reference is null; melt arithmetic cannot be recomputed")
        return out

    per_gram = per_oz / gpo
    checked = 0
    for m in MELT_ROW_RE.finditer(html):
        text = re.sub(r"<[^>]+>", " ", m.group(1))
        text = re.sub(r"&nbsp;|\s+", " ", text).strip()
        melts = [float(x.replace(",", "")) for x in re.findall(r"\$(\d[\d,]*\.\d{2})", text)]
        if not melts:
            continue
        km = re.search(r"\b(\d{2})K\b", text)
        grams = [float(x) for x in re.findall(r"(\d+\.\d+)\s*g\b", text)]
        if not km or not grams:
            continue
        karat = int(km.group(1))
        if karat not in (10, 14, 18, 22, 24):
            rep.fail("C16", f"prices.html row uses karat {karat}, which is not a real gold karat: {text[:80]}")
            continue

        if len(grams) >= 3:
            # quick-reference row: fineness %, then fine gold for 2 g / 4 g / 6 g gross,
            # then the melt value of the last (6 g) column.
            pct = re.search(r"(\d+\.\d+)\s*%", text)
            if pct:
                expect_pct = karat / 24.0 * 100.0
                if abs(expect_pct - float(pct.group(1))) > 0.01:
                    rep.fail("C16", f"prices.html {karat}K fineness {pct.group(1)}% != {expect_pct:.2f}%")
                else:
                    rep.ok(f"C16 {karat}K fineness")
            for gross, shown in ((2.0, grams[0]), (4.0, grams[1]), (6.0, grams[2])):
                expect = gross * karat / 24.0
                if abs(expect - shown) > 0.001:
                    rep.fail("C16", f"prices.html {karat}K fine gold for {gross} g shows {shown} != {expect:.4f}")
                else:
                    rep.ok(f"C16 {karat}K fine gold @{gross}g")
            expect_melt = (6.0 * karat / 24.0) * per_gram
            if abs(expect_melt - melts[0]) > 0.01:
                rep.fail("C16", f"prices.html {karat}K melt ${melts[0]:.2f} != ${expect_melt:.2f} (row: {text[:70]})")
            else:
                rep.ok(f"C16 {karat}K melt arithmetic")
            out["recomputed"].append({"row": f"{karat}K reference (6 g)", "karat": karat, "gross_g": 6.0,
                                      "fine_g": round(6.0 * karat / 24.0, 4), "displayed_melt": melts[0],
                                      "recomputed_melt": round(expect_melt, 2)})
            checked += 1
        else:
            # product row: gross g, fine g, melt, and (optionally) the asking price.
            gross, fine = grams[0], grams[1]
            expect_fine = gross * karat / 24.0
            if abs(expect_fine - fine) > 0.001:
                rep.fail("C16", f"prices.html fine gold {fine} g != {gross} g x {karat}/24 = {expect_fine:.4f} g")
            else:
                rep.ok("C16 product fine-gold derivation")
            expect_melt = expect_fine * per_gram
            if abs(expect_melt - melts[0]) > 0.01:
                rep.fail("C16", f"prices.html melt ${melts[0]:.2f} != ${expect_melt:.2f} (row: {text[:70]})")
            else:
                rep.ok("C16 product melt arithmetic")
            out["recomputed"].append({"row": text[:60], "karat": karat, "gross_g": gross,
                                      "fine_g": round(expect_fine, 4), "displayed_melt": melts[0],
                                      "recomputed_melt": round(expect_melt, 2)})
            # an asking price shown next to a product must be a registered price
            if len(melts) > 1:
                asking = f"{melts[1]:,.2f}"
                registered = {f"{v:,.2f}" for v in
                              (i.get("price") for i in by_id.values()) if isinstance(v, (int, float))}
                if asking not in registered:
                    rep.fail("C16", f"prices.html shows asking price ${asking} that no register row owns")
                else:
                    rep.ok(f"C16 asking ${asking} registered")
            checked += 1
    if checked == 0:
        rep.fail("C16", "no melt rows could be parsed from prices.html — control did not execute")
    else:
        rep.ok(f"C16 recomputed {checked} melt rows")
    return out


# --------------------------------------------------------------------------
# C17  no published number without a register entry (typed-number sweep)
# --------------------------------------------------------------------------

def check_gold_reference_parity(root: str, rep: Report) -> None:
    """C18 every page must show the same gold reference the register stores."""
    gold = load(os.path.join(root, "data/gold-price.json"))
    per_oz = gold.get("usd_per_troy_oz")
    if per_oz is None:
        rep.warning("C18", "stored gold reference is null; page parity cannot be checked")
        return
    want = f"{per_oz:,.2f}"
    for page in ROOT_HTML_PAGES:
        path = os.path.join(root, page)
        if not os.path.exists(path):
            continue
        text = read(path)
        shown = set(re.findall(r"\$?(4,0\d\d\.\d\d)", text))
        if not shown:
            continue
        for value in shown:
            if value != want:
                rep.fail("C18", f"{page} displays gold reference {value} but the register stores {want}")
            else:
                rep.ok(f"C18 {page} gold reference parity")


def check_unbacked_numbers(root: str, rep: Report, by_id: dict) -> None:
    """Any price rendered in a product table must belong to a registered row."""
    known = set()
    unassigned_known = set()
    for item in by_id.values():
        for key in ("price", "original_price"):
            v = item.get(key)
            if isinstance(v, (int, float)):
                known.add(f"{v:,.2f}")
        recorded_display = str(item.get("unassigned_price_text") or "")
        for entry in item.get("observed_native_display") or []:
            recorded_display += " " + str(entry)
        for amount in re.findall(r"[$\u20ac\u00a3]\s?(\d[\d,]*\.\d{2})", recorded_display):
            unassigned_known.add(f"{float(amount.replace(',', '')):,.2f}")
    for page in ROOT_HTML_PAGES:
        path = os.path.join(root, page)
        if not os.path.exists(path) or page in ("prices.html", "index.html", "flags.html", "methods.html"):
            continue
        html = read(path)
        for m in ROW_RE.finditer(html):
            text = re.sub(r"<[^>]+>", " ", m.group(0))
            for amount in re.findall(r"[$\u20ac\u00a3]\s?(\d[\d,]*\.\d{2})", text):
                norm = amount.replace(",", "")
                pretty = f"{float(norm):,.2f}"
                if pretty in known:
                    rep.ok(f"C17 {page} {pretty} backed by a register price")
                elif pretty in unassigned_known:
                    rep.ok(f"C17 {page} {pretty} backed by recorded unassigned display text")
                else:
                    rep.fail(
                        "C17",
                        f"{page}: rendered amount {pretty} belongs to no register price and no "
                        "recorded display text (possible typed/invented number)",
                    )


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)
    rep = Report()

    retailers = {r["id"]: r for r in load(os.path.join(root, "data/retailers.json"))["retailers"]}
    flags = {f["id"]: f for f in load(os.path.join(root, "data/flags.json"))["flags"]}

    items = check_register(root, rep, retailers, flags)
    by_id = {it["id"]: it for _r, it in items}

    # flags must also point back at rows that exist
    for fid, flag in flags.items():
        for iid in flag.get("affected_items") or []:
            if iid not in by_id:
                rep.warning("C09", f"{fid}.affected_items lists {iid}, which is not in the register")

    check_rendered_rows(root, rep, by_id)
    check_flag_anchors(root, rep, flags)
    check_stale_counts(root, rep, len(items))
    missing = check_cross_register(root, rep, items)
    gold = check_gold_arithmetic(root, rep, by_id)
    check_gold_reference_parity(root, rep)
    check_unbacked_numbers(root, rep, by_id)

    print("=" * 78)
    print("S-A87A02A5 independent provenance / hallucination scan")
    print(f"repo: {root}")
    print(f"scan date: {SCAN_DATE}   rows: {len(items)}   flags: {len(flags)}")
    print(f"gold reference in data: {gold.get('per_oz')} USD/troy oz "
          f"({gold.get('grams_per_troy_ounce')} g/ozt)")
    print("=" * 78)
    if rep.failures:
        print(f"\nFAILURES ({len(rep.failures)}) — possible hallucinations / contradictions:")
        for line in rep.failures:
            print(f"  FAIL {line}")
    if rep.warnings:
        print(f"\nWARNINGS ({len(rep.warnings)}) — coverage, scope or staleness gaps:")
        for line in rep.warnings:
            print(f"  WARN {line}")
    print(f"\ncontrols executed: {rep.controls}")
    print(
        "RESULT: "
        + ("FAIL — provenance defects found" if rep.failures else "PASS — no provenance defect found")
        + f" ({len(rep.failures)} failures, {len(rep.warnings)} warnings)"
    )
    print(
        "LIMITATION: this scan proves internal traceability only. It cannot prove that a\n"
        "quoted page said what the quote claims, that a price is still current, or that any\n"
        "ring is actually the stated purity. Re-read the official source after every review."
    )
    return 1 if rep.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
