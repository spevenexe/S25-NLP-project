"use client"

import { useState } from "react"
import { Button } from "./components/ui/button"
import { Card } from "./components/ui/card"
import { FileUpload } from "./components/file-upload"
import { QuestionGenerator } from "./components/question-generator"
import { QuestionsPage } from "./components/questions-page"

export default function App() {
  const [uploadComplete, setUploadComplete] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  const [showQuestions, setShowQuestions] = useState(false)
  const [questions, setQuestions] = useState<Array<{ id: number; text: string }>>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleUploadComplete = (name: string) => {
    setFileName(name)
    setUploadComplete(true)
  }

  const handleQuestionsGenerated = (generatedQuestions: Array<{ id: number; text: string }>) => {
    setQuestions(generatedQuestions)
    setShowQuestions(true)
    setIsLoading(false)
  }

  if (showQuestions) {
    return <QuestionsPage questions={questions} fileName={fileName || ""} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-950 to-indigo-950 flex flex-col">
      <header className="container mx-auto py-6">
        <nav className="flex justify-between items-center">
          <div className="text-white font-bold text-xl">QuizMaker</div>
          <div className="flex gap-4">
            <Button variant="ghost" className="text-white hover:text-purple-300">
              About
            </Button>
            <Button variant="ghost" className="text-white hover:text-purple-300">
              Features
            </Button>
            <Button variant="ghost" className="text-white hover:text-purple-300">
              Contact
            </Button>
          </div>
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="max-w-3xl w-full text-center space-y-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400">
              Self-Study Quiz Maker
            </span>
          </h1>

          <p className="text-xl text-purple-200">To begin, upload your PDF file you want to study over</p>

          <Card className="p-8 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
            <FileUpload onUploadComplete={handleUploadComplete} />
          </Card>

          {uploadComplete && (
            <Card className="p-8 bg-black/40 border border-purple-500/30 backdrop-blur-sm">
              <QuestionGenerator
                fileName={fileName || ""}
                onQuestionsGenerated={handleQuestionsGenerated}
                setIsLoading={setIsLoading}
              />
            </Card>
          )}

          {isLoading && <div className="text-purple-200 text-xl">Generating your questions... Please wait.</div>}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="bg-black/30 p-6 rounded-lg border border-purple-500/20">
              <h3 className="text-xl font-bold text-purple-300 mb-2">Generate Questions</h3>
              <p className="text-gray-300">Our AI analyzes your PDF and creates relevant study questions</p>
            </div>
            <div className="bg-black/30 p-6 rounded-lg border border-purple-500/20">
              <h3 className="text-xl font-bold text-purple-300 mb-2">Test Your Knowledge</h3>
              <p className="text-gray-300">Take quizzes to reinforce your understanding of the material</p>
            </div>
            <div className="bg-black/30 p-6 rounded-lg border border-purple-500/20">
              <h3 className="text-xl font-bold text-purple-300 mb-2">Track Progress</h3>
              <p className="text-gray-300">Monitor your improvement and focus on challenging areas</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="container mx-auto py-6 text-center text-purple-300/60 text-sm">
        © {new Date().getFullYear()} Self-Study Quiz Maker. All rights reserved.
      </footer>
    </div>
  )
}