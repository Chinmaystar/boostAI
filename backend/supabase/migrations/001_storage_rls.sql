-- ==========================================================
-- Migration: Secure Supabase Storage for BoostAI
-- 
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor)
-- or via `psql` with the service role connection string.
-- ==========================================================

-- ─── 1. Create / update the documents bucket ───────────────
-- `public = false` ensures the bucket is private.
-- `allowed_mime_types` restricts uploads to PDF only.
-- `file_size_limit = 52428800` caps files at 50 MB.
INSERT INTO storage.buckets (id, name, public, allowed_mime_types, file_size_limit)
VALUES ('documents', 'documents', false, ARRAY['application/pdf'], 52428800)
ON CONFLICT (id) DO UPDATE SET
  public             = false,
  allowed_mime_types = ARRAY['application/pdf'],
  file_size_limit    = 52428800;

-- ─── 2. Enable Row-Level Security on storage.objects ────
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- ─── 3. Drop existing per-user policies (idempotent) ──────
DROP POLICY IF EXISTS "Users can upload their own PDFs" ON storage.objects;
DROP POLICY IF EXISTS "Users can read their own PDFs"   ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own PDFs" ON storage.objects;

-- ─── 4. INSERT policy ──────────────────────────────────────
-- Authenticated users can upload only into their own folder.
-- `(storage.foldername(name))[1]` is the top-level folder of the
-- object path (e.g. "123/abc.pdf" → "123").  We compare it to
-- `auth.uid()::text` so user A cannot write into user B's folder.
-- `storage.extension(name) = 'pdf'` is a defence-in-depth check
-- in addition to the bucket-level `allowed_mime_types`.
CREATE POLICY "Users can upload their own PDFs" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'documents'
  AND (storage.foldername(name))[1] = auth.uid()::text
  AND storage.extension(name) = 'pdf'
);

-- ─── 5. SELECT policy ──────────────────────────────────────
-- Authenticated users can read only files inside their own folder.
CREATE POLICY "Users can read their own PDFs" ON storage.objects
FOR SELECT TO authenticated
USING (
  bucket_id = 'documents'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ─── 6. DELETE policy ──────────────────────────────────────
-- Authenticated users can delete only files inside their own folder.
CREATE POLICY "Users can delete their own PDFs" ON storage.objects
FOR DELETE TO authenticated
USING (
  bucket_id = 'documents'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ═══════════════════════════════════════════════════════════
-- POLICY EXPLANATION
-- ═══════════════════════════════════════════════════════════
--
-- 1. Bucket-level:
--    - `public = false` → objects are not accessible via public URL.
--      Only authenticated users (or signed URLs via service_role) can
--      access files.
--    - `allowed_mime_types = ['application/pdf']` → Supabase rejects
--      any upload whose Content-Type is not application/pdf.
--    - `file_size_limit = 52428800` (50 MB) → Supabase rejects uploads
--      larger than 50 MB at the API gateway level.
--
-- 2. INSERT policy:
--    - `(storage.foldername(name))[1] = auth.uid()::text` forces the
--      top-level folder to equal the user's auth UUID.
--      Example: user UUID "abc-def" can only upload to
--      `documents/abc-def/some-file.pdf`.
--    - `storage.extension(name) = 'pdf'` rejects files without a .pdf
--      extension (additional defence).
--
-- 3. SELECT policy:
--    - Same folder check.  User A cannot list / read files in user B's
--      folder, even if they know the object path.
--
-- 4. DELETE policy:
--    - Same folder check.  User A cannot delete user B's files.
--
-- NOTE: The backend uses `service_role` (SUPABASE_SERVICE_ROLE_KEY) for
-- uploads and deletes, which bypasses ALL RLS policies.  The policies
-- are in place so that when the frontend later uses the user's anon key
-- to interact with Storage directly, the RLS rules apply correctly.
-- ═══════════════════════════════════════════════════════════
