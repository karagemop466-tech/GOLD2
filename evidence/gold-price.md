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
4,028.53
Last Updated
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
