"use client"

import { useState } from "react"
import { Card } from "./ui/card"
import { Button } from "./ui/button"
import { ArrowLeft, Brain, Lightbulb, Zap } from "lucide-react"
import { BarChart } from "./ui/bar-chart"
import { Slider } from "./ui/slider"
import api from "../api"

interface Question {
  id: number
  text: string
  category: string
}

interface Score {
  id: number
  score: number
}

interface GenerateQuestionsResponse {
  questions: Question[]
}

interface SubmitAnswersResponse {
  strengths: string[]
  weaknesses: string[]
  scores: Score[]
}

interface ResultsPageProps {
  results: SubmitAnswersResponse
  questions: Question[]
  userAnswers: Record<number, string> // Add this prop to receive answers
  onGoBack: () => void
  onRegenerateQuiz?: (newQuestions: Question[]) => void // Add this callback
}

export function ResultsPage({ 
  results, 
  questions, 
  userAnswers, 
  onGoBack, 
  onRegenerateQuiz 
}: ResultsPageProps) {
  const [remakeQuiz, setRemakeQuiz] = useState<boolean | null>(null)
  const [questionCount, setQuestionCount] = useState(5)
  const [isLoading, setIsLoading] = useState(false)
  
  // Calculate total score and max possible score
  const totalScore = results.scores.reduce((sum, score) => sum + score.score, 0)
  const maxPossibleScore = questions.length * 5
  const scorePercentage = (totalScore / maxPossibleScore) * 100

  // Calculate scores by category
  const categoryScores = calculateCategoryScores(questions, results.scores)

  const handleRegenerateQuiz = async () => {
    setIsLoading(true)
    try {
      // Call the API to generate new questions
      const response = await api.post<GenerateQuestionsResponse>("/regenerateTailoredQuestions", {
        questionCount,
        "weaknesses" : results.weaknesses
      })

      if (response.status === 200 && response.data && onRegenerateQuiz) {
        // Call the parent component's callback with the new questions
        onRegenerateQuiz(response.data.questions)
      }
    } catch (error) {
      console.error("Error regenerating quiz:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-950 to-indigo-950 flex flex-col">
      <header className="container mx-auto py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Button variant="ghost" className="text-white hover:text-purple-300 p-2" onClick={onGoBack}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="text-white font-bold text-xl">QuizMaker</div>
          </div>
        </nav>
      </header>

      <main className="flex-1 container mx-auto py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-white mb-12 text-center">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400">
              Your Quiz Results
            </span>
          </h1>

          {/* Score Circle */}
          <div className="flex justify-center mb-16">
            <div className="text-center">
            <h2 className="text-2xl font-bold text-purple-200 mt-4">Your Full Score</h2>
              <div className="relative inline-flex">
                <ScoreCircle percentage={scorePercentage} />
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-white">{totalScore}</span>
                  <span className="text-sm text-purple-300">/ {maxPossibleScore}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Strengths and Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            <Card className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full bg-green-600/20">
                  <Zap className="h-6 w-6 text-green-400" />
                </div>
                <h3 className="text-xl font-bold text-green-400">Strengths</h3>
              </div>
              <ul className="space-y-2">
                {results.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start gap-2 text-purple-100">
                    <div className="mt-1 text-green-400">•</div>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full bg-orange-600/20">
                  <Lightbulb className="h-6 w-6 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold text-orange-400">Areas to Improve</h3>
              </div>
              <ul className="space-y-2">
                {results.weaknesses.map((weakness, index) => (
                  <li key={index} className="flex items-start gap-2 text-purple-100">
                    <div className="mt-1 text-orange-400">•</div>
                    <span>{weakness}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          {/* Performance by Category */}
          <Card className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-full bg-purple-600/20">
                <Brain className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-purple-400">Performance by Category</h3>
            </div>
            <div className="h-80">
              <BarChart data={categoryScores} />
            </div>
          </Card>

          {/* Question Review Section */}
          <h2 className="text-2xl font-bold text-purple-300 mb-6">Question Review</h2>
          <div className="space-y-6 mb-16">
            {questions.map((question) => {
              const score = results.scores.find((s) => s.id === question.id)?.score || 0
              const scorePercentage = (score / 5) * 100

              return (
                <Card key={question.id} className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
                  <div className="flex items-start gap-4">
                    <div className="flex-1 space-y-4">
                      <div>
                        <h3 className="text-lg font-medium text-purple-100">{question.text}</h3>
                        <span className="text-xs text-purple-400 mt-1 inline-block px-2 py-1 bg-purple-950/50 rounded-full">
                          {question.category}
                        </span>
                      </div>

                      <div className="pt-2">
                        <div className="text-sm text-gray-400 mb-1">Your Answer:</div>
                        <div className="bg-black/30 border-b-2 border-purple-500/50 px-4 py-2 text-white rounded-sm">
                          {userAnswers[question.id] || "No answer provided"}
                        </div>
                      </div>
                    </div>

                    <div className="flex-shrink-0 flex items-center">
                      <div className="relative inline-flex">
                        <SmallScoreCircle percentage={scorePercentage} />
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-lg font-bold text-white">{score}</span>
                          <span className="text-xs text-purple-300">/5</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>

          {/* Remake Quiz Section */}
          <Card className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm mb-8">
            <h3 className="text-xl font-bold text-purple-300 mb-4 text-center">
              Want to Remake a Quiz that focuses on your Weaknesses?
            </h3>

            <div className="flex justify-center gap-4 mb-6">
              <Button
                variant={remakeQuiz === true ? "default" : "outline"}
                className={
                  remakeQuiz === true
                    ? "bg-purple-600 hover:bg-purple-700 text-white"
                    : "text-purple-300 border-purple-500/50"
                }
                onClick={() => setRemakeQuiz(true)}
              >
                Yes
              </Button>
              <Button
                variant={remakeQuiz === false ? "default" : "outline"}
                className={
                  remakeQuiz === false
                    ? "bg-purple-600 hover:bg-purple-700 text-white"
                    : "text-purple-300 border-purple-500/50"
                }
                onClick={() => setRemakeQuiz(false)}
              >
                No
              </Button>
            </div>

            {remakeQuiz === true && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-purple-200">
                    <span>Number of questions to generate:</span>
                    <span className="font-bold">{questionCount}</span>
                  </div>

                  <Slider
                    value={[questionCount]}
                    min={1}
                    max={20}
                    step={1}
                    onValueChange={(value) => setQuestionCount(value[0])}
                    className="py-4"
                  />
                </div>

                <Button
                  onClick={handleRegenerateQuiz}
                  disabled={isLoading}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white py-4 text-lg"
                >
                  Regenerate New Quiz
                </Button>
              </div>
            )}

            {remakeQuiz === false && (
              <div className="flex justify-center">
                <Button onClick={onGoBack} className="bg-purple-600 hover:bg-purple-700 text-white py-4 px-8">
                  Go Back to Home
                </Button>
              </div>
            )}
          </Card>
        </div>
      </main>

      <footer className="container mx-auto py-6 text-center text-purple-300/60 text-sm">
        © {new Date().getFullYear()} Self-Study Quiz Maker. All rights reserved.
      </footer>
    </div>
  )
}

function calculateCategoryScores(questions: Question[], scores: Score[]) {
  // Create a map to group questions by category
  const categoriesMap = new Map<string, { total: number; max: number }>()

  // Initialize categories
  questions.forEach((question) => {
    if (!categoriesMap.has(question.category)) {
      categoriesMap.set(question.category, { total: 0, max: 0 })
    }
  })

  // Calculate scores for each category
  questions.forEach((question) => {
    const score = scores.find((s) => s.id === question.id)
    if (score) {
      const categoryData = categoriesMap.get(question.category)!
      categoryData.total += score.score
      categoryData.max += 5 // Each question is worth 5 points
    }
  })

  // Convert to percentage and format for the chart
  return Array.from(categoriesMap.entries()).map(([category, data]) => {
    const percentage = (data.total / data.max) * 100
    return {
      name: category,
      value: percentage,
    }
  })
}

function ScoreCircle({ percentage }: { percentage: number }) {
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <svg width="180" height="180" viewBox="0 0 180 180">
      {/* Background circle */}
      <circle cx="90" cy="90" r={radius} fill="transparent" stroke="#3b0764" strokeWidth="12" />
      {/* Progress circle */}
      <circle
        cx="90"
        cy="90"
        r={radius}
        fill="transparent"
        stroke="url(#gradient)"
        strokeWidth="12"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        strokeLinecap="round"
        transform="rotate(-90 90 90)"
      />
      {/* Gradient definition */}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#a855f7" />
          <stop offset="100%" stopColor="#818cf8" />
        </linearGradient>
      </defs>
    </svg>
  )
}

function SmallScoreCircle({ percentage }: { percentage: number }) {
  const radius = 25
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <svg width="70" height="70" viewBox="0 0 70 70">
      {/* Background circle */}
      <circle cx="35" cy="35" r={radius} fill="transparent" stroke="#3b0764" strokeWidth="6" />
      {/* Progress circle */}
      <circle
        cx="35"
        cy="35"
        r={radius}
        fill="transparent"
        stroke="url(#smallGradient)"
        strokeWidth="6"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        strokeLinecap="round"
        transform="rotate(-90 35 35)"
      />
      {/* Gradient definition */}
      <defs>
        <linearGradient id="smallGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#a855f7" />
          <stop offset="100%" stopColor="#818cf8" />
        </linearGradient>
      </defs>
    </svg>
  )
}