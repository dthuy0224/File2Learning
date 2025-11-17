import { useState, FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import toast from "react-hot-toast"
import { Button } from "../components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card"
import { Checkbox } from "../components/ui/checkbox"
import { Label } from "../components/ui/label"
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "../components/ui/select"
import { Input } from "../components/ui/input"
import api from "@/services/api"
import { useAuthStore } from "@/store/authStore"



export default function SetupLearningPage() {
  const navigate = useNavigate()
  const { updateUser, fetchUser } = useAuthStore() // Added to update user

  const [learningGoals, setLearningGoals] = useState<string[]>([])
  const [difficulty, setDifficulty] = useState<"" | "easy" | "medium" | "hard">("")
  const [dailyTime, setDailyTime] = useState<number | "">("")
  const [loading, setLoading] = useState(false)

  const goalsOptions: string[] = ["IELTS", "TOEIC", "Business English", "General English"]

  const handleGoalChange = (goal: string) => {
    setLearningGoals((prev) =>
      prev.includes(goal) ? prev.filter((g) => g !== goal) : [...prev, goal]
    )
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (learningGoals.length === 0) {
      toast.error("Please select at least one learning goal.")
      return
    }
    if (!difficulty) {
      toast.error("Please select your preferred difficulty.")
      return
    }
    if (!dailyTime || Number(dailyTime) < 10) {
      toast.error("Please set your daily study time (at least 10 minutes).")
      return
    }

    setLoading(true)
    try {
      // Send setup info
      const res = await api.put("/users/me/setup-learning", {
        learning_goals: learningGoals,
        difficulty_preference: difficulty,
        daily_study_time: Number(dailyTime),
      })

      // Update user in store (prefer res.data, fallback fetchUser)
      if (res?.data) {
        updateUser({ ...res.data, needs_setup: false })
      } else {
        await fetchUser()
      }

      toast.success("Your learning preferences have been saved!")
      navigate("/dashboard")
    } catch (error: any) {
      console.error("Error saving learning setup:", error)
      toast.error(error.response?.data?.detail || "Failed to save settings")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-lg shadow-xl border-0">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            🎯 Setup Your Learning Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Learning Goals */}
            <div>
              <Label className="text-lg font-medium mb-2 block">Learning Goals</Label>
              <div className="grid grid-cols-2 gap-3">
                {goalsOptions.map((goal) => (
                  <div key={goal} className="flex items-center space-x-2">
                    <Checkbox
                      id={goal}
                      checked={learningGoals.includes(goal)}
                      onCheckedChange={() => handleGoalChange(goal)}
                    />
                    <label htmlFor={goal}>{goal}</label>
                  </div>
                ))}
              </div>
            </div>

            {/* Difficulty */}
            <div>
              <Label className="text-lg font-medium mb-2 block">Difficulty</Label>
              <Select
                value={difficulty}
                onValueChange={(v) => setDifficulty(v as "easy" | "medium" | "hard")}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Easy</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="hard">Hard</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Daily Study Time */}
            <div>
              <Label className="text-lg font-medium mb-2 block">
                Daily Study Time (minutes)
              </Label>
              <Input
                type="number"
                min={10}
                step={5}
                placeholder="e.g. 30"
                value={dailyTime}
                onChange={(e) =>
                  setDailyTime(e.target.value ? Number(e.target.value) : "")
                }
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Saving..." : "Save"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
