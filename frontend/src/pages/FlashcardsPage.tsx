import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { CreditCard, Plus, RotateCcw } from 'lucide-react'

export default function FlashcardsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Flashcards</h1>
          <p className="text-gray-600 mt-2">Review and practice your vocabulary</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Create Flashcard</span>
        </Button>
      </div>

      {/* Study Session Card */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardHeader>
          <CardTitle className="text-white">Ready for Review</CardTitle>
          <CardDescription className="text-blue-100">
            You have 23 flashcards due for review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="secondary" className="flex items-center space-x-2">
            <RotateCcw className="h-4 w-4" />
            <span>Start Review Session</span>
          </Button>
        </CardContent>
      </Card>

      {/* Flashcards Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-lg">Vocabulary Set {i}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription>
                {Math.floor(Math.random() * 50) + 10} cards • 
                Due in {Math.floor(Math.random() * 24)} hours
              </CardDescription>
              <div className="mt-4 flex space-x-2">
                <Button size="sm" variant="outline">Review</Button>
                <Button size="sm">Practice</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
