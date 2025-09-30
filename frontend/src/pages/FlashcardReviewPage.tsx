import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import FlashcardService from '@/services/flashcardService';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';

// Giả sử backend trả về chất lượng (quality) từ 0-5
const QUALITY_LEVELS = [
  { label: 'Quên', value: 1, color: 'bg-red-500' },
  { label: 'Khó nhớ', value: 3, color: 'bg-yellow-500' },
  { label: 'Dễ dàng', value: 5, color: 'bg-green-500' },
];

export default function FlashcardReviewPage() {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const queryClient = useQueryClient();

  // 1. Lấy danh sách flashcard cần ôn tập
  const { data: dueCards, isLoading, isError } = useQuery({
    queryKey: ['dueFlashcards'],
    queryFn: () => FlashcardService.getDueFlashcards(50) // Lấy tối đa 50 card
  });

  // 2. Mutation để gửi kết quả review lên backend
  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: number; quality: number }) =>
      FlashcardService.reviewFlashcard(cardId, { quality }),
    onSuccess: () => {
      // Refresh dữ liệu để cập nhật danh sách due cards
      queryClient.invalidateQueries({ queryKey: ['dueFlashcards'] });

      // Chuyển sang thẻ tiếp theo sau khi gửi thành công
      if (dueCards && currentCardIndex < dueCards.length - 1) {
        setCurrentCardIndex(prev => prev + 1);
        setIsFlipped(false);
      } else {
        // Hoàn thành session
        setCurrentCardIndex(prev => prev + 1);
      }
    },
    onError: (error) => {
      toast.error('Có lỗi khi cập nhật flashcard. Vui lòng thử lại.');
      console.error('Review error:', error);
    }
  });

  const handleReview = (quality: number) => {
    if (dueCards) {
      const cardId = dueCards[currentCardIndex].id;
      reviewMutation.mutate({ cardId, quality });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (isError || !dueCards) {
    return (
      <div className="text-center min-h-[400px] flex items-center justify-center">
        <div>
          <p className="text-red-600 mb-4">Không thể tải phiên ôn tập.</p>
          <Button onClick={() => window.location.reload()}>
            Thử lại
          </Button>
        </div>
      </div>
    );
  }

  if (dueCards.length === 0 || currentCardIndex >= dueCards.length) {
    return (
      <div className="text-center min-h-[400px] flex items-center justify-center">
        <div>
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold mb-2">Hoàn thành!</h2>
          <p className="text-gray-600">Bạn đã ôn tập hết các thẻ trong hôm nay. Hãy quay lại sau nhé!</p>
          <Button className="mt-4" onClick={() => window.location.href = '/flashcards'}>
            Về trang Flashcards
          </Button>
        </div>
      </div>
    );
  }

  const currentCard = dueCards[currentCardIndex];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-center mb-2">Phiên ôn tập</h1>
        <p className="text-center text-gray-600">
          {currentCardIndex + 1} / {dueCards.length}
        </p>
      </div>

      {/* Thẻ Flashcard có thể lật */}
      <Card
        className="min-h-[300px] flex items-center justify-center p-8 cursor-pointer hover:shadow-lg transition-shadow mb-6"
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <CardContent className="text-center">
          {!isFlipped ? (
            <div>
              <div className="text-sm text-gray-500 mb-4">Nhấn để xem đáp án</div>
              <p className="text-4xl font-bold text-blue-600">
                {currentCard.front_text}
              </p>
              {currentCard.word_type && (
                <p className="text-sm text-gray-500 mt-2 uppercase">
                  {currentCard.word_type}
                </p>
              )}
            </div>
          ) : (
            <div>
              <p className="text-3xl font-bold mb-4">
                {currentCard.back_text}
              </p>
              {currentCard.example_sentence && (
                <p className="text-lg italic text-gray-600 mb-4">
                  "{currentCard.example_sentence}"
                </p>
              )}
              {currentCard.pronunciation && (
                <p className="text-sm text-gray-500">
                  Phát âm: {currentCard.pronunciation}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Các nút bấm đánh giá */}
      {isFlipped && (
        <div className="space-y-4">
          <p className="text-center text-gray-600">
            Bạn nhớ được từ này như thế nào?
          </p>
          <div className="grid grid-cols-3 gap-3">
            {QUALITY_LEVELS.map(level => (
              <Button
                key={level.value}
                className={`${level.color} hover:${level.color}/90 text-white h-12`}
                onClick={() => handleReview(level.value)}
                disabled={reviewMutation.isPending}
              >
                {reviewMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  level.label
                )}
              </Button>
            ))}
          </div>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => setIsFlipped(false)}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Xem lại
          </Button>
        </div>
      )}

      {!isFlipped && (
        <div className="text-center">
          <Button variant="outline" className="w-full" onClick={() => setIsFlipped(true)}>
            Hiện đáp án
          </Button>
        </div>
      )}
    </div>
  );
}
