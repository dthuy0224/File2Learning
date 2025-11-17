import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import FlashcardService from '../services/flashcardService';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Loader2, ArrowLeft, CheckCircle, Keyboard } from 'lucide-react';
import toast from 'react-hot-toast';
import MarkdownText from '../components/MarkdownText';
import { invalidateProgressQueries } from '@/utils/progressInvalidation';

// Quality rating levels corresponding to 'quality' score (0-5) for SM-2 algorithm
const QUALITY_LEVELS = [
  { label: 'Again', value: 0, color: 'bg-red-500', shortcut: '1' },
  { label: 'Hard', value: 3, color: 'bg-yellow-500', shortcut: '2' },
  { label: 'Good', value: 5, color: 'bg-green-500', shortcut: '3' },
];

export default function FlashcardReviewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [reviewedCards, setReviewedCards] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [showShortcuts, setShowShortcuts] = useState(false);

  // 1. Get list of cards that need review
  const { data: dueCards, isLoading, isError } = useQuery({
    queryKey: ['dueFlashcards'],
    queryFn: () => FlashcardService.getDueFlashcards(50),
  });

  // 2. Mutation to send review results to backend
  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: number; quality: number }) =>
      FlashcardService.reviewFlashcard(cardId, { quality }),
    onSuccess: (_data, variables) => {
      // Track stats
      setReviewedCards(prev => prev + 1);
      if (variables.quality >= 3) {
        setCorrectCount(prev => prev + 1);
      }
      
      // Move to next card
      if (dueCards && currentCardIndex < dueCards.length - 1) {
        setCurrentCardIndex(prev => prev + 1);
        setIsFlipped(false);
      } else {
        // Complete review session
        setCurrentCardIndex(prev => prev + 1);
        const accuracy = Math.round((correctCount / reviewedCards) * 100);
        toast.success(`Review completed! ${reviewedCards} cards, ${accuracy}% accuracy`);
        queryClient.invalidateQueries({ queryKey: ['flashcards'] });
        invalidateProgressQueries(queryClient, { includeTodayPlan: true });
      }
    },
    onError: () => {
        toast.error('Failed to review card.');
    }
  });

  const handleReview = (quality: number) => {
    if (dueCards && isFlipped) {
      const cardId = dueCards[currentCardIndex].id;
      reviewMutation.mutate({ cardId, quality });
    }
  };

  // Keyboard shortcuts (like Quizlet!)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Space to flip
      if (e.code === 'Space' && !reviewMutation.isPending) {
        e.preventDefault();
        setIsFlipped(prev => !prev);
      }
      
      // 1, 2, 3 for ratings (only when flipped)
      if (isFlipped && !reviewMutation.isPending) {
        if (e.key === '1') handleReview(0);
        else if (e.key === '2') handleReview(3);
        else if (e.key === '3') handleReview(5);
      }
      
      // ? to toggle shortcuts help
      if (e.key === '?') {
        setShowShortcuts(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isFlipped, currentCardIndex, dueCards, reviewMutation.isPending]);

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
  const progressPercentage = ((currentCardIndex + 1) / dueCards.length) * 100;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <Button variant="ghost" onClick={() => navigate('/flashcards')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => setShowShortcuts(!showShortcuts)}
        >
          <Keyboard className="mr-2 h-4 w-4" />
          Shortcuts
        </Button>
      </div>

      {/* Keyboard Shortcuts Help */}
      {showShortcuts && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold mb-2">⌨️ Keyboard Shortcuts</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><kbd className="px-2 py-1 bg-white border rounded">Space</kbd> Flip card</div>
            <div><kbd className="px-2 py-1 bg-white border rounded">1</kbd> Again</div>
            <div><kbd className="px-2 py-1 bg-white border rounded">2</kbd> Hard</div>
            <div><kbd className="px-2 py-1 bg-white border rounded">3</kbd> Good</div>
            <div><kbd className="px-2 py-1 bg-white border rounded">?</kbd> Toggle shortcuts</div>
          </div>
        </div>
      )}

      <h1 className="text-2xl font-bold mb-2 text-center">Review Session</h1>
      
      {/* Progress Bar and Stats */}
      <div className="mb-4 space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Card {currentCardIndex + 1} of {dueCards.length}</span>
          <span>{reviewedCards} reviewed • {Math.round((correctCount / Math.max(reviewedCards, 1)) * 100)}% correct</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Flashcard with flip effect */}
      <div
          className="relative h-64 cursor-pointer [transform-style:preserve-3d] transition-transform duration-500"
          style={{ transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {/* Front side */}
          <div className="absolute w-full h-full p-6 rounded-lg bg-blue-100 border-2 border-blue-300 flex items-center justify-center [backface-visibility:hidden]">
            <div className="text-2xl font-semibold text-blue-800 text-center">
              <MarkdownText>{currentCard.front_text}</MarkdownText>
            </div>
          </div>
          {/* Back side */}
          <div className="absolute w-full h-full p-6 rounded-lg bg-green-100 border-2 border-green-300 flex flex-col items-center justify-center [backface-visibility:hidden] [transform:rotateY(180deg)]">
            <div className="text-xl font-medium text-green-800 text-center">
              <MarkdownText>{currentCard.back_text}</MarkdownText>
            </div>
          </div>
        </div>

      {/* Instructions and Rating buttons */}
      <div className="mt-6">
        {!isFlipped ? (
          <p className="text-center text-gray-500 text-sm">
            Click card or press <kbd className="px-2 py-1 bg-gray-100 border rounded text-xs">Space</kbd> to flip
          </p>
        ) : (
          <div>
            <p className="text-center mb-4 font-medium">How well did you remember this?</p>
            <div className="grid grid-cols-3 gap-4">
              {QUALITY_LEVELS.map(level => (
                <Button
                  key={level.value}
                  className={`${level.color} hover:opacity-90 text-white font-bold py-6`}
                  onClick={() => handleReview(level.value)}
                  disabled={reviewMutation.isPending}
                >
                  <div className="flex flex-col items-center">
                    {reviewMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin"/>
                    ) : (
                      <>
                        <span className="text-lg">{level.label}</span>
                        <span className="text-xs mt-1 opacity-75">Press {level.shortcut}</span>
                      </>
                    )}
                  </div>
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
