# CI/CD Pipeline

How code gets from an idea to the live site, safely. Designed so a non-technical
developer never has to deploy by hand — the pipeline does it.

---

## The flow

```
Feature branch  →  Pull Request  →  CI checks + Vercel preview  →  Merge to main  →  Production
   (your work)      (open it)        (must be green)               (one click)       (automatic)
```

1. **Branch.** Never work on `main`. Create `feature/<short-name>`.
2. **Open a Pull Request** into `main`.
3. **CI runs automatically** (`.github/workflows/ci.yml`): install, lint, type-check,
   build. (Tests run here too as they're added — see `docs/TESTING.md`.)
4. **Vercel builds a preview deployment** for the PR — a real URL to click and check
   the change before it's live.
5. **Merge only when CI is green** and the preview looks right.
6. **Vercel deploys to production automatically** on merge to `main`
   (`vercel.json` enables git deploys for `main`).

---

## CI checks (the gate)

Defined in `.github/workflows/ci.yml`, run on every PR and push to `main`:

| Check | Command | Catches |
|---|---|---|
| Install | `npm ci` | broken/locked dependencies |
| Lint | `npm run lint` | bad patterns, unused code |
| Build + type-check | `npm run build` | type errors and anything that breaks the production build (`next build` type-checks with TypeScript strict and fails on any type error) |

**A red check blocks merge. Never merge a red PR.** If a check fails, ask Claude Code
to read the failure and fix the cause — don't disable the check.

Run the exact same checks locally before pushing with `npm run verify` (or the
`/preflight` skill). If it passes locally, CI should pass too.

---

## Environments

| Environment | Trigger | URL | Purpose |
|---|---|---|---|
| **Preview** | open/update a PR | per-PR Vercel URL | review before going live |
| **Production** | merge to `main` | live site | real users |

---

## Secrets & configuration

- Secrets (Supabase, OpenAI, Stripe keys) live in **Vercel Project Settings →
  Environment Variables** and, for CI, in **GitHub repo → Settings → Secrets**.
- **Never** put a real key in the repo or in `public/`. See `CLAUDE.md` §4.

---

## If something breaks in production

1. Don't panic and don't hot-edit `main`.
2. In Vercel, **roll back** to the previous deployment (instant).
3. Then fix forward via a normal PR.

---

## Setup checklist (one-time, for whoever owns the repo)
- [ ] `.github/workflows/ci.yml` present (✅ included).
- [ ] `package.json` has `lint`, `build`, `verify` scripts (✅ included).
- [ ] ESLint installed with a flat `eslint.config.mjs` (✅ included).
- [ ] Branch protection on `main`: require the CI check to pass before merge.
- [ ] Vercel project connected to the repo, Production Branch = `main`.
