# Architecture

This document describes **what BoostAI Study is today** and **where it is going**,
so changes stay coherent. It is the source of truth for technical decisions.
If you (or Claude) want to do something this document doesn't cover, update this
document first — don't just do it.

---

## 1. Current architecture (the MVP, as of June 2026)

### Stack
- **Framework:** Next.js 15 (App Router) + React 19
- **Language:** TypeScript, `strict: true`
- **Styling:** CSS Modules (one `*.module.css` per component)
- **Hosting:** Vercel, git-based auto-deploy from `main`
- **Fonts/assets:** local, under `public/boostai/`

### Layout
```
app/                      Routing layer (thin — pages just render components or redirect)
  layout.tsx              Root: fonts, <head>, site metadata
  page.tsx                "/"        → HomeLanding
  dashboard/page.tsx      "/dashboard" → StudyDashboard
  study|account/page.tsx  redirect → /dashboard
  university/page.tsx      redirect → /uni
  auth/page.tsx            redirect → /login.html (legacy)
components/boostai/        The real UI
  HomeLanding.tsx          Home / route chooser
  PersonaLanding.tsx       Shared school/uni landing
  StudyWorkspace.tsx       Interactive demo (client component)
  StudyDashboard.tsx       Demo dashboard (client component, reads localStorage)
  site-data.ts             All mock content, typed
  *.module.css             Styles
public/                    ⚠️ LEGACY static HTML + vanilla JS (see §3)
```

### Principle: thin routes, real components
`app/*/page.tsx` files stay tiny — they route and render. All UI and logic live in
`components/`. This keeps routing readable and components testable.

### State of the world
- **No backend.** No database, no API routes.
- **Auth is simulated** via `localStorage` (`boostai-local-session`). Not real.
- **All content is mock data** in `site-data.ts`.
- **No tests, and CI is being introduced** (see `docs/CICD.md`, `docs/TESTING.md`).

---

## 2. The legacy zone (technical debt)

`public/` holds an older, separate implementation of the site as plain HTML + JS
(`login.html`, `school/`, `uni/`, `auth/`, `legacy/`, `assets/*.js`). It includes the
only Supabase auth code that exists, plus duplicated `*-v2`/`*-nb2` bundles of
unclear status.

**Decision:** treat `public/` as **read-only legacy**. New features are built in
React under `app/` + `components/`. Pieces of the legacy site get rewritten in React
as the roadmap reaches them (auth is the first candidate). Do not extend the legacy
stack. See `CLAUDE.md` §2.

---

## 3. Target directory structure (when backend features land)

```
app/
  api/                          Next.js API routes (server-side only — no secrets reach the browser)
    auth/                       Supabase OAuth redirect callbacks
    questions/
      route.ts                  GET /api/questions, POST /api/questions
      generate/route.ts         POST → generate similar questions via OpenAI
    documents/
      upload/route.ts           POST → LlamaParse PDF pipeline
    webhooks/
      stripe/route.ts           Stripe webhook handler → writes subscription status to Postgres
  (pages as today)

lib/                            One typed module per external service
  supabase/
    client.ts                   Browser Supabase client (public anon key only)
    server.ts                   Server Supabase client (service role key — never imported by client components)
  openai/
    index.ts                    All OpenAI calls: generation + embeddings
  stripe/
    index.ts                    Stripe client + subscription helpers
  llamaparse/
    index.ts                    PDF → structured text pipeline

components/boostai/             UI only — never imports from lib/openai, lib/stripe, lib/llamaparse
```

### Boundary rules
- `lib/supabase/server.ts` and all of `lib/openai/`, `lib/stripe/`, `lib/llamaparse/` are **server-only** — imported exclusively by `app/api/` routes or Next.js Server Components.
- `lib/supabase/client.ts` is the only service file the browser ever touches.
- Client components call our `/api/` routes — never external provider APIs directly.

---

## 4. Target architecture (the roadmap — NOT built yet)

This is the direction. Build toward it incrementally; do not assume any of it exists.

- **Frontend:** Next.js 15 + TypeScript. *Roadmap mentions Tailwind + shadcn/ui;*
  *the MVP currently uses CSS Modules. Migrating is a deliberate, separate decision —*
  *record it here before starting, don't mix the two ad hoc.*
- **Backend:** Supabase — PostgreSQL, Auth, Storage, Edge Functions.
- **Auth:** Supabase Auth (Google + email). Replaces the localStorage fake and the
  legacy JS auth.
- **AI:** OpenAI GPT-5 (generation) + OpenAI embeddings (similarity). Use the latest,
  most capable models; centralise all AI calls behind one server-side module.
- **Document processing:** LlamaParse (PDF → structured text).
- **Vector search:** pgvector inside Supabase (no separate vector DB at MVP).
- **Payments:** Stripe (subscriptions, webhook-driven feature gating).

### The core learning loop (the product)
`Question → Solution → Explanation → Generate Similar → Practice → Mastery`
**Generate Similar** is the central feature. Everything else supports it.

### Hard architectural boundaries (apply these as features land)
1. **AI and secrets are server-side only.** API keys never reach the browser. All
   OpenAI / LlamaParse / Stripe calls happen in Supabase Edge Functions or Next.js
   server code. The client calls *our* endpoints, never the providers directly.
2. **AI output is never trusted blindly.** Every solution/explanation goes through
   the verification approach in `docs/TESTING.md` before a student sees it.
3. **Feature gating is driven by subscription status in Postgres**, set by Stripe
   webhooks — never by client-side checks alone.
4. **One module per external service.** Wrap Supabase, OpenAI, Stripe, and LlamaParse
   each behind a single typed module so they can be tested and swapped.

---

## 4. Recording decisions

When a non-trivial technical choice is made (a new library, a styling-system change,
a new service), add a short dated entry below. This is the project's memory.

### Decision log
- **2026-06 — Baseline.** MVP = Next.js + CSS Modules + mock data, no backend.
  Legacy `public/` frozen as read-only. CI + testing strategy introduced.
