#!/usr/bin/env bash
# S-59551D4B — runs every builder/scanner/test in the repo and records PASS/FAIL per step.
# Usage: bash audit/59551d4b/run_all_checks.sh <label>     (outputs -> audit/59551d4b/check_runs/<label>_*.txt)
set -u
label="${1:-run}"; out="audit/59551d4b/check_runs"; mkdir -p "$out"
summary="$out/${label}_SUMMARY.txt"; : > "$summary"
step() { # name, command...
  local name="$1"; shift
  if "$@" > "$out/${label}_${name}.txt" 2>&1; then echo "PASS  $name" | tee -a "$summary"; else echo "FAIL  $name (exit $?)" | tee -a "$summary"; fi
}
step root_build            python3 tools/build_site.py
step root_qa               python3 tools/qa.py
step root_calc_test        node tools/test_calculator.js
step root_build_again      python3 tools/build_site.py
step snapshot_audit        python3 reviews/independent_snapshot_audit.py .
step scan_8c810c15         python3 audit/8c810c15/security_and_hallucination_scanner.py .
step test_8c810c15         python3 audit/8c810c15/test_calculator_and_scanner.py
step scan_b200a880         python3 audit/b200a880/hallucination_security_scanner.py .
step test_b200a880         python3 audit/b200a880/test_scanner.py
step scan_88aa65fd         python3 audit/88aa65fd/hallucination_scan.py .
step dashboard_build       python3 dashboard/scripts/build.py
step dashboard_verify      python3 dashboard/scripts/verify.py --check-build
step dashboard_calc_test   node dashboard/scripts/calc-test.js
step scan_9b875c81         python3 audit/9b875c81/hallucination_security_pass.py .
step test_9b875c81         python3 audit/9b875c81/test_pass.py
step legacy_build          python3 scripts/build.py
step legacy_audit          python3 scripts/audit.py
step legacy_test           node scripts/test.js
step explore_verify        npm run -s verify
step explore_node_tests    npm test
step explore_build         npm run -s build
step explore_check_links   npm run -s check:links
step explore_security      node scripts/security.mjs
step scan_59551d4b         python3 audit/59551d4b/hallucination_scan.py .
step peer_provenance_dates python3 audit/36620e91/test_provenance_dates.py
echo "--- git status (generated files must be reproducible) ---" >> "$summary"
git status --short -- . ':!audit/59551d4b' ':!reports/qa-report.md' >> "$summary"
cat "$summary" | tail -5 >/dev/null
