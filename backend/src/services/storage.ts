import { config } from "../config.js";
import { createClient } from "@supabase/supabase-js";
import fs from "fs";
import path from "path";

let supabase: ReturnType<typeof createClient> | null = null;
function getClient() {
  if (!supabase) {
    supabase = createClient(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY);
  }
  return supabase;
}

const FALLBACK_BUCKETS = ["documents", "pdfs"];

function bucketsToTry(): string[] {
  const primary = config.SUPABASE_STORAGE_BUCKET;
  return Array.from(new Set([primary, ...FALLBACK_BUCKETS.filter(b => b !== primary)]));
}

function storagePath(userId: number, docId?: number): string {
  const prefix = `${userId}/`;
  if (docId) return `${prefix}${docId}.pdf`;
  return `${prefix}${Date.now()}.pdf`;
}

export async function ensureStorageBucket(): Promise<boolean> {
  if (!config.SUPABASE_SERVICE_ROLE_KEY) return false;
  const client = getClient();
  const bucket = config.SUPABASE_STORAGE_BUCKET;

  const { data: existing, error: listErr } = await client.storage.getBucket(bucket);
  if (existing) return true;
  if (listErr && !listErr.message.includes("not found")) {
    console.warn(`[storage] getBucket error: ${listErr.message}`);
  }

  const { error: createErr } = await client.storage.createBucket(bucket, {
    public: false,
    allowedMimeTypes: ["application/pdf"],
    fileSizeLimit: 52428800,
  });

  if (createErr) {
    console.warn(`[storage] Failed to create bucket: ${createErr.message}`);
    return false;
  }

  console.log(`[storage] Bucket "${bucket}" created`);
  return true;
}

export async function uploadFile(
  buffer: Buffer,
  userId: number,
  fileName: string,
  docId?: number
): Promise<string> {
  if (config.SUPABASE_SERVICE_ROLE_KEY) {
    const filePath = storagePath(userId, docId);
    const client = getClient();

    const { error } = await client.storage
      .from(config.SUPABASE_STORAGE_BUCKET)
      .upload(filePath, buffer, {
        contentType: "application/pdf",
        upsert: true,
      });

    if (error) {
      console.warn(`[storage] Supabase upload failed (${error.message}), falling back to local`);
    } else {
      return `supabase://${filePath}`;
    }
  }

  const dir = path.join(process.cwd(), "uploads", String(userId));
  fs.mkdirSync(dir, { recursive: true });
  const dest = path.join(dir, `${Date.now()}-${fileName}`);
  fs.writeFileSync(dest, buffer);
  return `local://${dest}`;
}

export async function getSignedUrl(
  storagePath: string,
  expiresIn: number = 3600
): Promise<string | null> {
  if (!storagePath.startsWith("supabase://")) return null;
  if (!config.SUPABASE_SERVICE_ROLE_KEY) return null;

  const filePath = storagePath.slice("supabase://".length);
  const client = getClient();

  for (const bucket of bucketsToTry()) {
    const { data, error } = await client.storage
      .from(bucket)
      .createSignedUrl(filePath, expiresIn);

    if (error || !data) {
      console.warn(`[storage] Signed URL error in "${bucket}": ${error?.message}`);
      continue;
    }

    return data.signedUrl;
  }

  return null;
}

export async function getFileStream(
  storagePath: string
): Promise<{ buffer: Buffer | null }> {
  if (storagePath.startsWith("supabase://")) {
    const filePath = storagePath.slice("supabase://".length);
    const client = getClient();

    for (const bucket of bucketsToTry()) {
      const { data, error } = await client.storage
        .from(bucket)
        .download(filePath);

      if (error || !data) {
        console.warn(`[storage] Supabase download failed in "${bucket}": ${error?.message}`);
        continue;
      }

      const arrayBuf = await data.arrayBuffer();
      return { buffer: Buffer.from(arrayBuf) };
    }

    return { buffer: null };
  }

  const localPath = storagePath.startsWith("local://")
    ? storagePath.slice("local://".length)
    : storagePath;

  if (!fs.existsSync(localPath)) return { buffer: null };
  return { buffer: fs.readFileSync(localPath) };
}

export async function deleteFile(storagePath: string): Promise<void> {
  if (storagePath.startsWith("supabase://")) {
    if (!config.SUPABASE_SERVICE_ROLE_KEY) return;
    const filePath = storagePath.slice("supabase://".length);
    const client = getClient();

    for (const bucket of bucketsToTry()) {
      const { error } = await client.storage
        .from(bucket)
        .remove([filePath]);

      if (!error) return;
      console.warn(`[storage] Supabase delete failed in "${bucket}": ${error.message}`);
    }
    return;
  }

  const localPath = storagePath.startsWith("local://")
    ? storagePath.slice("local://".length)
    : storagePath;

  try { fs.unlinkSync(localPath); } catch { /* may already be gone */ }
}
