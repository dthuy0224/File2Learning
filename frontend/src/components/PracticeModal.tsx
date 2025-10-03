import { useState, useMemo } from 'react';
import { Button } from './ui/button';
import { Flashcard } from '../services/flashcardService';

// Hàm helper để trộn mảng
const shuffleArray = (array: any[]) => [...array].sort(() => Math.random() - 0.5);

interface PracticeModalProps {
  card: Flashcard | null;
  allCards: Flashcard[];
  onClose: () => void;
}

export default function PracticeModal({ card, allCards, onClose }: PracticeModalProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  // Tạo câu hỏi và các lựa chọn
  const { question, options } = useMemo(() => {
    if (!card) return { question: '', options: [] };

    const questionText = `Which word means: "${card.back_text}"?`;

    // Lấy 3 đáp án sai ngẫu nhiên
    const otherOptions = allCards
      .filter(c => c.id !== card.id)
      .map(c => c.front_text);

    const wrongAnswers = shuffleArray(otherOptions).slice(0, 3);
    const allOptions = shuffleArray([card.front_text, ...wrongAnswers]);

    return { question: questionText, options: allOptions };
  }, [card, allCards]);

  const handleCheckAnswer = () => {
    if (selectedAnswer === card?.front_text) {
      setIsCorrect(true);
    } else {
      setIsCorrect(false);
    }
  };

  if (!card) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-full max-w-lg mx-4">
        <h2 className="text-xl font-bold mb-4">Practice</h2>
        <p className="mb-4">{question}</p>

        <div className="space-y-2">
          {options.map(option => (
            <Button
              key={option}
              variant={selectedAnswer === option ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => { setSelectedAnswer(option); setIsCorrect(null); }}
            >
              {option}
            </Button>
          ))}
        </div>

        {isCorrect !== null && (
            <p className={`mt-4 font-bold ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
                {isCorrect ? 'Correct!' : `Wrong! The correct answer is: ${card.front_text}`}
            </p>
        )}

        <div className="mt-6 flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Close</Button>
          <Button onClick={handleCheckAnswer} disabled={!selectedAnswer}>Check Answer</Button>
        </div>
      </div>
    </div>
  );
}
