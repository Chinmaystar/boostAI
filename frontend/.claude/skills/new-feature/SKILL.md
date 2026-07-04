---
name: new-feature
description: Guided, safe workflow for adding or changing a feature in BoostAI Study (a new page, section, component, or behaviour). Use when the user wants to build something bigger than a small copy or style tweak. Keeps a non-technical developer on the rails — branch, build small, verify, PR.
---

# Add a feature safely

Walk the developer through a change end-to-end without them needing to know git or
the codebase. Follow `CLAUDE.md` and `docs/ARCHITECTURE.md` throughout. Prefer the
smallest change that works — this is an MVP.

## 0. Gate before you start

### One thing at a time
Before doing anything else, run:
```
git branch --format='%(refname:short)' | grep -v '^main$'
git rev-parse --abbrev-ref HEAD
git status --short
```

Check for:
1. **Other feature branches** — compare each non-main branch against the *current* branch (from `rev-parse`). For any branch that is **not** the current branch, run `git log main..<branch> --oneline`. If any such branch has commits not yet merged into `main`, pause and tell the user in plain language:
   > "It looks like you already have work in progress on branch `feature/x`. It's best to finish one thing at a time — it keeps the project clean and makes sure nothing gets lost. Would you like to finish that one first, or is it safe to leave it for now?"
   - If the user says finish it first: help them run `/preflight`, commit, and open a PR before continuing.
   - If the user says leave it: confirm they're happy to park it, then continue.

2. **Uncommitted changes on the current branch** — if `git status` shows modified or untracked files (excluding `.DS_Store`), pause:
   > "There are unsaved changes on your current branch. Let's make sure nothing gets lost — do you want to save (commit) these changes first, or are they safe to discard?"
   - If save: help them commit with a plain-English message.
   - If discard: confirm explicitly before proceeding.

### Scope gate
Check the request against `CLAUDE.md` §7. If it touches `public/`, auth, payments,
the database, new dependencies, or env vars — **stop and ask the user first.**

## 1. Understand
- Restate the goal in one sentence and confirm it with the user.
- Find where it belongs using the map in `CLAUDE.md` §2:
  - UI/content → `components/boostai/`
  - new URL → a thin `app/<route>/page.tsx` that renders a component
  - static content/data → `site-data.ts` (typed)
- Read the relevant component(s) and CSS module before changing anything.

## 2. Branch
- Check the current branch (`git rev-parse --abbrev-ref HEAD`):
  - If already on a feature branch (anything that isn't `main`), stay on it — do **not** create a new branch.
  - If on `main`, create a new branch:
    ```
    git checkout -b feature/<short-name>
    ```

## 3. Build small
- Make the smallest change that satisfies the goal. Match existing patterns:
  named exports, `"use client"` only when state/effects are used, CSS Modules,
  `@/` imports, `next/image` for images.
- Keep new content typed in `site-data.ts` rather than hard-coded in JSX.

## 4. Test (right-sized to the feature)

Before verifying, decide the risk tier by what the feature touches (see `docs/TESTING.md`):

- **High risk** — auth, payments, subscriptions, AI output, user data:
  > "This feature touches a high-risk area, so we'll write a few tests to make sure it works correctly — and keeps working as the project grows. I'll write them for you, you just need to review that they match what you expect."
  Write component tests covering the core behaviours (happy path + key failure case) and a Playwright smoke test for the critical user path. Do not mark the feature done until these pass.

- **Medium risk** — new interactive UI, state, forms, API routes:
  > "This feature has some moving parts, so it's worth a quick test to make sure the main flow works. I'll write it — it only takes a moment."
  Write a component test covering the happy path and one edge case. Offer to add more if the logic is complex.

- **Low risk** — copy, styling, static content, layout:
  > "This is a straightforward change, so a quick preflight check is all we need here."
  No additional tests. Proceed to step 5.

If you're unsure of the tier, go one level higher. Never skip tests for a High risk feature.

## 5. Verify
- Run the `/preflight` skill (lint + types + build). Do not proceed until green.

## 6. Show & confirm
- Summarise what changed in plain language — what it does, what tier it was, and what tests were written (if any). Suggest viewing the Vercel preview once the PR is open.

## 7. Commit & PR (only when the user says yes)
- Commit with a short plain-English message.
- Push the branch and open a Pull Request into `main` (do not merge automatically).
- Remind the user that CI must be green and the preview should look right before merge
  (`docs/CICD.md`).

## Never
- Edit `public/` without asking. Add `any`/`@ts-ignore`. Add dependencies silently.
  Push to `main`. Skip preflight.
