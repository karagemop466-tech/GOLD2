#!/usr/bin/env python3
"""
security_and_hallucination_scanner.py — S8C8-T3 comprehensive zero-hallucination,
HTML table official-link, CSP/XSS security, GitHub Actions SHA pinning, and
WCAG 2.1 AA contrast scanner for GOLD2.

Exits 0 only when zero findings exist across the repository snapshot.
Run after EVERY review pass and build step:
    python3 audit/8c810c15/security_and_hallucination_scanner.py .
"""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}

BLOCKED_DOMAINS = {
    "reddit.com",
    "www.reddit.com",
    "quora.com",
    "www.quora.com",
    "trustpilot.com",
    "www.trustpilot.com",
    "yelp.com",
    "www.yelp.com",
    "wikipedia.org",
    "en.wikipedia.org",
    "medium.com",
    "example.com",
    "localhost",
    "127.0.0.1",
}

EVENT_HANDLER_RE = re.compile(r"\bon(?:click|input|change|submit|load|error|mouseover|focus|keyup)\s*=", re.I)
DANGEROUS_JS_RE = re.compile(r"\b(?:innerHTML|outerHTML|insertAdjacentHTML|eval)\s*[=(]")
SHA_PIN_RE = re.compile(r"^[0-9a-f]{40}$")
SECRET_RE = re.compile(r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,})")


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def rel_luminance(hex_color: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = rel_luminance(fg), rel_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


class PageHTMLInspector(HTMLParser):
    """Inspects every data <tr>, external <a>, CSP <meta>, and inline handlers."""

    def __init__(self) -> None:
        super().__init__()
        self.has_csp = False
        self.csp_content = ""
        self.in_tr = False
        self.tr_index = 0
        self.tr_has_td = False
        self.tr_text: list[str] = []
        self.tr_https_urls: list[str] = []
        self.rows: list[dict] = []
        self.target_blank_missing_noopener: list[str] = []
        self.blocked_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta" and amap.get("http-equiv", "").lower() == "content-security-policy":
            self.has_csp = True
            self.csp_content = amap.get("content", "")
        if tag == "tr":
            self.in_tr = True
            self.tr_index += 1
            self.tr_has_td = False
            self.tr_text = []
            self.tr_https_urls = []
        elif tag == "td" and self.in_tr:
            self.tr_has_td = True
        elif tag == "a":
            href = amap.get("href", "")
            if amap.get("target") == "_blank":
                rel_tokens = set(amap.get("rel", "").lower().split())
                if "noopener" not in rel_tokens:
                    self.target_blank_missing_noopener.append(href)
            if href.startswith(("http://", "https://")):
                host = (urlparse(href).hostname or "").lower()
                if host in BLOCKED_DOMAINS or not href.startswith("https://"):
                    self.blocked_links.append(href)
                elif self.in_tr:
                    self.tr_https_urls.append(href)

    def handle_data(self, data: str) -> None:
        if self.in_tr:
            self.tr_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            if self.tr_has_td:
                self.rows.append(
                    {
                        "row_index": self.tr_index,
                        "text": norm_ws("".join(self.tr_text))[:120],
                        "https_urls": list(self.tr_https_urls),
                    }
                )
            self.in_tr = False


def extract_item_section(md_text: str, item_id: str) -> str:
    pattern = rf"^##\s+{re.escape(item_id)}\b.*?(?=^##\s+|\Z)"
    m = re.search(pattern, md_text, flags=re.M | re.S)
    return m.group(0) if m else ""


def load_all_listing_items(root: Path) -> list[dict]:
    items: list[dict] = []
    listings_dir = root / "data" / "listings"
    if listings_dir.exists():
        for path in sorted(listings_dir.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            for item in doc.get("items", []):
                items.append({**item, "_file": str(path.relative_to(root))})
    solid_path = root / "data" / "solid-gold-verified.json"
    if solid_path.exists():
        doc = json.loads(solid_path.read_text(encoding="utf-8"))
        for item in doc.get("items", []):
            items.append({**item, "_file": str(solid_path.relative_to(root))})
    return items


def audit_repository(root: Path) -> dict:
    findings: list[dict] = []
    controls_passed = 0

    def add_finding(code: str, target: str, detail: str) -> None:
        findings.append({"code": code, "target": target, "detail": detail})

    # 1. Gold spot quote & rendered freshness check
    gp_path = root / "data" / "gold-price.json"
    if not gp_path.exists():
        add_finding("MISSING-GOLD-PRICE", "data/gold-price.json", "Missing gold spot data file")
    else:
        gp = json.loads(gp_path.read_text(encoding="utf-8"))
        quotes_joined = " ".join(gp.get("evidence_quotes", []))
        m_date = re.search(r"Data as of\s+(\d{1,2})\s+([A-Za-z]+),?\s+(20\d{2})", quotes_joined, re.I)
        if m_date:
            expected_iso = f"{m_date.group(3)}-{MONTHS[m_date.group(2).lower()]}-{int(m_date.group(1)):02d}"
            if gp.get("quote_date") != expected_iso:
                add_finding(
                    "GOLD-QUOTE-DATE-MISMATCH",
                    "data/gold-price.json",
                    f"quote_date={gp.get('quote_date')} != source quote date {expected_iso}",
                )
            else:
                controls_passed += 1
        spot = Decimal(str(gp["usd_per_troy_oz"]))
        spot_fmt = f"${spot:,.2f}"
        for page_name in ("index.html", "prices.html", "methods.html"):
            p = root / page_name
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                if spot_fmt not in txt:
                    add_finding(
                        "STALE-RENDERED-SPOT-PRICE",
                        page_name,
                        f"Expected {spot_fmt} from data/gold-price.json in rendered {page_name}",
                    )
                else:
                    controls_passed += 1

    # 2. Item-scoped anti-hallucination evidence check
    flags_doc = json.loads((root / "data" / "flags.json").read_text(encoding="utf-8"))
    flags_map = {f["id"]: f for f in flags_doc.get("flags", [])}
    items = load_all_listing_items(root)
    if not items:
        add_finding("NO-LISTINGS", "data/listings", "No listing items found")

    for item in items:
        iid = item["id"]
        ev_rel = item.get("evidence_file", "")
        ev_path = root / ev_rel
        if not ev_path.exists():
            add_finding("EVIDENCE-FILE-MISSING", iid, ev_rel)
            continue
        section = extract_item_section(ev_path.read_text(encoding="utf-8"), iid)
        if not section:
            add_finding("ITEM-EVIDENCE-SECTION-MISSING", iid, f"Missing '## {iid}' in {ev_rel}")
            continue
        norm_sec = norm_ws(section).lower()
        for q in item.get("evidence_quotes", []):
            if norm_ws(q).lower() not in norm_sec:
                add_finding("QUOTE-NOT-IN-ITEM-SECTION", iid, q)
        if item.get("metal") and norm_ws(item["metal"]).lower() not in norm_sec:
            add_finding("METAL-NOT-IN-ITEM-SECTION", iid, str(item["metal"]))
        if item.get("color") and not re.search(rf"\b{re.escape(str(item['color']))}\b", section, re.I):
            add_finding("COLOR-NOT-IN-ITEM-SECTION", iid, str(item["color"]))
        joined_quotes = norm_ws(" ".join(item.get("evidence_quotes", []))).lower()
        if item.get("sku") and norm_ws(str(item["sku"])).lower() not in joined_quotes:
            add_finding("UNQUOTED-SKU", iid, str(item["sku"]))
        if item.get("solid_gold_explicit"):
            if not re.search(r"solid[^.\n]{0,25}gold", joined_quotes, re.I):
                add_finding("UNSUPPORTED-SOLID-GOLD-TRUE", iid, "solid_gold_explicit=True without verbatim 'solid ... gold' quote")
        else:
            if "solid" in (item.get("notes") or "").lower():
                add_finding("SOLID-WORD-IN-NOTES", iid, item.get("notes", ""))
        if item.get("width_mm") is None:
            rel_flags = [flags_map[fid] for fid in item.get("flags", []) if fid in flags_map]
            if not any("width" in (rf["title"] + " " + rf["detail"]).lower() for rf in rel_flags):
                add_finding("MISSING-WIDTH-FLAG", iid, "width_mm is null without a width-specific flag")
        controls_passed += 1

    # 3. HTML pages: CSP, XSS sinks, no-hallucinations top banner, and 100% <tr> official https:// links
    html_files = sorted(list(root.glob("*.html")) + list((root / "site").glob("*.html")))
    for html_path in html_files:
        rel_name = str(html_path.relative_to(root))
        raw = html_path.read_text(encoding="utf-8")
        if EVENT_HANDLER_RE.search(raw):
            add_finding("INLINE-EVENT-HANDLER", rel_name, "Inline on*= attribute found")
        for script_body in re.findall(r"<script\b[^>]*>(.*?)</script>", raw, flags=re.S | re.I):
            if DANGEROUS_JS_RE.search(script_body):
                add_finding("DANGEROUS-JS-SINK", rel_name, "Disallowed DOM sink (innerHTML/eval) inside <script>")
        inspector = PageHTMLInspector()
        inspector.feed(raw)
        if not inspector.has_csp:
            add_finding("MISSING-CSP-META", rel_name, "Missing Content-Security-Policy <meta> header")
        if inspector.target_blank_missing_noopener:
            add_finding("MISSING-REL-NOOPENER", rel_name, ", ".join(inspector.target_blank_missing_noopener[:3]))
        if inspector.blocked_links:
            add_finding("NON-OFFICIAL-OR-HTTP-LINK", rel_name, ", ".join(inspector.blocked_links[:3]))
        for row in inspector.rows:
            if not row["https_urls"]:
                add_finding(
                    "TABLE-ROW-MISSING-OFFICIAL-HTTPS-LINK",
                    f"{rel_name}#row-{row['row_index']}",
                    f"Table data row lacks official https:// link: {row['text']}",
                )
            else:
                controls_passed += 1

    # 4. Prominent top-of-front-page No-Hallucinations statement & Flagged link check
    for front in ("index.html", "site/index.html"):
        fp = root / front
        if fp.exists():
            txt = fp.read_text(encoding="utf-8")
            head_slice = txt[: min(len(txt), 9000)]
            if not re.search(r"no[- ]hallucination", head_slice, re.I):
                add_finding("MISSING-TOP-NO-HALLUCINATION-BANNER", front, "Top summary must explicitly state the No-Hallucinations policy")
            elif "flags.html" not in head_slice:
                add_finding("TOP-SUMMARY-MISSING-FLAGS-LINK", front, "Top summary must link directly to Flagged for Review (flags.html)")
            else:
                controls_passed += 1

    # 5. GitHub Actions full 40-char commit SHA pinning check & secret scan
    wf_dir = root / ".github" / "workflows"
    if wf_dir.exists():
        for wf in sorted(wf_dir.glob("*.yml")):
            rel_wf = str(wf.relative_to(root))
            wf_txt = wf.read_text(encoding="utf-8")
            for line_no, line in enumerate(wf_txt.splitlines(), 1):
                m_use = re.match(r"^\s*-?\s*uses:\s*([^\s#]+)", line)
                if m_use:
                    spec = m_use.group(1).strip("'\"")
                    if "@" not in spec or not SHA_PIN_RE.match(spec.split("@", 1)[1]):
                        add_finding("UNPINNED-GITHUB-ACTION", f"{rel_wf}:{line_no}", f"Action not pinned to 40-hex commit SHA: {spec}")
                    else:
                        controls_passed += 1

    for tracked in root.rglob("*"):
        if not tracked.is_file() or ".git" in tracked.parts or tracked.suffix in {".png", ".jpg", ".ico", ".woff2"}:
            continue
        try:
            content = tracked.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_RE.search(content):
            add_finding("POTENTIAL-SECRET-TOKEN", str(tracked.relative_to(root)), "Matched token pattern")

    # 6. WCAG 2.1 AA CSS contrast verification (>= 4.5:1 for normal text tokens, resolving var(--x))
    def resolve_css_color(raw_val: str, vmap: dict[str, str]) -> str | None:
        raw_val = raw_val.strip()
        if raw_val.startswith("#"):
            return raw_val
        mv = re.match(r"var\(--([a-z0-9-]+)\)", raw_val)
        if mv and mv.group(1) in vmap:
            return vmap[mv.group(1)]
        return None

    for css_rel in ("assets/style.css", "site/style.css"):
        cp = root / css_rel
        if not cp.exists():
            continue
        css_txt = cp.read_text(encoding="utf-8")
        vars_map = dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", css_txt))
        bg = vars_map.get("bg", vars_map.get("paper", "#ffffff"))
        surface = vars_map.get("surface", vars_map.get("panel", "#ffffff"))
        for token in ("ink", "muted", "accent"):
            if token in vars_map:
                ratio = contrast_ratio(vars_map[token], bg)
                if ratio < 4.5:
                    add_finding("WCAG-CONTRAST-FAIL", f"{css_rel}:--{token}/bg", f"Contrast {ratio:.2f}:1 < 4.50:1")
                else:
                    controls_passed += 1
                ratio_surf = contrast_ratio(vars_map[token], surface)
                if ratio_surf < 4.5:
                    add_finding("WCAG-CONTRAST-FAIL", f"{css_rel}:--{token}/surface", f"Contrast {ratio_surf:.2f}:1 < 4.50:1")
                else:
                    controls_passed += 1
        m_eye = re.search(r"\.eyebrow\s*\{[^}]*?color\s*:\s*([^;\}]+)", css_txt, re.S)
        if m_eye:
            eye_fg = resolve_css_color(m_eye.group(1), vars_map)
            if eye_fg:
                ratio_eye = contrast_ratio(eye_fg, bg)
                if ratio_eye < 4.5:
                    add_finding("WCAG-CONTRAST-FAIL", f"{css_rel}:.eyebrow", f"Contrast {ratio_eye:.2f}:1 < 4.50:1 ({eye_fg} on {bg})")
                else:
                    controls_passed += 1

    return {"findings": findings, "controls_passed": controls_passed}


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--json"]
    as_json = "--json" in argv[1:]
    target = Path(args[0]).resolve() if args else Path.cwd().resolve()
    result = audit_repository(target)
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"SECURITY & HALLUCINATION SCAN: {len(result['findings'])} findings; "
            f"{result['controls_passed']} controls passed"
        )
        for f in result["findings"]:
            print(f"  [{f['code']}] {f['target']} :: {f['detail']}")
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
