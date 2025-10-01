import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import FlashcardService from '../services/flashcardService';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

// Quality rating levels corresponding to 'quality' score (0-5) for SM-2 algorithm
const QUALITY_LEVELS = [
  { label: 'Forgot', value: 0, color: 'bg-red-500' },
  { label: 'Hard', value: 3, color: 'bg-yellow-500' },
  { label: 'Easy', value: 5, color: 'bg-green-500' },
];

export default function FlashcardReviewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  // 1. Get list of cards that need review
  const { data: dueCards, isLoading, isError } = useQuery({
    queryKey: ['dueFlashcards'],
    queryFn: () => FlashcardService.getDueFlashcards(50),
  });

  // 2. Mutation to send review results to backend
  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: number; quality: number }) =>
      FlashcardService.reviewFlashcard(cardId, { quality }),
    onSuccess: () => {
      // Move to next card
      if (dueCards && currentCardIndex < dueCards.length - 1) {
        setCurrentCardIndex(prev => prev + 1);
        setIsFlipped(false);
      } else {
        // Complete review session
        setCurrentCardIndex(prev => prev + 1);
        toast.success('Review session completed!');
        queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      }
    },
    onError: () => {
        toast.error('Failed to review card.');
    }
  });

  const handleReview = (quality: number) => {
    if (dueCards) {
      const cardId = dueCards[currentCardIndex].id;
      reviewMutation.mutate({ cardId, quality });
    }
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (isError) {
    return <div className="text-center">Could not load the review session. Please try again.</div>;
  }

  // When there are no cards to review or session is completed
  if (!dueCards || dueCards.length === 0 || currentCardIndex >= dueCards.length) {
    return (
      <div className="text-center max-w-md mx-auto">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold">All done for now!</h2>
        <p className="text-gray-600 mt-2">You have reviewed all due cards. Come back later for more.</p>
        <Button className="mt-6" onClick={() => navigate('/flashcards')}>Back to Flashcards</Button>
      </div>
    );
  }

  const currentCard = dueCards[currentCardIndex];

  return (
    <div className="max-w-2xl mx-auto">
        <Button variant="ghost" onClick={() => navigate('/flashcards')} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
      <h1 className="text-2xl font-bold mb-2 text-center">Review Session</h1>
      <p className="text-center text-gray-500 mb-4">Card {currentCardIndex + 1} of {dueCards.length}</p>

      {/* Flashcard with flip effect */}
      <div
          className="relative h-64 cursor-pointer [transform-style:preserve-3d] transition-transform duration-500"
          style={{ transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {/* Front side */}
          <div className="absolute w-full h-full p-6 rounded-lg bg-blue-100 border-2 border-blue-300 flex items-center justify-center [backface-visibility:hidden]">
            <p className="text-2xl font-semibold text-blue-800 text-center">{currentCard.front_text}</p>
          </div>
          {/* Back side */}
          <div className="absolute w-full h-full p-6 rounded-lg bg-green-100 border-2 border-green-300 flex flex-col items-center justify-center [backface-visibility:hidden] [transform:rotateY(180deg)]">
            <p className="text-xl font-medium text-green-800 text-center">{currentCard.back_text}</p>
          </div>
        </div>

      {/* Rating buttons only show when card is flipped */}
      {isFlipped && (
        <div className="mt-6">
          <p className="text-center mb-4 font-medium">How well did you remember this?</p>
          <div className="grid grid-cols-3 gap-4">
            {QUALITY_LEVELS.map(level => (
              <Button
                key={level.value}
                className={`${level.color} hover:opacity-90 text-white font-bold`}
                onClick={() => handleReview(level.value)}
                disabled={reviewMutation.isPending}
              >
                {reviewMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin"/> : level.label}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
