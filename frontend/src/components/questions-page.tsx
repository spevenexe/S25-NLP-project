"use client"

import { useState } from "react"
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { ArrowLeft, Send } from "lucide-react"
import api from "../api"

interface QuestionsPageProps {
    questions: Array<{ id: number; text: string }>
    fileName: string
}

export function QuestionsPage({ questions, fileName }: QuestionsPageProps) {
    const [answers, setAnswers] = useState<Record<number, string>>(
        questions.reduce((acc, q) => ({ ...acc, [q.id]: "" }), {}),
    )
    const [submitting, setSubmitting] = useState(false)
    const [submitComplete, setSubmitComplete] = useState(false)
    const [error, setError] = useState<string | null>(null)

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
            const answersArray = Object.entries(answers).map(([id, answer]) => ({
                questionId: Number.parseInt(id),
                answer,
            }))

            // Submit answers to the API
            const response = await api.post("/submitAnswers", {
                fileName,
                answers: answersArray,
            })

            if (response.status === 200) {
                setSubmitComplete(true)
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
                        <span className="text-sm">File: </span>
                        <span className="font-medium">{fileName}</span>
                    </div>
                </nav>
            </header>

            <main className="flex-1 container mx-auto py-8 px-4">
                <div className="max-w-3xl mx-auto">
                    <h1 className="text-3xl font-bold text-white mb-8 text-center">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400">
                        Your Study Questions
                    </span>
                    </h1>

                    {submitComplete ? (
                        <Card className="p-8 bg-black/40 border border-purple-500/30 backdrop-blur-sm text-center">
                            <h2 className="text-2xl font-bold text-green-400 mb-4">Answers Submitted Successfully!</h2>
                            <p className="text-purple-200 mb-6">Thank you for completing the quiz.</p>
                            <Button onClick={handleGoBack} className="bg-purple-600 hover:bg-purple-700 text-white">
                            Create Another Quiz
                            </Button>
                        </Card>
                    ) : (
                        <>
                            <div className="space-y-8 mb-12">
                                {questions.map((q, index) => (
                                    <Card key={q.id} className="p-6 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
                                        <div className="space-y-4">
                                            <div className="flex items-start gap-4">
                                            <div className="bg-purple-700 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                                                {index + 1}
                                            </div>
                                            <h3 className="text-xl text-purple-100">{q.text}</h3>
                                            </div>

                                            <div className="pt-2">
                                            <input
                                                type="text"
                                                value={answers[q.id]}
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
                        </>
                    )}
                </div>
            </main>

            <footer className="container mx-auto py-6 text-center text-purple-300/60 text-sm">
            © {new Date().getFullYear()} Self-Study Quiz Maker. All rights reserved.
            </footer>
        </div>
    )
}