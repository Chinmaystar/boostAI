import { config } from "../config.js";
import fs from "fs";
import path from "path";

const SUPABASE_STORAGE_URL = `${config.SUPABASE_URL.replace(/\/+$/, "")}/storage/v1/object`;
const SUPABASE_MGMT_URL = `${config.SUPABASE_URL.replace(/\/+$/, "")}/storage/v1/bucket`;

function bucketPath(userId: number, fileName: string): string {
  return `${config.SUPABASE_STORAGE_BUCKET}/${userId}/${Date.now()}-${fileName}`;
}

export async function ensureStorageBucket(): Promise<boolean> {
  if (!config.SUPABASE_SERVICE_ROLE_KEY) return false;
  const bucket = config.SUPABASE_STORAGE_BUCKET;

  const listRes = await fetch(SUPABASE_MGMT_URL, {
    headers: {
      Authorization: `Bearer ${config.SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
    },
  });

  if (listRes.ok) {
    const buckets = await listRes.json() as { id: string }[];
    if (buckets.some(b => b.id === bucket)) return true;
  }

  const createRes = await fetch(SUPABASE_MGMT_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: bucket,
      name: bucket,
      public: true,
      allowed_mime_types: ["application/pdf"],
      file_size_limit: 104857600,
    }),
  });

  if (createRes.ok) {
    console.log(`[storage] Bucket "${bucket}" created`);
    return true;
  }

  const errText = await createRes.text().catch(() => "unknown");
  console.warn(`[storage] Failed to create bucket: ${createRes.status} ${errText}`);
  return false;
}

export async function uploadFile(
  buffer: Buffer,
  userId: number,
  fileName: string
): Promise<string> {
  if (config.SUPABASE_SERVICE_ROLE_KEY) {
    const objectPath = bucketPath(userId, fileName);
    const url = `${SUPABASE_STORAGE_URL}/${objectPath}`;

    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.SUPABASE_SERVICE_ROLE_KEY}`,
        "Content-Type": "application/pdf",
        "x-upsert": "true",
      },
      body: new Uint8Array(buffer),
    });

    if (!res.ok) {
      const err = await res.text().catch(() => "unknown");
      console.warn(`[storage] Supabase upload failed (${res.status}): ${err}, falling back to local`);
    } else {
      return `supabase://${objectPath}`;
    }
  }

  const dir = path.join(process.cwd(), "uploads", String(userId));
  fs.mkdirSync(dir, { recursive: true });
  const dest = path.join(dir, `${Date.now()}-${fileName}`);
  fs.writeFileSync(dest, buffer);
  return `local://${dest}`;
}

export async function getFileStream(
  storagePath: string
): Promise<{ buffer: Buffer | null }> {
  if (storagePath.startsWith("supabase://")) {
    const objectPath = storagePath.slice("supabase://".length);
    const url = `${SUPABASE_STORAGE_URL}/${objectPath}`;

    const res = await fetch(url, {
      headers: config.SUPABASE_SERVICE_ROLE_KEY
        ? { Authorization: `Bearer ${config.SUPABASE_SERVICE_ROLE_KEY}` }
        : {},
    });

    if (!res.ok) {
      console.warn(`[storage] Supabase download failed: ${res.status}`);
      return { buffer: null };
    }

    const arrayBuf = await res.arrayBuffer();
    return { buffer: Buffer.from(arrayBuf) };
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
    const objectPath = storagePath.slice("supabase://".length);
    const url = `${SUPABASE_STORAGE_URL}/${objectPath}`;

    const res = await fetch(url, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${config.SUPABASE_SERVICE_ROLE_KEY}` },
    });

    if (!res.ok) {
      console.warn(`[storage] Supabase delete failed: ${res.status}`);
    }
    return;
  }

  const localPath = storagePath.startsWith("local://")
    ? storagePath.slice("local://".length)
    : storagePath;

  try { fs.unlinkSync(localPath); } catch { /* may already be gone */ }
}
