import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Brain, Play, Plus, Clock } from 'lucide-react'

export default function QuizzesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quizzes</h1>
          <p className="text-gray-600 mt-2">Test your knowledge with AI-generated quizzes</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Create Quiz</span>
        </Button>
      </div>

      {/* Quick Start */}
      <Card className="bg-gradient-to-r from-green-500 to-blue-600 text-white">
        <CardHeader>
          <CardTitle className="text-white">Quick Quiz</CardTitle>
          <CardDescription className="text-green-100">
            Test your vocabulary with a 10-question mixed quiz
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="secondary" className="flex items-center space-x-2">
            <Play className="h-4 w-4" />
            <span>Start Quick Quiz</span>
          </Button>
        </CardContent>
      </Card>

      {/* Quizzes Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { title: "Business English", questions: 15, difficulty: "Medium" },
          { title: "IELTS Vocabulary", questions: 20, difficulty: "Hard" },
          { title: "General English", questions: 12, difficulty: "Easy" },
          { title: "Reading Comprehension", questions: 8, difficulty: "Medium" },
          { title: "Grammar Focus", questions: 18, difficulty: "Hard" },
          { title: "Daily Vocabulary", questions: 10, difficulty: "Easy" },
        ].map((quiz, i) => (
          <Card key={i} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-600" />
                <CardTitle className="text-lg">{quiz.title}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <CardDescription>
                  {quiz.questions} questions • {quiz.difficulty} difficulty
                </CardDescription>
                <div className="flex items-center space-x-1 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>~{quiz.questions * 2} minutes</span>
                </div>
              </div>
              <div className="mt-4 flex space-x-2">
                <Button size="sm" variant="outline">Preview</Button>
                <Button size="sm" className="flex items-center space-x-1">
                  <Play className="h-3 w-3" />
                  <span>Start</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
