# Evidence — Zales policies

- **URL:** product pages (see each listing)
- **Retrieved:** 2026-10-22 (UTC)

## Returns — verbatim excerpt (appears on every Zales product page retrieved)

```
Free and easy 30-day returns
```

## Not captured (at first pass, 2026-10-22)

- Standalone return-policy page (exclusions for resized / custom / clearance) — **not retrieved**.
- Contact phone / email — **not retrieved**.
- Metal weight in grams — **not published**.

These gaps are recorded as flag F-011 and are left blank in `data/retailers.json`.

---

## Standalone return policy — retrieved 2026-10-22 (session S-75094819)

- **Canonical policy page:** https://www.zales.com/return-and-exchange-policy
  (page title "Returns and Exchanges | Zales"; the text fetcher returned only the site navigation
  for this URL, so the policy body could not be quoted from it directly)
- **Text actually read from:** https://www.zales.com/return-and-exchange-modal
  (Zales' own modal rendition of the same policy, on zales.com; body fully extractable)
- **Method:** live page fetch; excerpts below copied verbatim from the modal page.

### Verbatim excerpts (modal page)

```
## Returns & Exchanges Policy

You may return your purchase within 30 days of the purchase(shipped) date. You may exchange jewelry within 60 days and watches within 30 days. Returns and exchanges are not allowed on special ordered watches, custom designs, ear piercing earrings, gift cards and merchandise received via the Jewelry Replacement Plan. Jewelry must be in good condition and watches unworn, unaltered and accompanied by the original packaging, warranty and instructions.
```

```
All refunds are credited to the same tender as the original purchase

- Credit and Debit Cards – The same account will be credited.
```

```
## Return by Mail

- Start your return online
- Ship your items with the prepaid shipping label that we'll email to you to print at home.
- Returns are processed within 5 business days and refunds can be expected 5-7 business days after processing.
```

### What this verifies

- Return window: 30 days from the purchase (shipped) date for jewelry returns; 60 days for jewelry exchanges.
- Custom exclusion: **yes** — "custom designs" are named verbatim.
- Free mail return shipping: **yes** — prepaid label offered.
- Card tender: "Credit and Debit Cards" are named as an original-purchase tender (refunds credited to the
  same account). Specific card networks are **not** stated on the retrieved page.

### What the retrieved policy text still does NOT state

- **Resized / sized-to-order rings:** the retrieved modal text does not mention resizing or sized-to-order
  rings at all. `return_excludes_resized` therefore stays blank. (A search-engine snippet for the canonical
  page mentioned a sizing-fee refund, but snippets are rejected sources in this project and the canonical
  page body was not extractable — not published as fact.)
- **Contact phone / email:** not on the retrieved policy pages. Still blank.
- **Metal weight in grams:** still not published on Zales product pages (flag F-003).

### Rejected source encountered during discovery

- `https://zales-jewelry.com/returns-refund/` appeared in search results using the Zales name. It is **not**
  Zales' official domain (`zales.com`) and was not used as a source for anything. Recorded here so a manual
  reviewer does not mistake it for the retailer.
