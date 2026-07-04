---
name: preflight
description: Run before committing or pushing any change to BoostAI Study. Runs lint, type-check, and build (the same checks CI runs) and reports pass/fail in plain language. Use whenever the user is about to commit, push, or open a PR, or asks "is this safe to ship / deploy / push?".
---

# Preflight check

You are the safety gate before code leaves the developer's machine. Run the exact
checks that CI runs (see `docs/CICD.md`) so there are no surprises in the Pull Request.

## Steps

1. If dependencies aren't installed yet (e.g. `next: not found`), run `npm ci` first.

2. Run the full verification:
   ```
   npm run verify
   ```
   This runs lint, then build.

3. Run a standalone type-check (belt-and-braces — `next build` can skip type errors
   if `ignoreBuildErrors` is ever set in `next.config.*`):
   ```
   npx tsc --noEmit
   ```

4. Report the result in plain, non-technical language:
   - **All green:** say clearly that lint, types, and build all passed and it's safe
     to commit/push.
   - **Something failed:** show *which* step failed (lint, types, or build) and the
     key error line(s). Explain what it means in one sentence, then propose the
     smallest fix. **Do not** fix by adding `any`, `@ts-ignore`, or disabling lint
     rules — fix the real cause or ask the user.

5. Never commit or push from this skill. Reporting the result is the job; the user
   (or another skill) decides what to do next.

## Reminders
- This mirrors `.github/workflows/ci.yml`. If it passes here, CI should pass too.
- If the user hasn't read `CLAUDE.md` §3 (the safe loop), point them to it.
