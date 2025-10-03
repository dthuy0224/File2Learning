import { useState } from 'react';
import { Button } from './ui/button';
import { Flashcard } from '../services/flashcardService';

interface FlashcardViewModalProps {
  card: Flashcard | null;
  onClose: () => void;
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
          <p className="text-xl text-center font-semibold" style={{color: isFlipped ? '#166534' : '#1e40af'}}>
            {isFlipped ? card.back_text : card.front_text}
          </p>
        </div>

        <p className="text-center text-sm text-gray-500 mt-2">Click on the card to flip it.</p>

        <div className="mt-6 flex justify-end">
          <Button onClick={handleClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}
