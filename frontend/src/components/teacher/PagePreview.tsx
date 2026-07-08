import { useState } from "react";

interface PagePreviewProps {
  pageNumber: number;
  documentId?: string;
}

const BACKEND_URL = "http://localhost:3001";

export default function PagePreview({ pageNumber, documentId }: PagePreviewProps) {
  const [imageError, setImageError] = useState(false);

  const imageUrl = documentId
    ? `${BACKEND_URL}/api/documents/${documentId}/pages/${pageNumber}`
    : null;

  return (
    <div className="bg-white border border-gray-200 rounded-[16px] overflow-hidden">
      <div className="bg-gray-50 px-5 py-3 border-b border-gray-100 flex items-center justify-between">
        <span className="text-[13px] font-semibold text-gray-700">Page {pageNumber}</span>
        <span className="text-[11px] text-gray-400">Preview</span>
      </div>
      <div className="p-6 flex items-center justify-center min-h-[160px]">
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={`Page ${pageNumber}`}
            className="max-w-full max-h-[600px] object-contain rounded-lg shadow-sm"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="text-center">
            <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.25a1.444 1.444 0 0 0 0 1.5c.368.5.955.833 1.464.833H5.1c.508 0 .985-.334 1.464-.833a1.444 1.444 0 0 0 0-1.5c-.479-.5-.956-.833-1.464-.833H3.5c-.509 0-.896.333-1.464.833ZM15.75 6.75a.75.75 0 0 0-.75.75v6c0 .414.336.75.75.75h.75a.75.75 0 0 0 .75-.75v-6a.75.75 0 0 0-.75-.225h-3.75A2.25 2.25 0 0 0 11.25 9v1.5m0 0v3.75m0-3.75H15" />
              </svg>
            </div>
            <p className="text-[13px] text-gray-400">
              {documentId ? "Page image not available yet" : "Page image will appear here"}
            </p>
            <p className="text-[11px] text-gray-300 mt-1">
              {documentId ? "The pipeline may still be processing" : "once rendering is available"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
