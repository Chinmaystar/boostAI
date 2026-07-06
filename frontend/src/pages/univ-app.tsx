import { useState, useRef, useEffect, useCallback } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";
import {
  Plus, Upload,
  ZoomIn, ZoomOut, Undo2, Redo2, Pen, Highlighter,
  Type, MousePointer2, ArrowLeft, FileText, BookOpen,
  Layers, Trash2, X, FolderPlus
} from "lucide-react";
import logo from "../assets/logo.avif";

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

interface AppModule {
  id: string;
  name: string;
}

const PEN_COLORS = ["#000000", "#2563EB", "#DC2626", "#16A34A", "#9333EA"];
const HIGHLIGHT_COLORS = ["#FEF08A", "#86EFAC", "#93C5FD", "#FDA4AF", "#D8B4FE"];

type Tool = "select" | "pen" | "highlight" | "textbox";
type RightMode = "tiles" | "quiz" | "flashcards" | "summary";

let modIdCounter = 0;
const nextModId = () => `mod_${++modIdCounter}`;

export default function UnivAppPage() {
  /* modules */
  const [modules, setModules] = useState<AppModule[]>([]);
  const [moduleDocs, setModuleDocs] = useState<Record<string, { name: string; file: File }[]>>({});
  const [activeModuleId, setActiveModuleId] = useState<string | null>(null);
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /* pdf */
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [numPages, setNumPages] = useState(0);
  const [zoom, setZoom] = useState(1);
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

  /* right panel */
  const [rightMode, setRightMode] = useState<RightMode>("tiles");

  /* refs */
  const canvasRefs = useRef<Record<number, HTMLCanvasElement | null>>({});
  const uploadRef = useRef<HTMLInputElement>(null);
  const sidebarUploadRef = useRef<HTMLInputElement>(null);
  const pageContainerRef = useRef<HTMLDivElement>(null);
  /* live drawing refs (avoids re-renders during drag) */
  const penPointsRef = useRef<{ x: number; y: number }[]>([]);
  const highlightDragRef = useRef<{ start: { x: number; y: number }; current: { x: number; y: number } } | null>(null);

  /* toolbar positioning */
  const [toolbarLeft, setToolbarLeft] = useState(0);
  const [toolbarWidth, setToolbarWidth] = useState(0);

  useEffect(() => {
    if (!pageContainerRef.current) return;
    const rect = pageContainerRef.current.getBoundingClientRect();
    setToolbarLeft(rect.left);
    setToolbarWidth(rect.width);
  }, [pageSizes, zoom, pdfFile]);

  /* derived */
  const activeModule = modules.find(m => m.id === activeModuleId) || null;
  const activeModuleDocs = activeModuleId ? moduleDocs[activeModuleId] || [] : [];
  const activeDocObj = activeModuleDocs.find(d => d.name === activeDocId) || null;
  const firstSize = Object.values(pageSizes)[0];
  const basePageWidth = firstSize?.width || 600;
  const pdfWidth = basePageWidth * zoom;
  const pageNumbers = Array.from(new Array(numPages), (_, i) => i + 1);

  /* ─── Module CRUD ─── */
  const createModule = () => {
    const name = prompt("Module name:")?.trim();
    if (!name) return;
    const newMod: AppModule = { id: nextModId(), name };
    setModules(prev => [...prev, newMod]);
    setModuleDocs(prev => ({ ...prev, [newMod.id]: [] }));
    setActiveModuleId(newMod.id);
  };

  const deleteModule = (id: string) => {
    if (!confirm("Delete this module and all its documents?")) return;
    setModules(prev => prev.filter(m => m.id !== id));
    setModuleDocs(prev => { const { [id]: _, ...rest } = prev; return rest; });
    if (activeModuleId === id) {
      setActiveModuleId(null);
      setActiveDocId(null);
      setPdfFile(null);
    }
  };

  const uploadDocToModule = (modId: string, file: File) => {
    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed");
      return;
    }
    setModuleDocs(prev => ({
      ...prev,
      [modId]: [...(prev[modId] || []), { name: file.name, file }],
    }));
  };

  const deleteDoc = (modId: string, docName: string) => {
    setModuleDocs(prev => ({
      ...prev,
      [modId]: (prev[modId] || []).filter(d => d.name !== docName),
    }));
    if (activeDocId === docName) {
      setActiveDocId(null);
      setPdfFile(null);
    }
  };

  const openDoc = (modId: string, docName: string) => {
    const docs = moduleDocs[modId] || [];
    const doc = docs.find(d => d.name === docName);
    if (!doc) return;
    setActiveModuleId(modId);
    setActiveDocId(docName);
    setPdfFile(doc.file);
    setZoom(1);
    setPageSizes({});
    setAnnotations([]);
    setHistory([]);
    setHistoryIdx(-1);
    setSidebarOpen(false);
  };

  /* ─── Annotation ─── */
  const pushHistory = useCallback((newAnnotations: Annotation[]) => {
    const cut = history.slice(0, historyIdx + 1);
    cut.push(newAnnotations);
    setHistory(cut);
    setHistoryIdx(cut.length - 1);
    setAnnotations(newAnnotations);
  }, [history, historyIdx]);

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

  useEffect(() => { redrawCanvas(); }, [redrawCanvas]);

  const getCanvasPos = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

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
      {sidebarOpen && (
        <div className="absolute left-0 top-0 bottom-0 w-[320px] bg-white shadow-xl z-50 flex flex-col border-r border-gray-200">
          <div className="flex items-center justify-between p-4 border-b border-gray-100">
            <h2 className="font-bold text-lg text-gray-900">Modules</h2>
            <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-gray-100 rounded-md text-gray-500">
              <ArrowLeft size={18} />
            </button>
          </div>
          <div className="p-3 border-b border-gray-100">
            <button
              onClick={createModule}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors"
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
                      onClick={() => setActiveModuleId(isActive ? null : mod.id)}
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
                            className={`flex-1 flex items-center gap-2 px-3 py-2 text-sm rounded-xl transition-colors ${
                              activeDocId === d.name
                                ? "bg-blue-50 text-blue-700 font-medium"
                                : "text-gray-600 hover:bg-gray-50"
                            }`}
                          >
                            <FileText size={14} />
                            <span className="truncate">{d.name}</span>
                          </button>
                          <button
                            onClick={() => deleteDoc(mod.id, d.name)}
                            className="p-1 hover:bg-red-50 rounded-md text-gray-400 hover:text-red-500"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          setActiveModuleId(mod.id);
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
          </div>
        </div>
      )}

      {/* ─── Left Pane ─── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="flex items-center gap-2 min-w-0 overflow-hidden">
            {/* Module button — opens sidebar */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-1.5 shadow-sm hover:bg-gray-100 active:bg-gray-200 transition-colors text-sm cursor-pointer"
            >
              <img src={logo} alt="BoostAI" className="w-5 h-5 object-contain rounded shrink-0" />
              <span className="font-semibold text-gray-800 max-w-[150px] truncate">
                {activeModule?.name || "Workspace"}
              </span>
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
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 hover:bg-gray-100 rounded-md text-gray-400 hover:text-gray-600"
              title="Browse all modules"
            >
              <BookOpen size={16} />
            </button>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 overflow-auto bg-[#F0F2F5]">
          <div className="flex flex-col items-center p-4 pb-24 min-h-full">
            {pdfFile ? (
              <div ref={pageContainerRef} className="relative" style={{ width: Math.min(pdfWidth + 40, 900) }}>
                <Document file={pdfFile} onLoadSuccess={onDocumentLoad}>
                  <div className="flex flex-col items-center gap-6">
                    {pageNumbers.map(pageNum => {
                      const size = pageSizes[pageNum];
                      return (
                        <div key={pageNum} className="relative shadow-xl rounded-lg overflow-hidden bg-white">
                          <Page
                            pageNumber={pageNum}
                            width={Math.min(basePageWidth, 860) * zoom}
                            onLoadSuccess={onPageLoad(pageNum)}
                            renderTextLayer
                            renderAnnotationLayer
                          />
                          {size && (
                            <canvas
                              ref={el => { canvasRefs.current[pageNum] = el; }}
                              width={size.width * zoom}
                              height={size.height * zoom}
                              className="absolute top-0 left-0 cursor-crosshair"
                              style={{ width: size.width * zoom, height: size.height * zoom }}
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
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-3">
                <FileText size={48} className="text-gray-300" />
                <p className="text-sm">{activeModuleId ? "Upload a PDF to get started" : "Create a module to get started"}</p>
                <button
                  onClick={() => {
                    if (activeModuleId) uploadRef.current?.click();
                    else createModule();
                  }}
                  className="px-4 py-2 bg-blue-600 rounded-xl text-sm font-medium hover:bg-blue-700"
                >
                  {activeModuleId ? "Upload PDF" : "Create Module"}
                </button>
              </div>
            )}
          </div>
        </div>
        {/* Fixed Annotation Toolbar */}
        {pdfFile && (
          <div
            className="fixed bottom-6 z-30"
            style={{
              left: toolbarLeft + toolbarWidth / 2,
              transform: 'translateX(-50%)',
            }}
          >
            <div className="bg-white rounded-full shadow-lg border border-gray-200 px-3 py-2 flex items-center gap-1">
              <button
                onClick={() => setActiveTool("select")}
                className={`p-2 rounded-full transition-colors ${activeTool === "select" ? "bg-blue-100 text-blue-600" : "hover:bg-gray-100 text-gray-600"}`}
                title="Select"
              >
                <MousePointer2 size={16} />
              </button>
              <div className="w-px h-6 bg-gray-200 mx-1" />
              <div className="flex items-center gap-0.5">
                <button
                  onClick={() => setActiveTool(activeTool === "pen" ? "select" : "pen")}
                  className={`p-2 rounded-full transition-colors ${activeTool === "pen" ? "bg-blue-100 text-blue-600" : "hover:bg-gray-100 text-gray-600"}`}
                  title="Pen"
                >
                  <Pen size={16} />
                </button>
                {activeTool === "pen" && (
                  <div className="flex gap-0.5 ml-0.5">
                    {PEN_COLORS.map(c => (
                      <button
                        key={c}
                        onClick={() => setPenColor(c)}
                        className={`w-4 h-4 rounded-full border-2 transition-all ${penColor === c ? "border-gray-800 scale-110" : "border-transparent"}`}
                        style={{ backgroundColor: c }}
                      />
                    ))}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-0.5">
                <button
                  onClick={() => setActiveTool(activeTool === "highlight" ? "select" : "highlight")}
                  className={`p-2 rounded-full transition-colors ${activeTool === "highlight" ? "bg-yellow-100 text-yellow-700" : "hover:bg-gray-100 text-gray-600"}`}
                  title="Highlight"
                >
                  <Highlighter size={16} />
                </button>
                {activeTool === "highlight" && (
                  <div className="flex gap-0.5 ml-0.5">
                    {HIGHLIGHT_COLORS.map(c => (
                      <button
                        key={c}
                        onClick={() => setHighlightColor(c)}
                        className={`w-4 h-4 rounded-full border-2 transition-all ${highlightColor === c ? "border-gray-800 scale-110" : "border-transparent"}`}
                        style={{ backgroundColor: c }}
                      />
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => setActiveTool(activeTool === "textbox" ? "select" : "textbox")}
                className={`p-2 rounded-full transition-colors ${activeTool === "textbox" ? "bg-blue-100 text-blue-600" : "hover:bg-gray-100 text-gray-600"}`}
                title="Text box"
              >
                <Type size={16} />
              </button>
              <div className="w-px h-6 bg-gray-200 mx-1" />
              <button onClick={() => setZoom(z => Math.max(0.5, z - 0.1))} className="p-2 hover:bg-gray-100 rounded-full text-gray-600" title="Zoom out">
                <ZoomOut size={16} />
              </button>
              <span className="text-xs font-medium text-gray-600 w-10 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom(z => Math.min(3, z + 0.1))} className="p-2 hover:bg-gray-100 rounded-full text-gray-600" title="Zoom in">
                <ZoomIn size={16} />
              </button>
              <div className="w-px h-6 bg-gray-200 mx-1" />
              <button onClick={undo} disabled={historyIdx < 0} className="p-2 hover:bg-gray-100 rounded-full text-gray-600 disabled:opacity-30" title="Undo">
                <Undo2 size={16} />
              </button>
              <button onClick={redo} disabled={historyIdx >= history.length - 1} className="p-2 hover:bg-gray-100 rounded-full text-gray-600 disabled:opacity-30" title="Redo">
                <Redo2 size={16} />
              </button>
              <button
                onClick={() => { setAnnotations([]); setHistory([]); setHistoryIdx(-1); }}
                className="p-2 hover:bg-red-50 rounded-full text-gray-500 hover:text-red-500 ml-1"
                title="Clear all annotations"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ─── Right Panel ─── */}
      <div className="w-[400px] bg-white border-l border-gray-200 flex flex-col overflow-hidden">
        {rightMode === "tiles" ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8">
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Study Tools</p>
            <button
              onClick={() => setRightMode("quiz")}
              className="w-full flex items-center gap-4 p-5 bg-gradient-to-br from-purple-50 to-purple-100/50 rounded-2xl border border-purple-200 hover:shadow-md transition-shadow group"
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
              onClick={() => setRightMode("flashcards")}
              className="w-full flex items-center gap-4 p-5 bg-gradient-to-br from-green-50 to-green-100/50 rounded-2xl border border-green-200 hover:shadow-md transition-shadow group"
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
              onClick={() => setRightMode("summary")}
              className="w-full flex items-center gap-4 p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl border border-blue-200 hover:shadow-md transition-shadow group"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <FileText size={24} className="text-blue-600" />
              </div>
              <div className="text-left">
                <p className="font-bold text-gray-900 text-lg">Summary</p>
                <p className="text-sm text-gray-500">Key points overview</p>
              </div>
            </button>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            <div className="flex items-center gap-2 p-4 border-b border-gray-100">
              <button onClick={() => setRightMode("tiles")} className="p-1 hover:bg-gray-100 rounded-md text-gray-500">
                <ArrowLeft size={18} />
              </button>
              <span className="font-semibold text-gray-800 capitalize">
                {rightMode === "quiz" ? "Quiz" : rightMode === "flashcards" ? "Flashcards" : "Summary"}
              </span>
            </div>
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
              Content coming soon
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
