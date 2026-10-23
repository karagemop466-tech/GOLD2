#!/usr/bin/env python3
"""
hallucination_security_pass.py — Session S-9B875C81 multi-surface anti-hallucination,
gemstone-mass physics, provenance quote verification, link integrity, CSP/XSS security,
GitHub Actions 40-SHA pinning, and WCAG 2.1 AA contrast auditor.

Audits:
  1. Audit artifacts (`audit/9b875c81/*.json` + `audit/9b875c81/evidence/**`)
  2. Companion dashboard (`dashboard/*.html` + `dashboard/data/*.json`) if present
  3. Root GitHub Pages dashboard (`*.html`, `data/**`, `evidence/**`), `site/`, and `.github/workflows/*.yml`

Run after EVERY review pass and EVERY build:
    python3 audit/9b875c81/hallucination_security_pass.py .
"""

from __future__ import annotations

import json
import math
import re
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

TROY_OZ_GRAMS = Decimal("31.1034768")
DWT_GRAMS = Decimal("1.55517384")
CARAT_GRAMS = Decimal("0.2")

BLOCKED_HOSTS = {
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

INLINE_EVENT_RE = re.compile(r"\bon(?:click|input|change|submit|load|error|mouseover|focus|keyup|keydown)\s*=", re.I)
DANGEROUS_SINK_RE = re.compile(r"\b(?:innerHTML|outerHTML|insertAdjacentHTML|eval)\s*[=(]")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SECRET_TOKEN_RE = re.compile(r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,})")


def norm_ws(text: str) -> str:
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
        text = text.replace(ch, "")
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def hex_to_srgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def relative_luminance(hex_color: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_srgb(hex_color)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def wcag_contrast(fg: str, bg: str) -> float:
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def compute_melt_nist(
    weight: float,
    karat: int,
    spot_usd_per_ozt: float,
    unit: str = "g",
    stone_carats_deduct: float = 0.0,
    ask_usd: float | None = None,
) -> dict | None:
    """Exact Decimal reference math with gem-carat mass subtraction safety check."""
    if not (math.isfinite(weight) and math.isfinite(karat) and math.isfinite(spot_usd_per_ozt)):
        return None
    if not math.isfinite(stone_carats_deduct) or stone_carats_deduct < 0:
        return None
    if weight <= 0 or karat <= 0 or karat > 24 or spot_usd_per_ozt <= 0:
        return None

    w_dec = Decimal(str(weight))
    if unit == "g":
        gross_g = w_dec
    elif unit == "dwt":
        gross_g = w_dec * DWT_GRAMS
    elif unit == "ozt":
        gross_g = w_dec * TROY_OZ_GRAMS
    else:
        return None

    stone_g = Decimal(str(stone_carats_deduct)) * CARAT_GRAMS
    net_metal_g = gross_g - stone_g
    if net_metal_g <= 0:
        return None

    fine_g = net_metal_g * Decimal(karat) / Decimal(24)
    usd_per_g = Decimal(str(spot_usd_per_ozt)) / TROY_OZ_GRAMS
    melt_usd = fine_g * usd_per_g

    result: dict = {
        "gross_g": float(round(gross_g, 4)),
        "stone_g": float(round(stone_g, 4)),
        "net_metal_g": float(round(net_metal_g, 4)),
        "fine_g": float(round(fine_g, 3)),
        "melt_usd": float(round(melt_usd, 2)),
        "multiple": None,
        "gold_share_pct": None,
    }
    if ask_usd is not None:
        if not math.isfinite(ask_usd) or ask_usd <= 0:
            return None
        ask_dec = Decimal(str(ask_usd))
        result["multiple"] = float(round(ask_dec / melt_usd, 2))
        result["gold_share_pct"] = float(round(melt_usd / ask_dec * Decimal(100), 2))
    return result


class HTMLSecurityAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_csp = False
        self.csp = ""
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.scripts: list[str] = []
        self.has_inline_script = False
        self.in_tr = False
        self.tr_has_td = False
        self.tr_index = 0
        self.tr_text: list[str] = []
        self.tr_https: list[str] = []
        self.rows: list[dict] = []
        self.bad_links: list[str] = []
        self.missing_noopener: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {k.lower(): (v or "") for k, v in attrs}
        if "id" in amap and amap["id"]:
            self.ids.append(amap["id"])
        if tag == "meta" and amap.get("http-equiv", "").lower() == "content-security-policy":
            self.has_csp = True
            self.csp = amap.get("content", "")
        elif tag == "script":
            if "src" in amap and amap["src"]:
                self.scripts.append(amap["src"])
            else:
                self.has_inline_script = True
        elif tag == "tr":
            self.in_tr = True
            self.tr_has_td = False
            self.tr_index += 1
            self.tr_text = []
            self.tr_https = []
        elif tag == "td" and self.in_tr:
            self.tr_has_td = True
        elif tag == "a":
            href = amap.get("href", "")
            self.hrefs.append(href)
            if amap.get("target") == "_blank":
                rel = set(amap.get("rel", "").lower().split())
                if "noopener" not in rel:
                    self.missing_noopener.append(href)
            if href.startswith(("http://", "https://", "javascript:")):
                parsed = urlparse(href)
                host = (parsed.hostname or "").lower()
                if parsed.scheme != "https" or host in BLOCKED_HOSTS:
                    self.bad_links.append(href)
                elif self.in_tr:
                    self.tr_https.append(href)

    def handle_data(self, data: str) -> None:
        if self.in_tr:
            self.tr_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            if self.tr_has_td:
                self.rows.append(
                    {
                        "index": self.tr_index,
                        "text": norm_ws("".join(self.tr_text))[:120],
                        "https": list(self.tr_https),
                    }
                )
            self.in_tr = False


def audit_html_directory(html_dir: Path, root: Path, add_finding, controls: list[int], require_row_https: bool = True) -> None:
    if not html_dir.exists():
        return
    html_files = sorted(html_dir.glob("*.html"))
    parsed_cache: dict[Path, HTMLSecurityAndLinkParser] = {}
    for p in html_files:
        rel = str(p.relative_to(root))
        raw = p.read_text(encoding="utf-8")
        if INLINE_EVENT_RE.search(raw):
            add_finding("INLINE-EVENT-HANDLER", rel, "Disallowed inline event handler found")
        for token in (">None<", ">nan<", "undefined", "{{", "}}"):
            if token in raw:
                add_finding("SUSPICIOUS-TEMPLATE-TOKEN", rel, f"Found unrendered token {token!r}")
        parser = HTMLSecurityAndLinkParser()
        parser.feed(raw)
        parsed_cache[p] = parser
        if not parser.has_csp:
            add_finding("MISSING-CSP", rel, "Missing Content-Security-Policy meta tag")
        if len(parser.ids) != len(set(parser.ids)):
            add_finding("DUPLICATE-DOM-ID", rel, "Duplicate element IDs detected")
        if parser.missing_noopener:
            add_finding("MISSING-NOOPENER", rel, ", ".join(parser.missing_noopener[:3]))
        if parser.bad_links:
            add_finding("UNSAFE-OR-BLOCKED-URL", rel, ", ".join(parser.bad_links[:3]))
        for s_src in parser.scripts:
            sp = (p.parent / s_src).resolve()
            if not sp.is_file():
                add_finding("MISSING-SCRIPT-ASSET", rel, s_src)
            elif DANGEROUS_SINK_RE.search(sp.read_text(encoding="utf-8")):
                add_finding("DANGEROUS-DOM-SINK", s_src, "Disallowed innerHTML/outerHTML/eval sink")
        if require_row_https:
            for row in parser.rows:
                if not row["https"]:
                    add_finding("ROW-MISSING-OFFICIAL-SOURCE", f"{rel}#tr-{row['index']}", row["text"])
                else:
                    controls[0] += 1
        controls[0] += 1

    # Check internal relative links & fragments within html_dir
    for p, parser in parsed_cache.items():
        rel = str(p.relative_to(root))
        for href in parser.hrefs:
            parsed = urlparse(href)
            if parsed.scheme in ("https", "http", "mailto", "tel") or not href:
                continue
            target_path = (p.parent / unquote(parsed.path)).resolve() if parsed.path else p.resolve()
            if target_path.is_dir():
                target_path = target_path / "index.html"
            if not target_path.is_file():
                add_finding("BROKEN-INTERNAL-LINK", rel, href)
                continue
            if parsed.fragment and target_path in parsed_cache:
                if parsed.fragment not in parsed_cache[target_path].ids:
                    add_finding("BROKEN-ANCHOR-FRAGMENT", rel, href)
            controls[0] += 1


def scan_workspace(root: Path) -> dict:
    findings: list[dict] = []
    controls = [0]

    def add_finding(code: str, target: str, detail: str) -> None:
        findings.append({"code": code, "target": target, "detail": detail})

    # 1. Verify S-9B875C81 audit JSON & verbatim evidence files
    new_json = root / "audit" / "9b875c81" / "new-listings-2026-10-23.json"
    ver_json = root / "audit" / "9b875c81" / "verified-sources-2026-10-23.json"
    if new_json.is_file() and ver_json.is_file():
        ver_doc = json.loads(ver_json.read_text(encoding="utf-8"))
        new_doc = json.loads(new_json.read_text(encoding="utf-8"))
        spot = float(ver_doc["gold_spot_reference"]["usd_per_troy_oz"])
        if abs(spot - float(new_doc["spot_usd_per_troy_oz"])) > 1e-6:
            add_finding("AUDIT-SPOT-MISMATCH", "audit/9b875c81", "Spot price mismatch across 9b875c81 JSON files")
        else:
            controls[0] += 1

        for item in new_doc.get("new_verified_listings", []):
            iid = item["id"]
            ev_file = root / item["evidence_file"]
            if not ev_file.is_file():
                add_finding("MISSING-NEW-EVIDENCE", iid, item["evidence_file"])
                continue
            ev_txt = norm_ws(ev_file.read_text(encoding="utf-8")).lower()
            if norm_ws(item["name"]).lower() not in ev_txt:
                add_finding("NAME-NOT-IN-EVIDENCE", iid, item["name"])
            if norm_ws(item["sku"]).lower() not in ev_txt:
                add_finding("SKU-NOT-IN-EVIDENCE", iid, item["sku"])
            if item.get("solid_gold_explicit") and "solid" not in ev_txt:
                add_finding("SOLID-GOLD-UNBACKED", iid, "solid_gold_explicit=True without verbatim 'solid' quote")
            # Gem-mass vs gross-weight safety check: never allow an ambiguous gross weight to populate metal-only weight_g!
            if item.get("ambiguous_weight_g") is not None and item.get("weight_g") is not None:
                add_finding("AMBIGUOUS-WEIGHT-ASSIGNED-AS-METAL", iid, "Ambiguous weight must remain null in weight_g")
            if item.get("weight_g") is not None:
                calc = compute_melt_nist(
                    item["weight_g"],
                    item["karat"],
                    spot,
                    unit="g",
                    stone_carats_deduct=0.0,
                    ask_usd=item.get("price"),
                )
                if not calc:
                    add_finding("INVALID-MELT-CALC", iid, "Failed NIST melt verification")
                else:
                    if abs(calc["fine_g"] - item["nominal_fine_gold_g"]) > 0.002:
                        add_finding("FINE-GOLD-DRIFT", iid, f"{calc['fine_g']} != {item['nominal_fine_gold_g']}")
                    if abs(calc["melt_usd"] - item["nominal_melt_usd"]) > 0.02:
                        add_finding("MELT-USD-DRIFT", iid, f"{calc['melt_usd']} != {item['nominal_melt_usd']}")
                    controls[0] += 1
            controls[0] += 1

    # 1b. Dynamic F-001 / F-002 / F-003 prose count invariants against data/listings/*.json
    flags_file = root / "data" / "flags.json"
    listings_dir = root / "data" / "listings"
    if flags_file.is_file() and listings_dir.is_dir():
        listing_files = [
            *sorted(listings_dir.glob("*.json")),
            *([root / "data" / "solid-gold-verified.json"] if (root / "data" / "solid-gold-verified.json").is_file() else []),
        ]
        all_rows = [
            it
            for lf in listing_files
            for it in json.loads(lf.read_text(encoding="utf-8")).get("items", [])
        ]
        fmap = {f["id"]: f for f in json.loads(flags_file.read_text(encoding="utf-8")).get("flags", [])}
        n_total = len(all_rows)
        n_no_solid = sum(1 for it in all_rows if it.get("solid_gold_explicit") is not True)
        n_no_hm = sum(1 for it in all_rows if it.get("hallmark_stated") is not True or it.get("makers_mark_stated") is not True)
        n_no_wt = sum(1 for it in all_rows if it.get("weight_g") is None)
        for fid, expected_substr in (
            ("F-001", f"{n_no_solid} of {n_total}"),
            ("F-002", f"None of the {n_no_hm} captured product pages"),
            ("F-003", f"Only {n_total - n_no_wt} of {n_total} rows publish"),
        ):
            txt = (fmap.get(fid, {}).get("title", "") + " " + fmap.get(fid, {}).get("detail", ""))
            if expected_substr not in txt:
                add_finding("STALE-FLAG-PROSE-COUNT", fid, f"Expected '{expected_substr}' in {fid} title/detail")
            else:
                controls[0] += 1

    # 2. Audit HTML surfaces (root, site/, dashboard/)
    audit_html_directory(root, root, add_finding, controls, require_row_https=True)
    audit_html_directory(root / "site", root, add_finding, controls, require_row_https=True)
    if (root / "dashboard").is_dir():
        audit_html_directory(root / "dashboard", root, add_finding, controls, require_row_https=True)
        dash_idx = root / "dashboard" / "index.html"
        if dash_idx.is_file():
            head_txt = dash_idx.read_text(encoding="utf-8")[:10000]
            if not re.search(r"no[- ]hallucination", head_txt, re.I):
                add_finding("DASHBOARD-MISSING-NO-HALLUCINATION-BANNER", "dashboard/index.html", "Missing top No-Hallucinations policy summary")
            elif "flagged.html" not in head_txt:
                add_finding("DASHBOARD-TOP-MISSING-FLAGGED-LINK", "dashboard/index.html", "Top summary must link to flagged.html")
            else:
                controls[0] += 1

    # 3. WCAG 2.1 AA contrast check across root, site, and dashboard stylesheets
    for css_rel in ("assets/style.css", "site/style.css", "dashboard/assets/style.css"):
        cp = root / css_rel
        if not cp.is_file():
            continue
        css_txt = cp.read_text(encoding="utf-8")
        vmap = dict(re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", css_txt))
        bg = vmap.get("bg", vmap.get("paper", "#ffffff"))
        card = vmap.get("card", vmap.get("surface", vmap.get("panel", "#ffffff")))
        for tok in ("ink", "muted", "gold", "accent", "ok", "warn", "bad", "info"):
            if tok in vmap and tok not in ("ok", "warn", "bad", "info"):
                for surface_name, bg_hex in (("bg", bg), ("card", card)):
                    ratio = wcag_contrast(vmap[tok], bg_hex)
                    if ratio < 4.5:
                        add_finding("WCAG-AA-CONTRAST-FAIL", f"{css_rel}:--{tok}/{surface_name}", f"{ratio:.2f}:1 < 4.50:1")
                    else:
                        controls[0] += 1

    # 4. Workflow SHA pinning & secret scan
    wf_dir = root / ".github" / "workflows"
    if wf_dir.is_dir():
        for wf in sorted(wf_dir.glob("*.yml")):
            rel = str(wf.relative_to(root))
            for idx, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
                m = re.match(r"^\s*-?\s*uses:\s*([^\s#]+)", line)
                if m:
                    spec = m.group(1).strip("'\"")
                    if "@" not in spec or not SHA40_RE.match(spec.split("@", 1)[1]):
                        add_finding("WORKFLOW-NOT-SHA-PINNED", f"{rel}:{idx}", spec)
                    else:
                        controls[0] += 1

    for fpath in root.rglob("*"):
        if not fpath.is_file() or ".git" in fpath.parts or "node_modules" in fpath.parts:
            continue
        if fpath.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".pdf"}:
            continue
        try:
            txt = fpath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_TOKEN_RE.search(txt):
            add_finding("SECRET-EXPOSURE", str(fpath.relative_to(root)), "Matched secret token pattern")

    return {"findings": findings, "controls_passed": controls[0]}


def main(argv: list[str]) -> int:
    as_json = "--json" in argv[1:]
    args = [a for a in argv[1:] if a != "--json"]
    root = Path(args[0]).resolve() if args else Path.cwd().resolve()
    report = scan_workspace(root)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"S-9B875C81 HALLUCINATION & SECURITY PASS: {len(report['findings'])} findings; "
            f"{report['controls_passed']} controls passed"
        )
        for item in report["findings"]:
            print(f"  [{item['code']}] {item['target']} — {item['detail']}")
        print(
            "REMINDER: Automated PASS verifies internal provenance, NIST math, link integrity, "
            "CSP/workflow security, and WCAG AA contrast — keep re-checking primary sources for hallucinations."
        )
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
