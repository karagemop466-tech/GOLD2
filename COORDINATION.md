# GOLD2 coordination board

## Rules and session

- Active session: `arena-24aeb4a8` (research, implementation, and final integration).
- Fixed Arena branch: `arena/24aeb4a8-gold2`. Arena requires all session work and pushes on this branch; no alternate task branches will be created.
- Read this board before claiming work. Do not edit another session's claimed files. Log cross-scope requests here. Claims with no commits for more than 60 minutes may be handed off with an explicit log entry.
- `needs review` means the issue is published on **Flagged for Review**; it does not block publication. Missing evidence must not be represented as verification.
- Shared data, navigation, and deployment files are reserved for the final integration owner below. All current tasks are owned by this session because the repository is initially empty apart from `README.md`.

## Task board

| Task | Status | Owner | File scope | Claimed (UTC) | Verification / sources / irregularities |
| --- | --- | --- | --- | --- | --- |
| R1 — Audit existing repository and establish evidence policy | in progress | arena-24aeb4a8 | `README.md`, `docs/**` | 2026-10-22T23:08:10Z | Initial tree contains only a one-line README. No existing products, prices, dependencies, or application to verify. |
| R2 — Research official product and buyer-protection sources | in progress | arena-24aeb4a8 | `research/**` | 2026-10-22T23:08:10Z | Collect official sources with observation timestamps; leave unconfirmed values blank. No claim of exhaustive market coverage. |
| I1 — Final integration: evidence data, dashboard, calculator, review page | in progress | arena-24aeb4a8 | `index.html`, `assets/**`, `data/**`, `catalog/**`, `calculator/**`, `standards/**`, `sources/**`, `review/**`, `404.html` | 2026-10-22T23:08:10Z | Owns all shared outputs. Do not enter unverified prices or infer missing specifications. |
| Q1 — Automated evidence, security, link, accessibility and build checks | in progress | arena-24aeb4a8 | `scripts/**`, `tests/**`, `package.json`, `package-lock.json`, `.gitignore`, `.github/**` | 2026-10-22T23:08:10Z | Deterministic checks flag missing/stale/unsupported facts; they cannot prove authenticity or detect every hallucination. |
| P1 — PR, merge, GitHub Pages publication, final verification | in progress | arena-24aeb4a8 | `COORDINATION.md` and GitHub repository/Pages settings | 2026-10-22T23:08:10Z | Open and merge explicit PR number only after checks pass; confirm deployment independently. |

## Log

- **2026-10-22T23:08:10Z — arena-24aeb4a8:** Read repository and remote state. No coordination file, other remote work branches, open PRs, or uncommitted changes found. Created this board and claimed the scopes above before implementation. The user's requested task-branch scheme is superseded by Arena's fixed session-branch requirement. Will pull/rebase before each push, make small commits, and preserve other sessions' work if new work appears.

## Publication record

- PR: pending
- Merge: pending
- Pages URL: pending
- Deployment: pending
