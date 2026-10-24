# S-F3B0B698 companion reconciliation audit

This additive audit does not import the root QA implementation, combined verifier, companion adapter, or companion verifier. It performs no network requests and makes no physical-authentication claim.

## Files

- `PRE_FIX_FINDINGS.md` — inherited baseline and companion/canonical drift found before the repair.
- `companion_audit.py` — independent offline canonical parity, blank/evidence, seller, rendered-row, arithmetic, policy, and security scanner.
- `test_mutations.py` — clean control plus deliberately injected defects; every mutation must be detected.
- `post-fix-scan.json` — machine-readable scanner result for the integrated companion state.
- `POST_FIX_VERIFICATION.md` — final command results and deployment record (completed after integration).

## Run

```bash
python3 dashboard/scripts/build.py
python3 dashboard/scripts/verify.py --check-build
python3 audit/f3b0b698/companion_audit.py \
  --root "$(pwd)" --json audit/f3b0b698/post-fix-scan.json
python3 audit/f3b0b698/test_mutations.py
```

To run the mutation controls against a disposable generated tree rather than the checkout:

```bash
GOLD2_AUDIT_ROOT=/path/to/disposable/repo python3 audit/f3b0b698/test_mutations.py
```

A PASS is limited to offline internal consistency. It does not prove source freshness, actual gold purity, seller behavior, or the absence of every hallucination. **Look for hallucinations again after every review and rerun all repository verification and security scans.**
