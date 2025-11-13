import { useState } from 'react';
import MarkdownText from './MarkdownText';

interface FlashcardViewModalProps {
  card: {
    id: number;
    front_text: string;
    back_text: string;
    example?: string;
    pronunciation?: string;
  } | null;
  onClose: () => void;
  open?: boolean;
  isFlipped?: boolean;
  onFlip?: () => void;
}

export default function FlashcardViewModal({ card, onClose }: FlashcardViewModalProps) {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleClose = () => {
    setIsFlipped(false);
    onClose();
  };

  if (!card) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" onClick={handleClose}>
      <div className="bg-white p-6 rounded-lg w-full max-w-md relative" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">Quick View</h3>

        <div
          className="min-h-[150px] p-4 rounded-md flex items-center justify-center cursor-pointer transition-colors"
          onClick={() => setIsFlipped(!isFlipped)}
          style={{
            backgroundColor: isFlipped ? '#f0fdf4' : '#eff6ff',
            borderColor: isFlipped ? '#bbf7d0' : '#bfdbfe',
            borderWidth: '2px'
          }}
        >
          <div className="text-xl text-center font-semibold" style={{color: isFlipped ? '#166534' : '#1e40af'}}>
            <MarkdownText>{isFlipped ? card.back_text : card.front_text}</MarkdownText>
          </div>
        </div>

        <p className="text-center text-sm text-gray-500 mt-2">Click on the card to flip it.</p>

        <div className="mt-6 flex justify-end">
          <button 
            onClick={handleClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
