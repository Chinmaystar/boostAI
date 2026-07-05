import fs from "fs";
import { execSync } from "child_process";
import path from "path";
import os from "os";

export function renderPDFPages(filePath: string): string[] {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "pdf-render-"));
  const prefix = path.join(tmpDir, "page");

  execSync(`pdftoppm -png -r 50 "${filePath}" "${prefix}"`, {
    stdio: "pipe",
  });

  const files = fs.readdirSync(tmpDir)
    .filter((f) => f.endsWith(".png"))
    .sort()
    .map((f) => path.join(tmpDir, f));

  if (files.length === 0) {
    fs.rmdirSync(tmpDir);
    throw new Error("pdftoppm produced no output pages");
  }

  return files;
}

export function cleanupRenderFiles(files: string[]): void {
  for (const f of files) {
    try { fs.unlinkSync(f); } catch { /* ignore */ }
  }
  const dir = path.dirname(files[0]);
  try { fs.rmdirSync(dir); } catch { /* ignore */ }
}
