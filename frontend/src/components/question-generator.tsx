"use client"

import { useState } from "react"
import { Button } from "./ui/button"
import { Slider } from "./ui/slider"
import api from "../api"

interface Question {
  id: number
  text: string
  category: string
}

interface GenerateQuestionsResponse {
  questions: Question[]
}

interface QuestionGeneratorProps {
  onQuestionsGenerated: (questions: Question[]) => void
  setIsLoading: (loading: boolean) => void
}

export function QuestionGenerator({ onQuestionsGenerated, setIsLoading }: QuestionGeneratorProps) {
  const [questionCount, setQuestionCount] = useState(5)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateQuestions = async () => {
    setError(null)
    setIsLoading(true)

    try {
      // Call the API to generate questions
      const response = await api.post<GenerateQuestionsResponse>("/generateQuestions", {
        questionCount,
      })

      // Handle successful response
      if (response.status === 200 && response.data) {
        onQuestionsGenerated(response.data.questions)
      } else {
        throw new Error("Invalid response from server")
      }
    } catch (err) {
      console.error("Error generating questions:", err)
      setError("Failed to generate questions. Please try again.")
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-purple-300">Generate Quiz Questions</h2>

      <div className="space-y-4">
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
          onClick={handleGenerateQuestions}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white py-6 text-lg"
        >
          Generate Questions
        </Button>
      </div>

      {error && <div className="text-red-400 bg-red-950/20 p-3 rounded-md text-center">{error}</div>}
    </div>
  )
}
