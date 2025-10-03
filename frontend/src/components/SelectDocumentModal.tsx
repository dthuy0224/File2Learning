import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import AIService, { Document } from '../services/aiService';
import { Button } from './ui/button';
import { Loader2, FileText } from 'lucide-react';

interface SelectDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SelectDocumentModal({ isOpen, onClose }: SelectDocumentModalProps) {
  const navigate = useNavigate();

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => AIService.getDocuments(),
    // Chỉ lấy những document đã xử lý xong
    select: (data: Document[]) => data.filter(doc => doc.processing_status === 'completed')
  });

  const handleSelectDocument = (documentId: number) => {
    onClose();
    navigate(`/documents/${documentId}/quiz`);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-full max-w-lg mx-4">
        <h2 className="text-2xl font-bold mb-4">Create Quiz from a Document</h2>
        <p className="mb-4 text-gray-600">
          Please select a document to generate a quiz from.
        </p>

        <div className="space-y-2 max-h-80 overflow-y-auto">
          {isLoading && (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          )}

          {documents && documents.length > 0 ? (
            documents.map(doc => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 border rounded-md hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => handleSelectDocument(doc.id)}
              >
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.title || doc.original_filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {doc.document_type} • {doc.word_count} words
                    </p>
                  </div>
                </div>
                <div className="text-xs text-gray-400 flex-shrink-0">
                  {new Date(doc.created_at).toLocaleDateString()}
                </div>
              </div>
            ))
          ) : (
            !isLoading && (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-500 mb-4">
                  No completed documents found.
                </p>
                <p className="text-sm text-gray-400">
                  Please upload and process a document first.
                </p>
                <Button
                  className="mt-4"
                  variant="outline"
                  onClick={() => {
                    onClose();
                    navigate('/documents');
                  }}
                >
                  Go to Documents
                </Button>
              </div>
            )
          )}
        </div>

        <div className="mt-6 flex justify-end">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}
