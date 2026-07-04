# Testing Strategy

Goal: catch mistakes **before** they reach production, with a setup a non-technical
developer can run with one command via Claude Code. Right-sized for an MVP — we add
depth as the product grows, not all at once.

---

## The layers (cheapest and fastest first)

### Layer 0 — Types & Lint (active now)
- **TypeScript `strict`** catches most mistakes as you type.
- **ESLint** (Next.js config) catches bad patterns.
- Run with: `npm run verify` (or the `/preflight` skill).
- **Rule:** never silence an error with `any` / `@ts-ignore` / disabled lint rules.
  Fix the cause or ask.

### Layer 1 — Component tests (add as logic appears)
- **Tools:** Vitest + React Testing Library.
- **What to test:** components with behaviour — start with `StudyWorkspace`
  (tab switching, "Generate similar" cycling, "Show me how" reveal) and
  `StudyDashboard` (session reading, greeting, name-from-email).
- **What NOT to test:** static markup and styling. Test behaviour, not pixels.
- Example cases for `StudyWorkspace`:
  - switching subject tabs resets the variant and hides the answer;
  - "Generate similar" cycles through variants and loops back;
  - "Show me how" reveals the answer text.

### Layer 2 — End-to-end smoke tests (add before real users)
- **Tool:** Playwright.
- **Critical paths only:** home loads → choose School/Uni route works → login page
  reachable → dashboard renders. Keep this small and fast.

### Layer 3 — AI output verification (the most important layer, for the roadmap)
**AI output quality is the #1 product risk: a wrong solution destroys trust instantly.**
When AI features (Generate Similar, solutions, extraction) are built, every response
must pass these steps before a student ever sees it:

#### Step 1 — Schema check (automated, happens in the API route)
The AI must return structured JSON. The API route validates the response against a
TypeScript type before using it. If validation fails, the request fails — nothing
broken is ever passed to the UI. Example shape:
```ts
type AIQuestion = {
  prompt: string;
  answer: string;
  reasoning: string[]; // must have at least one step
  marks: number;
};
```

#### Step 2 — Self-check prompt (automated, happens server-side)
After generating a question or solution, a second prompt asks the model:
> "Is the answer above correct? If not, return the corrected version."

Use the same JSON schema. Replace the original output with the corrected version if
the model flags an error. This catches obvious mistakes cheaply without a human.

#### Step 3 — Golden set regression (run before any prompt or model change)
Maintain a small fixed file (`lib/openai/golden-set.json`) of ~10 questions with
known-correct answers across the subjects in the demo. Before merging any change to
an AI prompt or model version, run these questions through the live API and manually
check each answer is still correct. This takes about 5 minutes and catches regressions.

#### Step 4 — Human review before content becomes permanent
Any AI-generated question added to the curriculum (not just shown once) must be
reviewed by a human before it is saved. The UI should make this obvious — e.g. an
"unreviewed" badge and no option to use the question in a session until it is approved.

#### Never
- Show a student an answer that failed Step 1 or Step 2. Fail closed — show an error instead.
- Auto-publish AI content to the curriculum without Step 4.
- Skip the golden set check when changing a prompt or upgrading the model.

---

## Risk tiers — how much testing a feature needs

Not every feature needs the same level of testing. Use this table to decide.

| Tier | What it covers | Required tests |
|---|---|---|
| **High** | Auth, payments, subscriptions, AI output, anything that handles user data | Component tests for every behaviour + Playwright end-to-end smoke test of the critical path + AI evaluation (if AI output is involved) |
| **Medium** | New interactive UI (tabs, forms, state, localStorage), new API routes | Component tests for the core behaviours (happy path + one failure case) |
| **Low** | Copy changes, styling, static layout, new landing page content | Preflight only (`/preflight`) — no additional tests needed |

**When in doubt, go one tier higher.** It is always cheaper to catch a bug in a test
than to fix it after a real user hits it.

---

## How a non-technical developer runs tests

- **Before every commit:** `/preflight` (or `npm run verify`). This is the line of
  defence that always runs.
- **Writing tests:** ask Claude Code — "add a component test for X" — and review that
  the test actually describes the behaviour you want.
- **In CI:** every Pull Request runs lint + types + build (and tests, once added)
  automatically. A red check means *do not merge.* See `docs/CICD.md`.

---

## Rollout order (don't do it all at once)
1. ✅ Types + lint + build via `npm run verify` and CI.
2. Component tests for the two interactive components.
3. Playwright smoke test of the 4 critical paths.
4. AI evaluation harness — built **together with** the first AI feature, never after.
