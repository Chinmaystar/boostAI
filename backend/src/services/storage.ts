import { config } from "../config.js";
import fs from "fs";
import path from "path";
import { createRequire } from "module";

const _require = createRequire(import.meta.url);

let firebaseApp: any = null;
let bucket: any = null;

function initFirebase() {
  if (firebaseApp) return true;
  if (!config.FIREBASE_PROJECT_ID || !config.FIREBASE_STORAGE_BUCKET) {
    return false;
  }
  try {
    const admin = _require("firebase-admin");
    firebaseApp = admin.initializeApp({
      credential: admin.credential.cert({
        projectId: config.FIREBASE_PROJECT_ID,
        clientEmail: config.FIREBASE_CLIENT_EMAIL,
        privateKey: (config.FIREBASE_PRIVATE_KEY || "").replace(/\\n/g, "\n"),
      }),
      storageBucket: config.FIREBASE_STORAGE_BUCKET,
    });
    bucket = admin.storage().bucket();
    return true;
  } catch (err) {
    console.warn("[storage] Firebase init failed, falling back to local:", (err as Error).message);
    return false;
  }
}

function getLocalDir(userId: number): string {
  const dir = path.join(process.cwd(), "uploads", String(userId));
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

export async function uploadFile(
  buffer: Buffer,
  userId: number,
  fileName: string
): Promise<string> {
  if (initFirebase()) {
    const dest = `users/${userId}/${Date.now()}-${fileName}`;
    const file = bucket.file(dest);
    await file.save(buffer, {
      metadata: { contentType: "application/pdf" },
    });
    return `firebase://${dest}`;
  }

  const dir = getLocalDir(userId);
  const dest = path.join(dir, `${Date.now()}-${fileName}`);
  fs.writeFileSync(dest, buffer);
  return `local://${dest}`;
}

export function getFilePath(storagePath: string): string {
  if (storagePath.startsWith("local://")) {
    return storagePath.slice("local://".length);
  }
  return storagePath;
}

export async function getFileStream(
  storagePath: string
): Promise<{ stream: fs.ReadStream | null; buffer: Buffer | null }> {
  const localPath = getFilePath(storagePath);

  if (storagePath.startsWith("firebase://")) {
    if (!initFirebase()) {
      throw new Error("Firebase not configured");
    }
    const dest = storagePath.slice("firebase://".length);
    const [contents] = await bucket.file(dest).download();
    return { stream: null, buffer: contents };
  }

  return { stream: null, buffer: fs.readFileSync(localPath) };
}

export async function deleteFile(storagePath: string): Promise<void> {
  if (storagePath.startsWith("firebase://")) {
    if (!initFirebase()) return;
    const dest = storagePath.slice("firebase://".length);
    try {
      await bucket.file(dest).delete();
    } catch { /* may already be gone */ }
    return;
  }

  const localPath = getFilePath(storagePath);
  try { fs.unlinkSync(localPath); } catch { /* may already be gone */ }
}
