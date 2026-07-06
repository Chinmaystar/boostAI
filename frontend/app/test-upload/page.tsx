"use client";

import { useState, useRef, type FormEvent } from "react";

export default function TestUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [pages, setPages] = useState<{ page: number; text: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setPages([]);
    setDone(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:3001/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "Upload failed" }));
        throw new Error(err.error || "Upload failed");
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;
        buf += decoder.decode(value, { stream: true });

        const lines = buf.split("\n");
        buf = lines.pop() || "";

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.page) {
                setPages((prev) => [...prev, { page: data.page, text: data.text }]);
              }
              if (data.pageCount) {
                setDone(true);
              }
            } catch { /* skip malformed */ }
          }
        }
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 800, margin: "40px auto", padding: "0 20px", fontFamily: "system-ui, sans-serif" }}>
      <h1>PDF Upload Test (SSE streaming)</h1>

      <form onSubmit={handleSubmit}>
        <div
          onClick={() => inputRef.current?.click()}
          style={{
            border: "2px dashed #999",
            borderRadius: 8,
            padding: 40,
            textAlign: "center",
            cursor: "pointer",
            background: file ? "#e8f5e9" : "#fafafa",
            marginBottom: 16,
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            style={{ display: "none" }}
          />
          {file ? (
            <p style={{ fontSize: 16, fontWeight: 600 }}>{file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
          ) : (
            <p style={{ color: "#666" }}>Click to select a PDF file</p>
          )}
        </div>

        <button
          type="submit"
          disabled={!file || loading}
          style={{
            padding: "10px 24px",
            fontSize: 16,
            background: !file || loading ? "#ccc" : "#1976d2",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: !file || loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Processing..." : "Upload & Extract Text"}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 20, padding: 12, background: "#ffebee", borderRadius: 6, color: "#c62828" }}>
          Error: {error}
        </div>
      )}

      {loading && !done && (
        <div style={{ marginTop: 20, color: "#666" }}>
          Processing page {pages.length + 1}...
        </div>
      )}

      {done && (
        <div style={{ marginTop: 20, padding: 8, background: "#e8f5e9", borderRadius: 6, color: "#2e7d32" }}>
          Done — {pages.length} page{pages.length !== 1 ? "s" : ""} extracted
        </div>
      )}

      {pages.map((p, i) => (
        <div key={i} style={{ marginTop: 20 }}>
          <h3>Page {p.page}</h3>
          <pre
            style={{
              background: "#1e1e1e",
              color: "#d4d4d4",
              padding: 16,
              borderRadius: 6,
              overflow: "auto",
              maxHeight: 400,
              fontSize: 13,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {p.text || "(no text extracted)"}
          </pre>
        </div>
      ))}
    </main>
  );
}
