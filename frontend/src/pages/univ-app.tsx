import { useState, useRef, useEffect, useCallback } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";
import { AnimatePresence, motion } from "framer-motion";
import {
  Plus, Upload,
  ArrowLeft, FileText, BookOpen,
  Layers, X, FolderPlus, LogOut, Loader2, Trash2, ChevronDown, RefreshCw
} from "lucide-react";
import logo from "../assets/logo.avif";
import { useAuth } from "../hooks/useAuth";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

/* ─── Types ─── */
interface PenAnnotation {
  page: number;
  type: "pen";
  color: string;
  points: { x: number; y: number }[];
}
interface HighlightAnnotation {
  page: number;
  type: "highlight";
  color: string;
  x: number; y: number; width: number; height: number;
}
interface TextboxAnnotation {
  page: number;
  type: "textbox";
  x: number; y: number; text: string; fontSize: number;
}
type Annotation = PenAnnotation | HighlightAnnotation | TextboxAnnotation;

interface DocInfo {
  id: number | null;
  name: string;
  loading: boolean;
  pages: { page: number; text: string }[];
  localFile?: File;
}

interface AppModule {
  id: string;
  serverId: number;
  name: string;
}

interface QAItem {
  questionNumber: number;
  question: string;
  answer: string;
  type: string;
}
interface Flashcard {
  front: string;
  back: string;
}
interface SummaryResult {
  summary: string;
  keyPoints: string[];
}
interface StudyContent {
  quiz: QAItem[];
  flashcards: Flashcard[];
  summary: SummaryResult | null;
}

const PEN_COLORS = ["#000000", "#2563EB", "#DC2626", "#16A34A", "#9333EA"];
const HIGHLIGHT_COLORS = ["#FEF08A", "#86EFAC", "#93C5FD", "#FDA4AF", "#D8B4FE"];

type Tool = "select" | "pen" | "highlight" | "textbox";
type RightMode = "tiles" | "quiz" | "flashcards" | "summary";

export default function UnivAppPage() {
  const { user, loading, logout } = useAuth();

  /* modules */
  const [modules, setModules] = useState<AppModule[]>([]);
  const [moduleDocs, setModuleDocs] = useState<Record<string, DocInfo[]>>({});
  const [activeModuleId, setActiveModuleId_] = useState<string | null>(null);
  const setActiveModId = useCallback((id: string | null) => {
    setActiveModuleId_(id);
    if (id) localStorage.setItem("activeModuleId", id);
    else localStorage.removeItem("activeModuleId");
  }, []);
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /* server docs */
  const [serverDocs, setServerDocs] = useState<DocInfo[]>([]);

  /* pdf */
  const [pdfFile, setPdfFile] = useState<File | string | null>(null);
  const [numPages, setNumPages] = useState(0);
  const [pageSizes, setPageSizes] = useState<Record<number, { width: number; height: number }>>({});

  /* annotation */
  const [activeTool, setActiveTool] = useState<Tool>("select");
  const [penColor, setPenColor] = useState(PEN_COLORS[0]);
  const [highlightColor, setHighlightColor] = useState(HIGHLIGHT_COLORS[0]);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [history, setHistory] = useState<Annotation[][]>([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawPage, setDrawPage] = useState(0);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [textboxInput, setTextboxInput] = useState("");
  const [textboxPos, setTextboxPos] = useState<{ x: number; y: number } | null>(null);
  const [textboxPage, setTextboxPage] = useState(0);

  /* toast */
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  /* pdf loading */
  const [pdfLoading, setPdfLoading] = useState(false);

  /* right panel */
  const [rightMode, setRightMode] = useState<RightMode>("tiles");
  const [studyContent, setStudyContent] = useState<Record<string, StudyContent>>({});
  const [generatingType, setGeneratingType] = useState<string | null>(null);
  const [studyError, setStudyError] = useState<Record<string, string | null>>({});
  const [flashcardIdx, setFlashcardIdx] = useState(0);

  /* module name input */
  const [moduleInputOpen, setModuleInputOpen] = useState(false);
  const [moduleInput, setModuleInput] = useState("");

  /* refs */
  const canvasRefs = useRef<Record<number, HTMLCanvasElement | null>>({});
  const uploadRef = useRef<HTMLInputElement>(null);
  const sidebarUploadRef = useRef<HTMLInputElement>(null);
  const pageContainerRef = useRef<HTMLDivElement>(null);
  /* live drawing refs (avoids re-renders during drag) */
  const penPointsRef = useRef<{ x: number; y: number }[]>([]);
  const highlightDragRef = useRef<{ start: { x: number; y: number }; current: { x: number; y: number } } | null>(null);

  /* ─── Annotation helpers (non-hooks, safe to reference from hooks) ─── */
  const drawAnnotationOnCtx = (ctx: CanvasRenderingContext2D, a: Annotation) => {
    if (a.type === "pen") {
      ctx.beginPath();
      ctx.strokeStyle = a.color;
      ctx.lineWidth = 2;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      for (let i = 0; i < a.points.length; i++) {
        if (i === 0) ctx.moveTo(a.points[i].x, a.points[i].y);
        else ctx.lineTo(a.points[i].x, a.points[i].y);
      }
      ctx.stroke();
    } else if (a.type === "highlight") {
      ctx.fillStyle = a.color + "66";
      ctx.fillRect(a.x, a.y, a.width, a.height);
    } else if (a.type === "textbox") {
      ctx.fillStyle = "#000";
      ctx.font = `${a.fontSize}px sans-serif`;
      ctx.fillText(a.text, a.x, a.y + a.fontSize);
    }
  };

  /* ─── Annotation hooks ─── */
  const pushHistory = useCallback((newAnnotations: Annotation[]) => {
    const cut = history.slice(0, historyIdx + 1);
    cut.push(newAnnotations);
    setHistory(cut);
    setHistoryIdx(cut.length - 1);
    setAnnotations(newAnnotations);
  }, [history, historyIdx]);

  const redrawCanvas = useCallback(() => {
    const pages = new Set(annotations.map(a => a.page));
    for (const page of pages) {
      const cvs = canvasRefs.current[page];
      if (!cvs) continue;
      const ctx = cvs.getContext("2d");
      if (!ctx) continue;
      ctx.clearRect(0, 0, cvs.width, cvs.height);
    }
    for (const a of annotations) {
      const cvs = canvasRefs.current[a.page];
      if (!cvs) continue;
      const ctx = cvs.getContext("2d");
      if (!ctx) continue;
      drawAnnotationOnCtx(ctx, a);
    }
  }, [annotations, pageSizes]);

  const redrawPage = useCallback((pageNum: number) => {
    const cvs = canvasRefs.current[pageNum];
    if (!cvs) return;
    const ctx = cvs.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, cvs.width, cvs.height);
    for (const a of annotations) {
      if (a.page !== pageNum) continue;
      drawAnnotationOnCtx(ctx, a);
    }
  }, [annotations, pageSizes]);

  useEffect(() => {
    if (!loading && !user) {
      window.location.href = "/login?role=univ";
    }
  }, [user, loading]);

  useEffect(() => { redrawCanvas(); }, [redrawCanvas]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch("http://localhost:3001/api/modules", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then((mods: any[]) => {
        setModules(mods.map(m => ({ id: String(m.id), serverId: m.id, name: m.name })));
        const docsMap: Record<string, DocInfo[]> = {};
        for (const mod of mods) {
          docsMap[String(mod.id)] = (mod.documents || []).map((d: any) => ({
            id: d.id,
            name: d.name,
            loading: false,
            pages: [],
          }));
        }
        setModuleDocs(docsMap);
        const savedId = localStorage.getItem("activeModuleId");
        if (savedId && mods.some(m => String(m.id) === savedId)) {
          setActiveModId(savedId);
        } else if (mods.length > 0) {
          setActiveModId(String(mods[0].id));
        }
      })
      .catch(console.error);

    fetch("http://localhost:3001/api/documents/list", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(docs => {
        setServerDocs(docs.map((d: any) => ({
          id: d.id,
          name: d.name,
          loading: false,
          pages: [],
        })));
      })
      .catch(console.error);
  }, []);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#F3F8FB]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-gray-500 font-medium">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  /* derived */
  const activeModule = modules.find(m => m.id === activeModuleId) || null;
  const activeModuleDocs = activeModuleId ? moduleDocs[activeModuleId] || [] : [];
  const activeDocObj = activeModuleDocs.find(d => d.name === activeDocId) || null;
  const firstSize = Object.values(pageSizes)[0];
  const basePageWidth = firstSize?.width || 600;
  const pageNumbers = Array.from(new Array(numPages), (_, i) => i + 1);

  /* ─── Module CRUD ─── */
  const createModule = async () => {
    setModuleInputOpen(true);
    setModuleInput("");
  };

  const submitModule = async () => {
    const name = moduleInput.trim();
    if (!name) { setModuleInputOpen(false); return; }
    setModuleInputOpen(false);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch("http://localhost:3001/api/modules", {
        method: "POST",
        headers: token ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` } : { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to create module");
      const newMod: AppModule = { id: String(data.id), serverId: data.id, name: data.name };
      setModules(prev => [...prev, newMod]);
      setModuleDocs(prev => ({ ...prev, [newMod.id]: [] }));
      setActiveModId(newMod.id);
    } catch (err) {
      alert("Failed to create module: " + (err as Error).message);
    }
  };

  const deleteModule = async (id: string) => {
    if (!confirm("Delete this module and all its documents?")) return;
    const mod = modules.find(m => m.id === id);
    if (mod) {
      const token = localStorage.getItem("token");
      try {
        await fetch(`http://localhost:3001/api/modules/${mod.serverId}`, {
          method: "DELETE",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
      } catch { /* ignore */ }
    }
    setModules(prev => prev.filter(m => m.id !== id));
    setModuleDocs(prev => { const { [id]: _, ...rest } = prev; return rest; });
    if (activeModuleId === id) {
      setActiveModId(null);
      setActiveDocId(null);
      setPdfFile(null);
    }
  };

  const uploadDocToModule = async (modId: string, file: File) => {
    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed");
      return;
    }

    const docName = file.name;
    const fileUrl = URL.createObjectURL(file);
    const newDoc: DocInfo = { id: null, name: docName, loading: true, pages: [], localFile: file };
    setModuleDocs(prev => ({
      ...prev,
      [modId]: [...(prev[modId] || []), newDoc],
    }));

    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", file);
    const mod = modules.find(m => m.id === modId);
    if (mod) {
      formData.append("moduleId", String(mod.serverId));
    }

    try {
      const res = await fetch("http://localhost:3001/api/documents/upload", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
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
        if (value) buf += decoder.decode(value, { stream: true });
        if (streamDone) break;

        const lines = buf.split("\n");
        buf = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.page) {
                console.log(data);
                setModuleDocs(prev => ({
                  ...prev,
                  [modId]: (prev[modId] || []).map(d =>
                    d.name === docName ? { ...d, pages: [...d.pages, data] } : d
                  ),
                }));
              }
              if (data.id != null) {
                setModuleDocs(prev => ({
                  ...prev,
                  [modId]: (prev[modId] || []).map(d =>
                    d.name === docName ? { ...d, id: data.id, loading: false } : d
                  ),
                }));
                setActiveModId(modId);
                setActiveDocId(docName);
                setPdfFile(fileUrl);
                setPageSizes({});
                setAnnotations([]);
                setHistory([]);
                setHistoryIdx(-1);
                setSidebarOpen(false);
                setToast({ message: "Processing done", type: "success" });
                setTimeout(() => setToast(null), 4000);
              }
            } catch { /* skip malformed */ }
          }
        }
      }
    } catch (err) {
      console.error("Upload failed:", err);
      setModuleDocs(prev => ({
        ...prev,
        [modId]: (prev[modId] || []).filter(d => d.name !== docName),
      }));
      alert("Upload failed: " + (err as Error).message);
    }
  };

  const deleteDoc = async (modId: string, docName: string) => {
    const token = localStorage.getItem("token");
    let doc: DocInfo | undefined;
    if (modId === "__server__") {
      doc = serverDocs.find(d => d.name === docName);
    } else {
      doc = (moduleDocs[modId] || []).find(d => d.name === docName);
    }

    setModuleDocs(prev => ({
      ...prev,
      [modId]: (prev[modId] || []).filter(d => d.name !== docName),
    }));
    setServerDocs(prev => prev.filter(d => d.name !== docName));
    if (activeDocId === docName) {
      setActiveDocId(null);
      setPdfFile(null);
    }

    if (doc?.id != null) {
      fetch(`http://localhost:3001/api/documents/${doc.id}`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }).catch(() => {});
    }
  };

  const openDoc = async (modId: string, docName: string) => {
    const docs = (modId === "__server__" ? serverDocs : moduleDocs[modId]) || [];
    const doc = docs.find(d => d.name === docName);
    if (!doc) return;
    setActiveModId(modId);
    setActiveDocId(docName);

    if (doc.localFile) {
      setPdfFile(doc.localFile);
    } else if (doc.id != null) {
      setPdfLoading(true);
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`http://localhost:3001/api/documents/${doc.id}/file`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok) {
          const blob = await res.blob();
          setPdfFile(URL.createObjectURL(blob));
        }
      } catch { /* fall through */ }
      setPdfLoading(false);
    }

    setPageSizes({});
    setAnnotations([]);
    setHistory([]);
    setHistoryIdx(-1);
    setSidebarOpen(false);
  };

  /* ─── Study content ─── */
  const ensureStudyContent = async (type: "quiz" | "flashcards" | "summary", force?: boolean) => {
    if (!activeDocObj || activeDocObj.id == null) return;
    const docId = activeDocObj.id;
    const docName = activeDocObj.name;

    if (!force && studyContent[docName]?.[type] && (type !== "summary" || studyContent[docName].summary)) {
      const existing = studyContent[docName][type];
      if (Array.isArray(existing) && existing.length === 0) {
        /* empty array from a previous failed run — regenerate */
      } else {
        return;
      }
    }

    setGeneratingType(type);
    setStudyError(prev => ({ ...prev, [type]: null }));
    const token = localStorage.getItem("token");
    try {
      if (!force) {
        let res = await fetch(
          `http://localhost:3001/api/documents/${docId}/study-content?type=${type}`,
          { headers: token ? { Authorization: `Bearer ${token}` } : {} }
        );
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data.content) && data.content.length === 0) {
            /* stale empty array in DB — fall through to generate */
          } else {
            setStudyContent(prev => ({
              ...prev,
              [docName]: { ...prev[docName], [type]: data.content },
            }));
            setGeneratingType(null);
            return;
          }
        }
      }

      /* Not cached — generate */
      const res = await fetch(
        `http://localhost:3001/api/documents/${docId}/generate?type=${type}`,
        { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error(`Generation failed (${res.status})`);
      const data = await res.json();
      setStudyContent(prev => ({
        ...prev,
        [docName]: { ...prev[docName], [type]: data.content },
      }));
    } catch (err) {
      console.error("Study content error:", err);
      setStudyError(prev => ({ ...prev, [type]: (err as Error).message }));
    } finally {
      setGeneratingType(null);
    }
  };

  /* ─── Annotation ─── */
  const undo = () => {
    if (historyIdx < 0) return;
    const prev = history[historyIdx - 1] || [];
    setAnnotations(prev);
    setHistoryIdx(historyIdx - 1);
  };
  const redo = () => {
    if (historyIdx >= history.length - 1) return;
    const next = history[historyIdx + 1];
    setAnnotations(next);
    setHistoryIdx(historyIdx + 1);
  };

  const getCanvasPos = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const handleCanvasDown = (pageNum: number) => (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!pdfFile) return;
    const pos = getCanvasPos(e);
    if (activeTool === "textbox") {
      setTextboxPage(pageNum);
      setTextboxPos(pos);
      setTextboxInput("");
      return;
    }
    setIsDrawing(true);
    setDrawPage(pageNum);
    setDrawStart(pos);
    if (activeTool === "pen") {
      penPointsRef.current = [pos];
      const cvs = canvasRefs.current[pageNum];
      if (!cvs) return;
      const ctx = cvs.getContext("2d");
      if (!ctx) return;
      ctx.beginPath();
      ctx.strokeStyle = penColor;
      ctx.lineWidth = 2;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.moveTo(pos.x, pos.y);
    } else if (activeTool === "highlight") {
      highlightDragRef.current = { start: pos, current: pos };
    }
  };

  const handleCanvasMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !pdfFile) return;
    const pos = getCanvasPos(e);
    if (activeTool === "pen") {
      penPointsRef.current.push(pos);
      const cvs = canvasRefs.current[drawPage];
      if (!cvs) return;
      const ctx = cvs.getContext("2d");
      if (!ctx) return;
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
    } else if (activeTool === "highlight" && drawStart && highlightDragRef.current) {
      highlightDragRef.current.current = pos;
      const cvs = canvasRefs.current[drawPage];
      if (!cvs) return;
      const ctx = cvs.getContext("2d");
      if (!ctx) return;
      redrawPage(drawPage);
      const x = Math.min(drawStart.x, pos.x);
      const y = Math.min(drawStart.y, pos.y);
      const w = Math.abs(pos.x - drawStart.x);
      const h = Math.abs(pos.y - drawStart.y);
      ctx.fillStyle = highlightColor + "66";
      ctx.fillRect(x, y, w, h);
    }
  };

  const handleCanvasUp = () => {
    if (!isDrawing || !pdfFile) return;
    setIsDrawing(false);
    const page = drawPage;
    if (activeTool === "pen") {
      const pts = penPointsRef.current;
      penPointsRef.current = [];
      if (pts.length > 1) {
        pushHistory([...annotations, { page, type: "pen", color: penColor, points: pts }]);
      } else {
        redrawCanvas();
      }
    } else if (activeTool === "highlight" && drawStart) {
      const end = highlightDragRef.current?.current || drawStart;
      const w = Math.abs(end.x - drawStart.x);
      const h = Math.abs(end.y - drawStart.y);
      highlightDragRef.current = null;
      if (w > 3 || h > 3) {
        pushHistory([...annotations, {
          page, type: "highlight", color: highlightColor,
          x: Math.min(drawStart.x, end.x),
          y: Math.min(drawStart.y, end.y),
          width: w, height: h,
        }]);
      } else {
        redrawCanvas();
      }
    }
    setDrawStart(null);
    setDrawPage(0);
  };

  const submitTextbox = () => {
    if (!textboxInput.trim() || !textboxPos) return;
    pushHistory([...annotations, { page: textboxPage, type: "textbox", x: textboxPos.x, y: textboxPos.y, text: textboxInput, fontSize: 16 }]);
    setTextboxPos(null);
    setTextboxInput("");
    setTextboxPage(0);
  };

  const onDocumentLoad = ({ numPages }: { numPages: number }) => setNumPages(numPages);
  const onPageLoad = (pageNum: number) => ({ width, height }: { width: number; height: number }) => {
    setPageSizes(prev => ({ ...prev, [pageNum]: { width, height } }));
  };

  return (
    <div className="flex h-screen bg-[#F3F8FB] overflow-hidden font-sans relative">
      {/* ─── Sidebar ─── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="absolute left-0 top-0 bottom-0 w-[320px] bg-white shadow-xl z-50 flex flex-col border-r border-gray-200"
          >
          <div className="flex items-center justify-between p-4 border-b border-gray-100">
            <h2 className="font-bold text-lg text-gray-900">Modules</h2>
            <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-gray-100 rounded-md text-gray-500">
              <ArrowLeft size={18} />
            </button>
          </div>
          <div className="p-3 border-b border-gray-100">
            <button
              onClick={createModule}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors border-0"
            >
              <FolderPlus size={16} /> New Module
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {modules.length === 0 && (
              <p className="text-sm text-gray-400 text-center py-8">No modules yet. Create one to get started.</p>
            )}
            {modules.map(mod => {
              const isActive = activeModuleId === mod.id;
              const docs = moduleDocs[mod.id] || [];
              return (
                <div key={mod.id}>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setActiveModId(isActive ? null : mod.id)}
                      className={`flex-1 flex items-center gap-2 px-3 py-2.5 text-sm font-semibold rounded-xl transition-colors ${
                        isActive ? "bg-blue-50 text-blue-700" : "text-gray-800 hover:bg-gray-50"
                      }`}
                    >
                      <BookOpen size={16} className={isActive ? "text-blue-600" : "text-gray-400"} />
                      {mod.name}
                    </button>
                    <button
                      onClick={() => deleteModule(mod.id)}
                      className="p-1.5 hover:bg-red-50 rounded-md text-gray-400 hover:text-red-500"
                      title="Delete module"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  {isActive && (
                    <div className="ml-6 space-y-0.5 mb-1 mt-1">
                      {docs.length === 0 && (
                        <p className="text-xs text-gray-400 px-3 py-1">No documents</p>
                      )}
                      {docs.map(d => (
                        <div key={d.name} className="flex items-center gap-1">
                          <button
                            onClick={() => openDoc(mod.id, d.name)}
                            className={`flex-1 min-w-0 flex items-center gap-2 px-3 py-2 text-sm rounded-xl transition-colors ${
                              activeDocId === d.name
                                ? "bg-blue-50 text-blue-700 font-medium"
                                : "text-gray-600 hover:bg-gray-50"
                            }`}
                          >
                            <FileText size={14} />
                            <span className="truncate">{d.name}</span>
                          </button>
                          {d.loading && (
                            <Loader2 size={12} className="animate-spin text-blue-500" />
                          )}
                          {!d.loading && (
                            <button
                              onClick={() => deleteDoc(mod.id, d.name)}
                              className="p-1 hover:bg-red-50 rounded-md text-gray-400 hover:text-red-500"
                            >
                              <X size={12} />
                            </button>
                          )}
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          setActiveModId(mod.id);
                          sidebarUploadRef.current?.click();
                        }}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Upload size={12} /> Upload PDF
                      </button>
                      <input
                        ref={sidebarUploadRef}
                        type="file"
                        accept=".pdf,application/pdf"
                        className="hidden"
                        onChange={e => {
                          const f = e.target.files?.[0];
                          if (f) uploadDocToModule(mod.id, f);
                          e.target.value = "";
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
            {serverDocs.length > 0 && (
              <div className="pt-3 border-t border-gray-100 mt-3">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">Documents</h3>
                {serverDocs.map(d => (
                  <div key={d.name} className="flex items-center gap-1 mb-0.5">
                    <button
                      onClick={() => openDoc("__server__", d.name)}
                      className={`flex-1 min-w-0 flex items-center gap-2 px-3 py-2 text-sm rounded-xl transition-colors ${
                        activeDocId === d.name
                          ? "bg-blue-50 text-blue-700 font-medium"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      <FileText size={14} />
                      <span className="truncate">{d.name}</span>
                    </button>
                    <button
                      onClick={() => deleteDoc("__server__", d.name)}
                      className="p-1 hover:bg-red-50 rounded-md text-gray-400 hover:text-red-500"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      )}
      </AnimatePresence>

      <AnimatePresence>
        {moduleInputOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/20"
            onClick={() => setModuleInputOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ type: "spring", damping: 20, stiffness: 300 }}
              className="bg-white rounded-2xl shadow-xl p-5 w-80 border border-gray-200"
              onClick={e => e.stopPropagation()}
            >
              <p className="text-sm font-semibold text-gray-800 mb-3">Module name</p>
              <input
                autoFocus
                value={moduleInput}
                onChange={e => setModuleInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") submitModule(); if (e.key === "Escape") setModuleInputOpen(false); }}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                placeholder="e.g. Calculus II"
              />
              <div className="flex justify-center gap-3 mt-4">
                <button onClick={() => setModuleInputOpen(false)} style={{ backgroundColor: "#fef2f2", color: "#dc2626", padding: "8px 20px", fontSize: "14px", fontWeight: 600, borderRadius: "9999px", border: "none", cursor: "pointer" }}>Cancel</button>
                <button onClick={submitModule} style={{ backgroundColor: "#eff6ff", color: "#2563eb", padding: "8px 20px", fontSize: "14px", fontWeight: 600, borderRadius: "9999px", border: "none", cursor: "pointer" }}>Create</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-2.5 bg-green-500 text-white rounded-full shadow-lg text-sm font-medium"
          >
            <span>{toast.message}</span>
            <button onClick={() => setToast(null)} className="p-0.5 hover:bg-white/20 rounded-full">
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ─── Left Pane ─── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="flex items-center gap-2 min-w-0">
            {/* Module button — opens sidebar */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm hover:bg-gray-100 active:bg-gray-200 transition-colors text-sm cursor-pointer"
            >
              <img src={logo} alt="BoostAI" className="w-5 h-5 object-contain rounded shrink-0" />
              <span className="font-semibold text-gray-800 max-w-[180px] truncate">
                {activeModule?.name ? `Module - ${activeModule.name}` : "Select Module"}
              </span>
              <ChevronDown size={14} className="text-gray-400 shrink-0" />
            </button>

            <input ref={uploadRef} type="file" accept=".pdf,application/pdf" className="hidden"
              onChange={e => {
                const f = e.target.files?.[0];
                if (f && activeModuleId) uploadDocToModule(activeModuleId, f);
                e.target.value = "";
              }} />

            {!activeModule && (
              <button
                onClick={createModule}
                className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg border border-dashed border-blue-200 transition-colors"
              >
                <Plus size={14} /> New
              </button>
            )}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 font-medium hidden sm:block truncate max-w-[120px]">
              {user.email}
            </span>
            <button
              onClick={logout}
              className="p-1.5 hover:bg-red-50 rounded-md text-gray-400 hover:text-red-500"
              title="Log out"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 overflow-auto bg-sky-50">
          <div className="flex flex-col items-center p-4 pb-24 min-h-full">
            {pdfLoading ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-3 text-gray-400">
                <Loader2 size={28} className="animate-spin" />
                <span className="text-sm">Loading PDF...</span>
              </div>
            ) : pdfFile ? (
              <div ref={pageContainerRef} className="relative" style={{ width: Math.min(basePageWidth + 40, 900) }}>
                <Document file={pdfFile} onLoadSuccess={onDocumentLoad}>
                  <div className="flex flex-col items-center gap-6">
                    {pageNumbers.map(pageNum => {
                      const size = pageSizes[pageNum];
                      return (
                        <div key={pageNum} className="relative shadow-xl rounded-lg overflow-hidden bg-white">
                          <Page
                            pageNumber={pageNum}
                            width={Math.min(basePageWidth, 860)}
                            onLoadSuccess={onPageLoad(pageNum)}
                            renderTextLayer
                            renderAnnotationLayer
                          />
                          {size && (
                            <canvas
                              ref={el => { canvasRefs.current[pageNum] = el; }}
                              width={size.width}
                              height={size.height}
                              className="absolute top-0 left-0 cursor-crosshair"
                              style={{ width: size.width, height: size.height }}
                              onMouseDown={handleCanvasDown(pageNum)}
                              onMouseMove={handleCanvasMove}
                              onMouseUp={handleCanvasUp}
                              onMouseLeave={handleCanvasUp}
                            />
                          )}
                          {textboxPage === pageNum && textboxPos && (
                            <input
                              autoFocus
                              value={textboxInput}
                              onChange={e => setTextboxInput(e.target.value)}
                              onKeyDown={e => { if (e.key === "Enter") submitTextbox(); if (e.key === "Escape") setTextboxPos(null); }}
                              onBlur={submitTextbox}
                              className="absolute z-30 border border-blue-500 rounded px-1 py-0.5 text-sm bg-white shadow-lg outline-none"
                              style={{ left: textboxPos.x, top: textboxPos.y, minWidth: 80 }}
                              placeholder="Type here..."
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </Document>
              </div>
            ) : modules.length > 0 && !activeModuleId ? (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-4">
                <BookOpen size={48} className="text-gray-300" />
                <p className="text-sm font-medium text-gray-500">Select a Module</p>
                <div className="flex flex-col gap-2 w-64">
                  {modules.map(mod => (
                    <button
                      key={mod.id}
                      onClick={() => setActiveModId(mod.id)}
                      className="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-800 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-colors shadow-sm"
                    >
                      <BookOpen size={16} className="text-gray-400 shrink-0" />
                      <span className="truncate">{mod.name}</span>
                    </button>
                  ))}
                </div>
                <button
                  onClick={createModule}
                  className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg border border-dashed border-blue-200 transition-colors"
                >
                  <Plus size={14} /> New Module
                </button>
              </div>
            ) : activeModuleId ? (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-4">
                <FileText size={48} className="text-gray-300" />
                <p className="text-sm font-medium text-gray-500">{activeModule?.name || "Module"}</p>
                {activeModuleDocs.length === 0 ? (
                  <>
                    <p className="text-xs text-gray-400">No PDFs in this module</p>
                    <button
                      onClick={() => { uploadRef.current?.click(); }}
                      className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors border-0"
                    >
                      <Upload size={14} /> Upload PDF
                    </button>
                  </>
                ) : (
                  <div className="flex flex-col gap-2 w-72">
                    {activeModuleDocs.map(d => (
                      <button
                        key={d.name}
                        onClick={() => openDoc(activeModuleId, d.name)}
                        className="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-800 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-colors shadow-sm"
                      >
                        <FileText size={16} className="text-gray-400 shrink-0" />
                        <span className="truncate">{d.name}</span>
                        {d.loading && <Loader2 size={12} className="animate-spin text-blue-500 shrink-0" />}
                      </button>
                    ))}
                  </div>
                )}
                <button
                  onClick={() => uploadRef.current?.click()}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg border border-dashed border-blue-200 transition-colors"
                >
                  <Plus size={12} /> Upload another PDF
                </button>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-3">
                <FileText size={48} className="text-gray-300" />
                <p className="text-sm">{activeModuleId ? "Upload a PDF to get started" : "Create a module to get started"}</p>
                <button
                  onClick={() => {
                    if (activeModuleId) uploadRef.current?.click();
                    else createModule();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors border-0"
                >
                  {activeModuleId ? "Upload PDF" : "Create Module"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── Right Panel ─── */}
      <div className="w-[400px] bg-white border-l border-gray-200 flex flex-col overflow-hidden">
        {rightMode === "tiles" ? (
          <motion.div
            key="tiles"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="flex-1 flex flex-col items-center justify-center gap-4 p-8"
          >
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Study Tools</p>
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">for this pdf only</div>
            <button
              onClick={() => { if (!activeDocObj) return; setRightMode("quiz"); setFlashcardIdx(0); ensureStudyContent("quiz"); }}
              className={`w-full flex items-center gap-4 p-5 rounded-2xl border transition-shadow group ${
                !activeDocObj
                  ? "bg-gray-50 border-gray-200 opacity-50 cursor-not-allowed"
                  : "bg-gradient-to-br from-purple-50 to-purple-100/50 border-purple-200 hover:shadow-md"
              }`}
            >
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Layers size={24} className="text-purple-600" />
              </div>
              <div className="text-left">
                <p className="font-bold text-gray-900 text-lg">Quiz</p>
                <p className="text-sm text-gray-500">Test your knowledge</p>
              </div>
            </button>
            <button
              onClick={() => { if (!activeDocObj) return; setRightMode("flashcards"); setFlashcardIdx(0); ensureStudyContent("flashcards"); }}
              className={`w-full flex items-center gap-4 p-5 rounded-2xl border transition-shadow group ${
                !activeDocObj
                  ? "bg-gray-50 border-gray-200 opacity-50 cursor-not-allowed"
                  : "bg-gradient-to-br from-green-50 to-green-100/50 border-green-200 hover:shadow-md"
              }`}
            >
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <Layers size={24} className="text-green-600" />
              </div>
              <div className="text-left">
                <p className="font-bold text-gray-900 text-lg">Flashcards</p>
                <p className="text-sm text-gray-500">Review with cards</p>
              </div>
            </button>
            <button
              onClick={() => { if (!activeDocObj) return; setRightMode("summary"); ensureStudyContent("summary"); }}
              className={`w-full flex items-center gap-4 p-5 rounded-2xl border transition-shadow group ${
                !activeDocObj
                  ? "bg-gray-50 border-gray-200 opacity-50 cursor-not-allowed"
                  : "bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200 hover:shadow-md"
              }`}
            >
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <FileText size={24} className="text-blue-600" />
              </div>
              <div className="text-left">
                <p className="font-bold text-gray-900 text-lg">Summary</p>
                <p className="text-sm text-gray-500">Key points overview</p>
              </div>
            </button>
          </motion.div>
        ) : (
          <div className="flex-1 flex flex-col min-h-0">
            <div className={`flex items-center gap-2 p-4 border-b ${
              rightMode === "quiz" ? "bg-purple-50/60 border-purple-100" :
              rightMode === "flashcards" ? "bg-green-50/60 border-green-100" :
              "bg-blue-50/60 border-blue-100"
            }`}>
              <button onClick={() => setRightMode("tiles")} className={`p-1 hover:bg-black/5 rounded-md ${
                rightMode === "quiz" ? "text-purple-500" :
                rightMode === "flashcards" ? "text-green-500" :
                "text-blue-500"
              }`}>
                <ArrowLeft size={18} />
              </button>
              <span className={`font-semibold capitalize flex-1 ${
                rightMode === "quiz" ? "text-purple-800" :
                rightMode === "flashcards" ? "text-green-800" :
                "text-blue-800"
              }`}>
                {rightMode === "quiz" ? "Quiz" : rightMode === "flashcards" ? "Flashcards" : "Summary"}
              </span>
              <button
                onClick={() => ensureStudyContent(rightMode as "quiz" | "flashcards" | "summary", true)}
                disabled={generatingType === rightMode}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-colors ${
                  rightMode === "quiz"
                    ? "text-purple-700 border-purple-200 hover:bg-purple-100 disabled:opacity-40"
                    : rightMode === "flashcards"
                    ? "text-green-700 border-green-200 hover:bg-green-100 disabled:opacity-40"
                    : "text-blue-700 border-blue-200 hover:bg-blue-100 disabled:opacity-40"
                }`}
              >
                <RefreshCw size={13} className={generatingType === rightMode ? "animate-spin" : ""} />
                {generatingType === rightMode ? "Generating..." : "Regenerate"}
              </button>
            </div>
            <div className="flex-1 overflow-y-auto min-h-0">
              <AnimatePresence mode="wait">
                {rightMode === "quiz" && (
                  <motion.div key="quiz" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.15 }}>
                    <QuizPanel
                      items={activeDocObj ? studyContent[activeDocObj.name]?.quiz || null : null}
                      loading={generatingType === "quiz"}
                      error={studyError.quiz || null}
                      onGenerate={() => ensureStudyContent("quiz")}
                    />
                  </motion.div>
                )}
                {rightMode === "flashcards" && (
                  <motion.div key="flashcards" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.15 }}>
                    <FlashcardsPanel
                      items={activeDocObj ? studyContent[activeDocObj.name]?.flashcards || null : null}
                      loading={generatingType === "flashcards"}
                      error={studyError.flashcards || null}
                      onGenerate={() => ensureStudyContent("flashcards")}
                      idx={flashcardIdx}
                      setIdx={setFlashcardIdx}
                    />
                  </motion.div>
                )}
                {rightMode === "summary" && (
                  <motion.div key="summary" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.15 }}>
                    <SummaryPanel
                      data={activeDocObj ? studyContent[activeDocObj.name]?.summary || null : null}
                      pages={activeDocObj?.pages || null}
                      loading={generatingType === "summary"}
                      error={studyError.summary || null}
                      onGenerate={() => ensureStudyContent("summary")}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Sub-components ─── */

function QuizPanel({ items, loading, error, onGenerate }: {
  items: QAItem[] | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
}) {
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-400">
        <Loader2 size={24} className="animate-spin" />
        <span className="text-sm">Generating quiz questions...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <p className="text-sm text-red-500 text-center max-w-[280px]">{error}</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-purple-600 text-white rounded-xl text-sm font-semibold hover:bg-purple-700 transition-colors border-0">
          Retry
        </button>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-gray-400">
        <p className="text-sm">No questions yet</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-purple-600 text-white rounded-xl text-sm font-semibold hover:bg-purple-700 transition-colors border-0">
          Generate Quiz
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {items.map(q => (
        <div key={q.questionNumber} className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
          <div className="flex items-start justify-between gap-2 mb-2">
            <span className="text-xs font-semibold text-gray-400 shrink-0">Q{q.questionNumber}</span>
            <span className="text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 shrink-0">{q.type}</span>
          </div>
          <p className="text-sm font-medium text-gray-900 mb-3">{q.question}</p>
          <button
            onClick={() => setRevealed(p => ({ ...p, [q.questionNumber]: !p[q.questionNumber] }))}
            className="text-xs font-semibold text-purple-600 hover:text-purple-700 transition-colors"
          >
            {revealed[q.questionNumber] ? "Hide answer" : "Show answer"}
          </button>
          <AnimatePresence>
            {revealed[q.questionNumber] && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.15 }}
                className="mt-3 pt-3 border-t border-gray-100"
              >
                <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{q.answer}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}

function FlashcardsPanel({ items, loading, error, onGenerate, idx, setIdx }: {
  items: Flashcard[] | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
  idx: number;
  setIdx: (v: number) => void;
}) {
  const [flipped, setFlipped] = useState(false);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-400">
        <Loader2 size={24} className="animate-spin" />
        <span className="text-sm">Generating flashcards...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <p className="text-sm text-red-500 text-center max-w-[280px]">{error}</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-semibold hover:bg-green-700 transition-colors border-0">
          Retry
        </button>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-gray-400">
        <p className="text-sm">No flashcards yet</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-semibold hover:bg-green-700 transition-colors border-0">
          Generate Flashcards
        </button>
      </div>
    );
  }

  const card = items[idx];

  return (
    <div className="flex flex-col items-center justify-center gap-4 p-4">
      <div className="flex items-center gap-2 text-xs text-gray-400 font-medium">
        <button
          onClick={() => { setIdx(Math.max(0, idx - 1)); setFlipped(false); }}
          disabled={idx === 0}
          className="p-1.5 hover:bg-gray-100 rounded-md disabled:opacity-30 transition-colors"
        >
          <ArrowLeft size={16} />
        </button>
        <span>{idx + 1} / {items.length}</span>
        <button
          onClick={() => { setIdx(Math.min(items.length - 1, idx + 1)); setFlipped(false); }}
          disabled={idx === items.length - 1}
          className="p-1.5 hover:bg-gray-100 rounded-md disabled:opacity-30 transition-colors"
        >
          <ArrowLeft size={16} className="rotate-180" />
        </button>
      </div>

      <div
        onClick={() => setFlipped(!flipped)}
        className="w-full min-h-[260px] cursor-pointer perspective-1000"
      >
        <div className={`relative w-full min-h-[260px] transition-transform duration-500 [transform-style:preserve-3d] ${flipped ? "[transform:rotateY(180deg)]" : ""}`}>
          <div className="absolute inset-0 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col items-center justify-center [backface-visibility:hidden]">
            <p className="text-sm font-medium text-gray-900 text-center leading-relaxed">{card.front}</p>
            <p className="mt-4 text-xs text-gray-400">Tap to flip</p>
          </div>
          <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-green-100/50 border border-green-200 rounded-2xl p-6 shadow-sm flex flex-col items-center justify-center [transform:rotateY(180deg)] [backface-visibility:hidden]">
            <p className="text-sm text-gray-700 text-center leading-relaxed whitespace-pre-wrap">{card.back}</p>
            <p className="mt-4 text-xs text-gray-400">Tap to flip back</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryPanel({ data, pages, loading, error, onGenerate }: {
  data: SummaryResult | null;
  pages: { page: number; text: string }[] | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
}) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-400">
        <Loader2 size={24} className="animate-spin" />
        <span className="text-sm">Generating summary...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <p className="text-sm text-red-500 text-center max-w-[280px]">{error}</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors border-0">
          Retry
        </button>
      </div>
    );
  }

  if (!data && (!pages || pages.length === 0)) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-gray-400">
        <p className="text-sm">No content to summarize</p>
        <button onClick={onGenerate} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors border-0">
          Generate Summary
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {data ? (
        <>
          <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{data.summary}</p>
          </div>
          {data.keyPoints.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-1">Key Points</h4>
              <ul className="space-y-1.5">
                {data.keyPoints.map((kp, i) => (
                  <li key={i} className="flex items-start gap-2 px-1">
                    <span className="text-blue-500 mt-0.5 shrink-0">•</span>
                    <span className="text-sm text-gray-700">{kp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      ) : (
        pages && pages.map(p => (
          <div key={p.page} className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Page {p.page}</h4>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{p.text}</p>
          </div>
        ))
      )}
    </div>
  );
}
