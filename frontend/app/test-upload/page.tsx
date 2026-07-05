"use client";

import { useState, useRef, type FormEvent } from "react";

type UploadResult = {
  filename: string;
  pageCount: number;
  method: "pdf-parse" | "gemini";
  text: string;
  tookMs: number;
};

export default function TestUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:3001/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Upload failed");
      }

      const data: UploadResult = await res.json();
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 800, margin: "40px auto", padding: "0 20px", fontFamily: "system-ui, sans-serif" }}>
      <h1>PDF Upload Test</h1>

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

      {result && (
        <div style={{ marginTop: 20 }}>
          <div style={{ display: "flex", gap: 16, marginBottom: 12, flexWrap: "wrap" }}>
            <InfoBadge label="File" value={result.filename} />
            <InfoBadge label="Pages" value={String(result.pageCount)} />
            <InfoBadge label="Method" value={result.method} />
            <InfoBadge label="Time" value={`${result.tookMs}ms`} />
            <InfoBadge label="Text length" value={`${result.text.length} chars`} />
          </div>

          <h3>Extracted Text</h3>
          <pre
            style={{
              background: "#1e1e1e",
              color: "#d4d4d4",
              padding: 16,
              borderRadius: 6,
              overflow: "auto",
              maxHeight: 600,
              fontSize: 13,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {result.text || "(no text extracted)"}
          </pre>
        </div>
      )}
    </main>
  );
}

function InfoBadge({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: "6px 12px", background: "#e3f2fd", borderRadius: 6, fontSize: 14 }}>
      <strong>{label}:</strong> {value}
    </div>
  );
}
