# Evidence — gold price reference

- **Source:** World Gold Council, "Gold spot prices"
- **URL:** https://www.gold.org/goldhub/data/gold-prices
- **Retrieved:** 2026-10-22 (UTC)
- **Method:** live page fetch; values copied from the rendered text

## Verbatim excerpts

```
USD
/oz
-
4,024.36
```

```
Data as of 21 October, 2026
```

```
Market Data: Provided by ICE Data Services.
```

## Cross-check: LBMA (not usable as a free source)

Source: https://www.lbma.org.uk/prices-and-data/precious-metal-prices (retrieved 2026-10-22)

```
## Tables have moved to the MyLBMA Portal

The historical tabulated data for the LBMA Precious Metals Prices has been moved to our MyLBMA Portal. In order to view this data on our Portal, you will need to have the relevant licence from IBA.
```

**Consequence:** no free LBMA fix value is recorded in `data/gold-price.json`. The World Gold Council quote is used instead, with its date. This is recorded as flag F-013.

## Re-check — session S-75094819, 2026-10-22 (UTC)

Same URL fetched again. The spot widget now renders a different value; the chart dataset date is unchanged.
The widget shows "Last Updated" but no date/time beside the figure in the captured text.

```
USD

/oz

-

4,028.53

Last Updated
```

```
Data as of 21 October, 2026
```

**Action:** `data/gold-price.json` updated to 4028.53 USD/troy oz with `retrieved_at` 2026-10-22 and
`quote_date` 2026-10-21 (the dataset date printed on the page). The earlier 4024.36 observation above is
preserved verbatim and in `quote_history`. No value was averaged or carried forward without re-reading the page.
