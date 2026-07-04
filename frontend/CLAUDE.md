# CLAUDE.md — BoostAI Study

This file tells Claude Code how to work safely in this repository. Read it
before making any change. If a request conflicts with this file, stop and ask.

---

## 0. Who you are working with

The person using Claude Code on this project is **non-technical with no developer background**. They are not a programmer. Keep this in mind at all times:

- **Never use jargon without explaining it.** No "merge conflicts", "type errors", "API routes", "props", "hooks", or git commands dropped without context. If a technical term is unavoidable, explain it in one plain sentence.
- **Explain the why, not just the what.** Don't just say "run preflight" — say "this checks that everything is working correctly before we save your changes."
- **One step at a time.** Never present a wall of options or a multi-step plan all at once. Walk through changes one step at a time and confirm before moving to the next.
- **Use plain, encouraging language.** Mistakes are normal and expected — never make the user feel like they did something wrong. Frame problems as things to fix together, not errors they caused.
- **Never ask the user to run commands directly.** Claude Code runs commands on their behalf. Do not paste terminal commands and ask the user to run them.
- **Decisions should feel easy.** When the user needs to choose something, offer at most two options, explain each in one sentence, and give a clear recommendation.

---

## 1. What this project is

BoostAI Study is an AI-powered learning platform. The long-term product vision
lives in `docs/ARCHITECTURE.md` (the "Target Architecture" section) — read it for
context, but **do not assume those features exist yet**.

**What exists today (the MVP):**
- A Next.js 15 + React 19 + TypeScript web app deployed on Vercel.
- Landing pages (home, school, university) and a demo dashboard.
- Mock content only — no real database, no AI calls, no payments, fake login.

**Golden rule:** This is an MVP. Prefer the smallest change that works. Do not add
new tools, libraries, or services unless the task explicitly requires it and
`docs/ARCHITECTURE.md` approves it.

---

## 2. Where things live (and where to edit)

| You want to change… | Edit here |
|---|---|
| A page's content or layout | `components/boostai/*.tsx` (NOT `app/*/page.tsx`) |
| Routing / which page shows at a URL | `app/<route>/page.tsx` |
| Demo questions, route cards, copy | `components/boostai/site-data.ts` |
| Styling | the matching `*.module.css` next to the component |
| Site-wide `<head>`, fonts, metadata | `app/layout.tsx` |

### ⚠️ The legacy zone — do not edit without asking

`public/` contains an **older, separate** version of the site built as plain
HTML + JavaScript (`public/login.html`, `public/school/`, `public/uni/`,
`public/auth/`, `public/legacy/`, and everything in `public/assets/*.js`).

- This is **not** the React app. Changes here do not follow our conventions.
- The duplicated `*-v2.js` / `*-nb2.js` files are of unknown status — **never edit them.**
- If a task seems to require touching `public/`, **stop and ask the user first.**
  The correct long-term move is usually to rebuild that piece in React.

---

## 3. How to make a change (the safe loop)

1. **Understand first.** Read the relevant component and its CSS module before editing.
2. **Make the smallest change** that satisfies the request.
3. **Run the preflight check** (lint + types + build) — use the `/preflight` skill,
   or run `npm run verify`. Do not skip this.
4. **Show the user what changed** in plain language before committing.
5. **Commit and push** only when the user asks (see section 6).

For anything bigger than a copy/style tweak, use the `/new-feature` skill — it walks
through the change safely.

---

## 4. Hard rules (never break these)

- **Never commit secrets.** API keys, Supabase keys, Stripe keys, and OpenAI keys
  go in environment variables / Vercel project settings — never in the repo.
  `public/assets/supabase-config.js` uses placeholders on purpose; keep it that way.
- **Never push directly to `main`.** `main` is production (Vercel auto-deploys it).
  All work goes on a feature branch and reaches `main` via a Pull Request.
- **Never delete files you did not create** without confirming with the user.
- **Keep TypeScript strict.** Do not add `any`, `// @ts-ignore`, or disable lint
  rules to make an error go away. Fix the real cause or ask.
- **No new dependencies** without checking `docs/ARCHITECTURE.md` and telling the user.
- **AI output quality is the #1 product risk.** When AI features are added later,
  never ship AI-generated solutions/answers without the verification steps in
  `docs/TESTING.md`.

---

## 5. Conventions

- **Components:** function components, named exports, `"use client"` only when the
  component uses state/effects/browser APIs (e.g. `StudyWorkspace`, `StudyDashboard`).
- **Styling:** CSS Modules (`styles.foo`). Do **not** introduce Tailwind or other
  styling systems without an explicit decision recorded in `docs/ARCHITECTURE.md`.
- **Data/content:** static content goes in `site-data.ts` as typed objects.
- **Images:** use `next/image`, store assets under `public/boostai/`.
- **Imports:** use the `@/` alias (e.g. `@/components/boostai/...`).

---

## 6. Git & deployment

- Feature branches only. Use a clear name (e.g. `feature/add-physics-topic`).
- Commit messages: short, plain English, describe the *what* and *why*.
- Open a Pull Request to `main`. CI (`.github/workflows/ci.yml`) must pass.
- Vercel builds a **preview** for every PR and **production** on merge to `main`.
- See `docs/CICD.md` for the full pipeline.

---

## 7. When to stop and ask the user

Stop and ask (use the question tool) before:
- Editing anything in `public/`.
- Adding a dependency, service, or environment variable.
- Changing auth, payments, or database behaviour.
- Any change you cannot fully verify with the preflight check.
- Deleting or renaming files.

When in doubt, do less and ask. That is always the right call on this project.
