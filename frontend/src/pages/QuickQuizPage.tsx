import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Loader2, Send } from 'lucide-react';
import { toast } from 'react-hot-toast';
import QuizService from '../services/quizService'; // Đảm bảo import đúng
import { QuizQuestion } from '../services/quizService'; // Import kiểu dữ liệu

export default function QuickQuizPage() {
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState<any>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    const fetchQuickQuiz = async () => {
      try {
        setLoading(true);
        const quizData = await QuizService.getQuickQuiz(); // Gọi hàm lấy quick quiz
        setQuiz(quizData);
        // Gán ID tạm thời cho câu hỏi để quản lý state
        const questionsWithId = quizData.questions.map((q, index) => ({ ...q, id: index }));
        setQuestions(questionsWithId);
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Không thể tạo Quick Quiz.');
        navigate('/quizzes');
      } finally {
        setLoading(false);
      }
    };
    fetchQuickQuiz();
  }, [navigate]);

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmitQuiz = () => {
    let correctAnswers = 0;
    questions.forEach(q => {
      if (userAnswers[q.id] === q.correct_answer) {
        correctAnswers++;
      }
    });
    setScore(correctAnswers);
    setShowResult(true); // Hiển thị kết quả
  };

  // Các hàm điều hướng câu hỏi
  const handleNextQuestion = () => setCurrentQuestionIndex(prev => Math.min(prev + 1, questions.length - 1));
  const handlePreviousQuestion = () => setCurrentQuestionIndex(prev => Math.max(prev - 1, 0));


  if (loading) {
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (showResult) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
        <div className="text-center">
            <h2 className="text-2xl font-bold">Kết quả Quick Quiz!</h2>
            <p className="text-4xl font-bold my-4">{percentage}%</p>
            <p>Bạn đã trả lời đúng {score} / {questions.length} câu hỏi.</p>
            <Button className="mt-6" onClick={() => navigate('/quizzes')}>Quay lại</Button>
        </div>
    );
  }

  if (!quiz || questions.length === 0) {
    return <div>Không có câu hỏi nào.</div>;
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="max-w-2xl mx-auto">
        {/* Giao diện làm bài có thể tái sử dụng từ QuizTakingPage */}
        <h1 className="text-3xl font-bold mb-4">{quiz.title}</h1>
        <Card>
            <CardHeader>
                <CardDescription>Câu hỏi {currentQuestionIndex + 1} / {questions.length}</CardDescription>
                <CardTitle>{currentQuestion.question_text}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {currentQuestion.options?.map((option, index) => (
                    <div key={index} className="flex items-center space-x-2">
                        <input
                            type="radio"
                            id={`option-${index}`}
                            name={`question-${currentQuestion.id}`}
                            value={option}
                            checked={userAnswers[currentQuestion.id] === option}
                            onChange={() => handleAnswerSelect(currentQuestion.id, option)}
                        />
                        <label htmlFor={`option-${index}`}>{option}</label>
                    </div>
                ))}
            </CardContent>
        </Card>
        <div className="mt-6 flex justify-between">
            <Button variant="outline" onClick={handlePreviousQuestion} disabled={currentQuestionIndex === 0}>Câu trước</Button>
            {currentQuestionIndex === questions.length - 1 ? (
                <Button onClick={handleSubmitQuiz}><Send className="mr-2 h-4 w-4"/>Nộp bài</Button>
            ) : (
                <Button onClick={handleNextQuestion}>Câu tiếp</Button>
            )}
        </div>
    </div>
  );
}
