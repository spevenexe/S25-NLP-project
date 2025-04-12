"use client"

import { useState, useEffect } from "react"
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { ArrowLeft, Send } from "lucide-react"
import api from "../api"
import { ResultsPage } from "./results-page"
import { Loader2 } from "lucide-react"

interface Question {
  id: number
  text: string
  category: string
}

interface Score {
  id: number
  score: number
}

interface SubmitAnswersResponse {
  strengths: string[]
  weaknesses: string[]
  scores: Score[]
}

interface QuestionsPageProps {
  questions: Question[]
}

export function QuestionsPage({ questions: initialQuestions }: QuestionsPageProps) {
  // Store questions in state so we can update them
  const [questions, setQuestions] = useState<Question[]>(initialQuestions)
  
  // Initialize answers based on questions
  const [answers, setAnswers] = useState<Record<number, string>>(
    questions.reduce((acc, q) => ({ ...acc, [q.id]: "" }), {}),
  )
  
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<SubmitAnswersResponse | null>(null)

  // Reset answers whenever questions change
  useEffect(() => {
    setAnswers(questions.reduce((acc, q) => ({ ...acc, [q.id]: "" }), {}))
  }, [questions])

  const handleAnswerChange = (id: number, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [id]: value,
    }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setError(null)

    try {
      // Format answers for submission
      const answersArray = Object.entries(answers).map(([id, text]) => ({
        id: Number.parseInt(id),
        text,
      }))

      const isIncomplete = answersArray.some(a => !a.text)
      if (isIncomplete) {
        setError("Please complete all answers before submitting.")
        setSubmitting(false)
        return
      }

      // Submit answers to the API
      const response = await api.post("/submitAnswers", {
        answers: answersArray,
      })

      if (response.status === 200) {
        setResults(response.data)
      } else {
        throw new Error("Failed to submit answers")
      }
    } catch (err) {
      console.error("Error submitting answers:", err)
      setError("Failed to submit answers. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  const handleGoBack = () => {
    window.location.reload()
  }

  const handleRegenerateQuiz = (newQuestions: Question[]) => {
    // Update questions state
    setQuestions(newQuestions)
    // Reset results
    setResults(null)
  }

  // If we have results, show the results page
  if (results) {
    return (
      <ResultsPage 
        results={results} 
        questions={questions} 
        userAnswers={answers} 
        onGoBack={handleGoBack} 
        onRegenerateQuiz={handleRegenerateQuiz}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-950 to-indigo-950 flex flex-col">
      <header className="container mx-auto py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Button variant="ghost" className="text-white hover:text-purple-300 p-2" onClick={handleGoBack}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="text-white font-bold text-xl">QuizMaker</div>
          </div>
          <div className="text-purple-300">
            <span className="text-sm">Questions: </span>
            <span className="font-medium">{questions.length}</span>
          </div>
        </nav>
      </header>

      <main className="flex-1 container mx-auto py-8 px-4">
        {submitting ? (
          <div className="max-w-3xl mx-auto flex flex-col items-center justify-center h-full space-y-8">
            <div className="relative">
              <Loader2 className="h-16 w-16 text-purple-400 animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-4 w-4 rounded-full bg-purple-600"></div>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-purple-200 text-center">Grading and Analyzing Your Answers...</h2>
            <p className="text-purple-300/70 text-center max-w-md">
              Our AI is evaluating your responses and preparing detailed feedback on your strengths and weaknesses.
            </p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8 text-center">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400">
                Your Study Questions
              </span>
            </h1>

            <div className="space-y-8 mb-12">
              {questions.map((q, index) => (
                <Card key={q.id} className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
                  <div className="space-y-4">
                    <div className="flex items-start gap-4">
                      <div className="bg-purple-700 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="text-xl text-purple-100">{q.text}</h3>
                        <span className="text-xs text-purple-400 mt-1 inline-block px-2 py-1 bg-purple-950/50 rounded-full">
                          {q.category}
                        </span>
                      </div>
                    </div>

                    <div className="pt-2">
                      <input
                        type="text"
                        value={answers[q.id] || ""}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                        placeholder="Type your answer here..."
                        className="w-full bg-black/30 border-b-2 border-purple-500/50 focus:border-purple-400 px-4 py-2 text-white outline-none transition-colors"
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {error && <div className="text-red-400 bg-red-950/20 p-3 rounded-md text-center mb-6">{error}</div>}

            <div className="flex justify-center">
              <Button
                onClick={handleSubmit}
                disabled={submitting}
                className="bg-purple-600 hover:bg-purple-700 text-white py-6 px-8 text-lg flex items-center gap-2"
              >
                <span>Submit Answers</span>
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </div>
        )}
      </main>

      <footer className="container mx-auto py-6 text-center text-purple-300/60 text-sm">
        © {new Date().getFullYear()} Self-Study Quiz Maker. All rights reserved.
      </footer>
    </div>
  )
}