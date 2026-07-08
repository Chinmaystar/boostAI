import { useState, useRef, useEffect } from 'react';
import type { ExtractedQuestion } from '../../mocks/extractionReview';
import QuestionStatusBadge from './QuestionStatusBadge';

interface QuestionCardProps {
  question: ExtractedQuestion;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onSaveEdit: (id: string, text: string) => void;
  onResetStatus: (id: string) => void;
  onDuplicate: (id: string) => void;
}

export default function QuestionCard({
  question,
  onApprove,
  onReject,
  onSaveEdit,
  onResetStatus,
  onDuplicate,
}: QuestionCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(question.editedText ?? question.text);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(editText.length, editText.length);
    }
  }, [isEditing, editText.length]);

  useEffect(() => {
    setEditText(question.editedText ?? question.text);
  }, [question.id, question.text, question.editedText]);

  const handleEditToggle = () => {
    if (isEditing) {
      if (editText !== question.text) {
        onSaveEdit(question.id, editText);
      }
      setIsEditing(false);
    } else {
      setEditText(question.editedText ?? question.text);
      setIsEditing(true);
    }
  };

  const handleCancelEdit = () => {
    setEditText(question.editedText ?? question.text);
    setIsEditing(false);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-[16px] overflow-hidden transition-shadow hover:shadow-sm">
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 bg-blue-50 text-blue-700 rounded-[10px] flex items-center justify-center text-[14px] font-bold">
            {question.questionNumber}
          </span>
          <div className="flex items-center gap-2">
            <QuestionStatusBadge status={question.status} />
            {question.type && (
              <span className="text-[12px] text-gray-400 font-medium capitalize">
                {question.type.replace('-', ' ')}
              </span>
            )}
            {question.hasDiagram && (
              <span className="flex items-center gap-1 text-[12px] text-gray-400 font-medium">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                </svg>
                Diagram
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="px-5 py-4">
        <textarea
          ref={textareaRef}
          value={isEditing ? editText : (question.editedText ?? question.text)}
          readOnly={!isEditing}
          onChange={(e) => setEditText(e.target.value)}
          className={`w-full resize-none bg-transparent text-[15px] leading-relaxed text-gray-900 outline-none ${
            isEditing ? 'border border-blue-300 rounded-[10px] p-3 bg-blue-50/30 min-h-[80px]' : 'border-none p-0 min-h-[24px]'
          } ${question.status === 'rejected' ? 'text-gray-400 line-through' : ''}`}
          rows={isEditing ? 3 : 1}
        />
      </div>

      <div className="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          {question.status !== 'approved' && (
            <button
              onClick={() => onApprove(question.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-[8px] text-[13px] font-semibold transition-colors"
              title="Approve"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
              Approve
            </button>
          )}
          {question.status !== 'rejected' && (
            <button
              onClick={() => onReject(question.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-[8px] text-[13px] font-semibold transition-colors"
              title="Reject"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
              Reject
            </button>
          )}
          {question.status !== 'rejected' && (isEditing ? (
            <>
              <button
                onClick={handleEditToggle}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-[8px] text-[13px] font-semibold transition-colors"
                title="Save edit"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-[8px] text-[13px] font-semibold transition-colors"
                title="Cancel"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              onClick={handleEditToggle}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-[8px] text-[13px] font-semibold transition-colors"
              title="Edit"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
              </svg>
              Edit
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5">
          {(question.status !== 'pending' && !isEditing) && (
            <button
              onClick={() => onResetStatus(question.id)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-gray-400 hover:text-gray-600 rounded-[8px] text-[13px] font-semibold transition-colors"
              title="Reset to pending"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
              </svg>
              Reset
            </button>
          )}
          <button
            onClick={() => onDuplicate(question.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-gray-400 hover:text-gray-600 rounded-[8px] text-[13px] font-semibold transition-colors"
            title="Duplicate"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
            </svg>
            Duplicate
          </button>
        </div>
      </div>
    </div>
  );
}
