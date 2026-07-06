# BoostAI

AI-powered EdTech platform.

## Backend API

**Base URL:** `http://localhost:3001`

### Upload PDF (SSE streaming)

```
POST /api/documents/upload
Content-Type: multipart/form-data
Body: file=<PDF>
```

Returns `text/event-stream` with events:

```
event: page
data: {"page":1,"text":"..."}

event: page
data: {"page":2,"text":"..."}

event: done
data: {"method":"ollama","pageCount":2,"tookMs":738}
```

### Models

- **Ollama** (local): Qwen3-VL 2B via `./backend/.env VISION_PROVIDER=ollama`
- **Gemini** (cloud): via `./backend/.env VISION_PROVIDER=gemini`
- **Vision mode**: Snippet-based — renders only math regions as small images using pdftoppm, sends to VL model. Non-math text uses pdfjs extraction.
