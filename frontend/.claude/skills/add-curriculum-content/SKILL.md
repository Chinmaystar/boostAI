---
name: add-curriculum-content
description: Add or edit BoostAI's structured learning content — exam boards, subjects, topics, subtopics, demo questions, route cards, or landing copy. Use when the user wants to add a subject/topic, change demo questions, or edit on-page text. Keeps content typed, consistent, and in the right place.
---

# Add or edit curriculum / demo content

Content is the product's moat (see the roadmap and `docs/ARCHITECTURE.md`). Today all
content is mock data in `components/boostai/site-data.ts`, organised as typed objects.
Keep it that way: typed, consistent, and separate from layout.

## Steps

1. **Open `components/boostai/site-data.ts`** and find the relevant export
   (e.g. `workspaceExamples`, `routeCards`). Read the `type` definition above it first.

2. **Match the existing shape exactly.** Every new entry must satisfy its TypeScript
   type — fill in every required field. For a new demo question, that means subject,
   level, marks, topic, prompt, full `reasoning` steps, `answer`, and `variants`.

3. **Keep the School structure in mind** (roadmap):
   `Exam Board → Subject → Topic → Subtopic`. When richer content models are added,
   model them as nested typed objects here before any UI consumes them — agree the
   shape with the user first.

4. **Content accuracy is critical.** Wrong answers destroy trust (the #1 product risk
   in `docs/TESTING.md`). For anything academic:
   - double-check the answer and the reasoning are correct;
   - flag to the user that human review is required before it's treated as real
     curriculum content — never present unverified academic content as authoritative.

5. **Do not** put content in the JSX/components or in `public/`. Content lives in
   `site-data.ts`; components render whatever the data provides.

6. **Verify** with the `/preflight` skill (a malformed entry will fail type-check),
   then follow the normal commit/PR flow.

## Never
- Add an entry that doesn't fully match its type.
- Hard-code content into components.
- Mark AI-generated or unverified academic content as authoritative.
