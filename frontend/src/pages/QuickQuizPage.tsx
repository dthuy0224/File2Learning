import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CheckCircle, XCircle, RotateCcw } from 'lucide-react';
import quizService from '@/services/quizService';

interface UserAnswer {
  [questionId: number]: string;
}

export default function QuickQuizPage() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<UserAnswer>({});
  const [showResults, setShowResults] = useState(false);
  const [quizResults, setQuizResults] = useState<{
    correct: number;
    total: number;
    percentage: number;
    answers: any[];
  } | null>(null);

  // Lấy dữ liệu quiz nhanh
  const { data: quiz, isLoading, isError } = useQuery({
    queryKey: ['quickQuiz'],
    queryFn: () => quizService.getQuickQuiz(),
    retry: false
  });

  const handleAnswerChange = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (quiz && currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleSubmitQuiz();
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitQuiz = () => {
    if (!quiz) return;

    // Tính điểm ngay trên frontend (quiz tạm thời)
    let correct = 0;
    const answers = quiz.questions.map(question => {
      const userAnswer = userAnswers[question.id] || '';
      const isCorrect = userAnswer.toLowerCase().trim() === question.correct_answer.toLowerCase().trim();

      if (isCorrect) correct++;

      return {
        question: question.question_text,
        userAnswer,
        correctAnswer: question.correct_answer,
        isCorrect,
        explanation: question.explanation || ''
      };
    });

    const percentage = Math.round((correct / quiz.questions.length) * 100);

    setQuizResults({
      correct,
      total: quiz.questions.length,
      percentage,
      answers
    });

    setShowResults(true);
  };

  const handleRestartQuiz = () => {
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
    setQuizResults(null);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Đang tạo quiz từ flashcard của bạn...</p>
        </div>
      </div>
    );
  }

  if (isError || !quiz) {
    return (
      <div className="text-center min-h-[400px] flex items-center justify-center">
        <div>
          <p className="text-red-600 mb-4">
            Không thể tạo Quick Quiz. Bạn cần có ít nhất 4 flashcard để tạo quiz.
          </p>
          <Button onClick={() => window.location.href = '/flashcards'}>
            Đến trang Flashcards
          </Button>
        </div>
      </div>
    );
  }

  if (showResults && quizResults) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Kết quả Quick Quiz</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-6">
            <div className="text-6xl">
              {quizResults.percentage >= 80 ? '🎉' : quizResults.percentage >= 60 ? '👍' : '😅'}
            </div>

            <div className="text-4xl font-bold">
              {quizResults.correct}/{quizResults.total}
            </div>

            <div className="text-2xl">
              {quizResults.percentage}% đúng
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Chi tiết câu trả lời:</h3>
              {quizResults.answers.map((answer, index) => (
                <div key={index} className="text-left border rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    {answer.isCorrect ? (
                      <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium">{answer.question}</p>
                      <p className={`text-sm ${answer.isCorrect ? 'text-green-600' : 'text-red-600'}`}>
                        Đáp án của bạn: {answer.userAnswer || 'Không trả lời'}
                      </p>
                      {!answer.isCorrect && (
                        <p className="text-sm text-gray-600">
                          Đáp án đúng: {answer.correctAnswer}
                        </p>
                      )}
                      {answer.explanation && (
                        <p className="text-sm text-gray-500 mt-1">
                          Giải thích: {answer.explanation}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex space-x-4 justify-center">
              <Button onClick={handleRestartQuiz} className="flex items-center space-x-2">
                <RotateCcw className="h-4 w-4" />
                <span>Làm lại</span>
              </Button>
              <Button variant="outline" onClick={() => window.location.href = '/quizzes'}>
                Về trang Quizzes
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const currentAnswer = userAnswers[currentQuestion.id] || '';

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-center mb-2">{quiz.title}</h1>
        <p className="text-center text-gray-600">
          Câu hỏi {currentQuestionIndex + 1} / {quiz.questions.length}
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">{currentQuestion.question_text}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {currentQuestion.options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-3">
                <input
                  type="radio"
                  id={`option-${index}`}
                  name={`question-${currentQuestion.id}`}
                  value={option}
                  checked={currentAnswer === option}
                  onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                  className="w-4 h-4 text-blue-600"
                />
                <label htmlFor={`option-${index}`} className="flex-1 cursor-pointer text-sm">
                  {option}
                </label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handlePreviousQuestion}
          disabled={currentQuestionIndex === 0}
        >
          Câu trước
        </Button>

        <div className="flex space-x-2">
          {quiz.questions.map((_, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full ${
                index === currentQuestionIndex
                  ? 'bg-blue-500'
                  : userAnswers[quiz.questions[index].id]
                    ? 'bg-green-500'
                    : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        <Button
          onClick={handleNextQuestion}
          disabled={!currentAnswer}
        >
          {currentQuestionIndex === quiz.questions.length - 1 ? 'Nộp bài' : 'Câu tiếp'}
        </Button>
      </div>

      <div className="mt-4 text-center">
        <p className="text-sm text-gray-500">
          Hãy chọn đáp án trước khi tiếp tục
        </p>
      </div>
    </div>
  );
}
