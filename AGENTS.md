# BoostAI — Agent Guide

## Project Overview
AI EdTech platform: upload PDFs, view/annotate them, generate study materials (quiz, flashcards, summary) via LLM.

## Stack
- **Backend**: Hono (Node.js/TypeScript), Drizzle ORM, Supabase (PostgreSQL + pgvector)
- **Frontend**: Vite + React 19 + Tailwind CSS v4, `lucide-react`, GSAP, `react-pdf` + `pdfjs-dist`
- **Vision**: DeepSeek OCR-2 via community demo API (free, API key `"whale"`)

## Dev Servers
- Frontend: `http://localhost:3000` (`npm run dev` in `frontend/`)
- Backend: `http://localhost:3001` (`npm run dev` in `backend/`)

## Directory Layout
```
boostAI/
├── frontend/
│   └── src/pages/univ-app.tsx  ← main workspace (modules, PDF, annotations, right panel)
│   └── src/pages/login.tsx, univ.tsx, landing.tsx
│   └── src/hooks/useAuth.tsx   ← auth context (JWT + user state)
│   └── src/App.tsx             ← routes + AuthProvider
│   └── vite.config.ts
├── backend/
│   └── uploads/                ← per-user PDF storage (auto-created)
│   └── src/db/schema.ts        ← Drizzle schema (users + documents tables)
│   └── src/db/index.ts         ← DB client
│   └── src/routes/auth.ts      ← signup / login / me endpoints
│   └── src/middleware/auth.ts   ← JWT guard middleware
│   └── src/services/providers/deepseekocr.ts
│   └── src/services/documentProcessor.ts
│   └── src/services/vision.ts
│   └── src/routes/documents.ts ← upload(list/file/delete) — all authGuarded
│   └── src/index.ts            ← Hono app entry
│   └── src/config.ts           ← env vars (DB, JWT, vision)
│   └── .env                    ← secrets
│   └── drizzle.config.ts       ← Drizzle Kit config
```

## Auth System
- **DB**: Supabase PostgreSQL via Drizzle ORM. `users` table + `documents` table (id, userId FK, name, pageCount, storagePath, pages JSONB, createdAt).
- **JWT**: Built-in `hono/jwt` (not the separate `@hono/jwt` package) for signing/verifying. `JWT_SECRET` from env.
- **Google OAuth**: Sign In With Google (GIS) popup flow. Uses `jose` on backend to verify Google's RS256 JWT via JWKS endpoint. `POST /api/auth/google` creates or finds user by email.
- **Endpoints**:
  - `POST /api/auth/signup` — create account, return JWT
  - `POST /api/auth/login` — authenticate, return JWT
  - `POST /api/auth/google` — Google OAuth sign-in/sign-up, return JWT
  - `GET /api/auth/me` — validate JWT, return user
- **Document Endpoints** (all authGuarded):
  - `POST /api/documents/upload` — SSE streaming upload, accepts `moduleId` form field, saves PDF to `uploads/{userId}/`, returns `docId` in done event
  - `GET /api/documents/list` — returns orphan docs (no moduleId) `[{id, name, pageCount, createdAt}]`
  - `GET /api/documents/:id/file` — serves stored PDF as `application/pdf`
  - `DELETE /api/documents/:id` — removes from DB + filesystem
- **Module Endpoints** (all authGuarded):
  - `POST /api/modules` — create module `{ name }` → `{ id, name, createdAt }`
  - `GET /api/modules` — list modules with nested `documents` array
  - `PUT /api/modules/:id` — rename module `{ name }`
  - `DELETE /api/modules/:id` — cascade delete: removes all documents (DB + filesystem) + module
- **Frontend**: `useAuth` React context stores JWT in localStorage, automatically validates on mount.
- **Protection**: `univ-app.tsx` guards with redirect to `/login?role=univ` if no valid session.

## Key Architecture

### Workspace (`univ-app.tsx`)
- **Layout**: Sidebar (left) | PDF viewer (center) | Right panel (study tools)
- **Modules**: Persisted on server. `AppModule { id, serverId, name }`. On mount, fetched from `GET /api/modules`. `activeModuleId` persisted to `localStorage` — restored on mount, auto-selects first module if saved ID no longer exists.
- **Documents**: `DocInfo { id, name, loading, pages, localFile? }`. Uploaded via SSE streaming to `POST /api/documents/upload` with `moduleId`. Loading spinner in sidebar during processing. On completion, auto-opens. Uses `URL.createObjectURL(file)` for immediate rendering.
- **PDF Loading**: `pdfLoading` state shows spinner while PDF blob is being fetched from server. Center pane shows doc list from active module (with loading indicators per doc), or "No PDFs" message with upload button.
- **SSE stream reading**: The `while` loop reads chunks with `reader.read()`. CRITICAL: `value` is processed into `buf` BEFORE checking `streamDone`, because the last chunk may carry the final data with `done: true`. If you break before appending `value`, the done event is silently lost.
- **Server docs (orphans)**: Docs without a module. Fetched from `GET /api/documents/list` on mount. Shown in a "Documents" section.
- **Delete doc**: Calls `DELETE /api/documents/:id` on server + removes from state.
- **Long filenames**: Scrollable horizontally without visible scrollbar (`overflow-x-auto whitespace-nowrap scrollbar-none`).
- **PDF rendering**: `react-pdf` with continuous scroll. PDF fetched from server as blob URL or from local File object.
- **Study content**: Q&A, flashcards, and summaries generated on-demand via OpenRouter (DeepSeek chat) API. Page text from OCR is fed to the LLM in **chunks of 2 pages**, results merged. Each chunk wrapped in try/catch — if all chunks fail, throws error so frontend can show Retry.
- **Right panel**: Three modes — tiles (landing), quiz (scrollable Q&A with reveal-answer), flashcards (single-card flip with prev/next), summary (LLM-generated + key points). Each panel has a **tinted header** (purple/green/blue) with a **Regenerate button** (top-right, always visible, spinner while loading). `force` parameter on `ensureStudyContent` bypasses all caches (local state + DB) for fresh generation.
- **Error handling**: `studyError` state per tool type. On generation failure, error message shown in red + Retry button. Stale empty arrays in DB are cleared on failure. `study-content` GET returns 404 for empty arrays.
- **PDF storage**: Files uploaded to Supabase Storage (private bucket) with RLS policies. Downloads use signed URLs (302 redirect) with 1hr expiry; backend proxies as fallback.
- **Study tool tiles**: Disabled (grayed out, `opacity-50`, `cursor-not-allowed`) when no PDF is loaded. Click does nothing.
- **Module picker**: When `activeModuleId` is null but modules exist, center pane shows a clickable module list + "New Module" button.
- **Animations**: `framer-motion` via `AnimatePresence` + `motion.div` — sidebar slide (spring), modal fade+scale (spring), toast slide-down (spring), right panel views cross-fade (150ms), quiz answer reveal fade.
- **CSS note**: `button { background: none; }` was removed from `index.css` — use `border-0` + `bg-*` classes for button styling.

## Conventions
- Tailwind v4 utility classes (no inline styles except for modal buttons)
- No comments in code (unless absolutely necessary)
- `lucide-react` for icons
- Types at top of file

## Build & Verify
- TypeScript check: `npx tsc --noEmit` (run in respective directory)
- Frontend dev: `npm run dev` (port 3000)
- Backend dev: `npm run dev` (port 3001)
- Always run `npx tsc --noEmit` after making changes

## Critical Rules
1. **Make the entire button area clickable** — no dead zones between icon/text/chevron
2. **Annotation state stays in refs during drag** — never call `pushHistory` or `setAnnotations` on mousemove
3. **DO NOT add explanatory comments** to code
4. **DO NOT create documentation files (*.md) unless explicitly asked**
5. **Only commit when explicitly asked** by the user
6. **Answer concisely** — minimal text before/after responses
7. **Keep this file updated** — always update AGENTS.md when you add/modify a major feature, change a convention, or add a dependency
