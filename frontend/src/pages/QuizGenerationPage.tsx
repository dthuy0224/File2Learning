import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Loader2, ArrowLeft, FileText, Brain, CheckCircle, AlertCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { QuizQuestionExtended, QuizResponse } from '../services/aiService'
import QuizService from '../services/quizService'

export default function QuizGenerationPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [document, setDocument] = useState<any>(null)
  const [quiz, setQuiz] = useState<QuizQuestionExtended[]>([])
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({})
  const [savedQuiz, setSavedQuiz] = useState<any>(null)
  const [savingQuiz, setSavingQuiz] = useState(false)

  // Quiz generation settings
  const [quizType, setQuizType] = useState<'mcq' | 'fill_blank' | 'mixed'>('mixed')
  const [numQuestions, setNumQuestions] = useState(5)

  useEffect(() => {
    if (documentId) {
      fetchDocumentDetails()
    }
  }, [documentId])

  const fetchDocumentDetails = async () => {
    try {
      setLoading(true)
      const documentData = await AIService.getDocumentContent(parseInt(documentId!))
      setDocument(documentData)
    } catch (error) {
      console.error('Error fetching document:', error)
      toast.error('Failed to load document details')
      navigate('/documents')
    } finally {
      setLoading(false)
    }
  }

  const generateQuiz = async () => {
    try {
      setGenerating(true)
      const response: QuizResponse = await AIService.generateQuiz(
        parseInt(documentId!),
        quizType,
        numQuestions
      )

      
      const formattedQuiz: QuizQuestionExtended[] = response.quiz.map((q, index) => ({
        
        question: q.question,
        options: q.options,
        correct_answer: q.correct_answer,
        question_type: q.question_type,
        
        id: index, // Temporary ID for frontend display
        question_text: q.question,
        explanation: undefined, 
        points: 1,
        order_index: index + 1,
        quiz_id: 0, 
        created_at: new Date().toISOString()
      }))

      setQuiz(formattedQuiz)
      toast.success(`Generated ${response.quiz.length} quiz questions!`)
    } catch (error: any) {
      console.error('Error generating quiz:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate quiz')
    } finally {
      setGenerating(false)
    }
  }

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }))
  }

  const checkAnswers = () => {
    let correct = 0
    quiz.forEach((question, index) => {
      if (userAnswers[index] === question.correct_answer) {
        correct++
      }
    })

    const percentage = Math.round((correct / quiz.length) * 100)
    toast.success(`Quiz completed! Score: ${correct}/${quiz.length} (${percentage}%)`)
  }

  const saveQuiz = async () => {
    if (quiz.length === 0) {
      toast.error('No quiz to save');
      return;
    }

    try {
      setSavingQuiz(true);

      const quizData = {
        title: `${document.title || document.original_filename} - Quiz`,
        description: `AI-generated ${quizType.toUpperCase()} quiz with ${numQuestions} questions`,
        quiz_type: quizType === 'mcq' ? 'multiple_choice' : quizType === 'fill_blank' ? 'fill_blank' : 'mixed',
        difficulty_level: 'medium',
        document_id: parseInt(documentId!),
        questions: quiz.map((q) => ({
          question: q.question_text, // Change from question_text to question to match createQuizFromAI
          options: q.options,
          correct_answer: q.correct_answer,
          question_type: q.question_type,
          explanation: q.explanation,
          points: 1
          // No need for order_index as createQuizFromAI will create it automatically
        }))
      };

      // Call the service to create quiz
      const savedQuizData = await QuizService.createQuizFromAI(quizData as any);
      setSavedQuiz(savedQuizData);
      toast.success('Quiz saved successfully!');
    } catch (error: any) {
      console.error('Error saving quiz:', error);
      toast.error(error.response?.data?.detail?.[0]?.msg || 'Failed to save quiz.');
    } finally {
      setSavingQuiz(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading document...</span>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Document not found</h3>
        <p className="text-gray-600">The document you're looking for doesn't exist or has been deleted.</p>
        <Button className="mt-4" onClick={() => navigate('/documents')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      
      <div className="flex items-center space-x-4">
        <Button variant="outline" onClick={() => navigate('/documents')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Generate Quiz</h1>
          <p className="text-gray-600 mt-2">
            Create AI-powered quiz questions from: {document.title || document.original_filename}
          </p>
        </div>
      </div>

      
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <CardTitle>{document.title || document.original_filename}</CardTitle>
              <CardDescription>
                {document.word_count.toLocaleString()} words • {document.document_type.toUpperCase()}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

                        
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Quiz Settings</span>
          </CardTitle>
          <CardDescription>
            Configure your AI-generated quiz parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quiz Type
              </label>
              <Select value={quizType} onValueChange={(value: any) => setQuizType(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select quiz type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mcq">Multiple Choice</SelectItem>
                  <SelectItem value="fill_blank">Fill in the Blank</SelectItem>
                  <SelectItem value="mixed">Mixed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions
              </label>
              <Select value={numQuestions.toString()} onValueChange={(value) => setNumQuestions(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select number of questions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3">3 Questions</SelectItem>
                  <SelectItem value="5">5 Questions</SelectItem>
                  <SelectItem value="10">10 Questions</SelectItem>
                  <SelectItem value="15">15 Questions</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button
            onClick={generateQuiz}
            disabled={generating}
            className="w-full"
            size="lg"
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Quiz...
              </>
            ) : (
              <>
                <Brain className="h-4 w-4 mr-2" />
                Generate Quiz
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Quiz */}
      {quiz.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Quiz</CardTitle>
            <CardDescription>
              Answer the following {quiz.length} questions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {quiz.map((question, index) => (
              <div key={question.id} className="border-b border-gray-200 pb-6 last:border-b-0">
                <h4 className="font-medium text-gray-900 mb-3">
                  {index + 1}. {question.question_text}
                </h4>

                {question.question_type === 'multiple_choice' && question.options ? (
                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <label key={optionIndex} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={option}
                          checked={userAnswers[question.id] === option}
                          onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
                          className="text-blue-600"
                        />
                        <span className="text-gray-700">
                          {String.fromCharCode(65 + optionIndex)}. {option}
                        </span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <div>
                    <input
                      type="text"
                      value={userAnswers[question.id] || ''}
                      onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
                      placeholder="Type your answer here..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                )}
              </div>
            ))}

            <div className="flex justify-center space-x-4">
              <Button onClick={checkAnswers} size="lg" variant="outline">
                Check Answers (Preview)
              </Button>
              <Button onClick={saveQuiz} disabled={savingQuiz || savedQuiz} size="lg">
                {savingQuiz ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : savedQuiz ? (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Quiz Saved
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Save Quiz
                  </>
                )}
              </Button>
            </div>

            {savedQuiz && (
              <div className="text-center space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-green-800 font-medium">Quiz saved successfully!</p>
                  <p className="text-green-600 text-sm">You can now take this quiz anytime from your quiz list.</p>
                </div>
                <div className="flex justify-center space-x-4">
                  <Button onClick={() => navigate(`/quizzes/${savedQuiz.id}/take`)} size="lg">
                    Start Quiz Now
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/quizzes')} size="lg">
                    View All Quizzes
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
