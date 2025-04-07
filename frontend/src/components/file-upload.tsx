"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "./ui/button"
import { Upload, FileText, Check, AlertCircle } from "lucide-react"
import { Progress } from "./ui/progress"
import api from "../api"

interface FileUploadProps {
    onUploadComplete: (fileName: string) => void
}

export function FileUpload({ onUploadComplete }: FileUploadProps) {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [uploadComplete, setUploadComplete] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        const maxFileSize = 10 * 1024 * 1024 // 10MB size limit
        if (selectedFile) {
            if (selectedFile.type !== "application/pdf") {
                setError("Please upload a PDF file")
                setFile(null)
                return
            }
            if (selectedFile.size > maxFileSize) {
                setError(`File exceeds ${maxFileSize / (1024 * 1024)}MB limit`)
                setFile(null)
                return
            }
            setError(null)
            setFile(selectedFile)
            setUploadComplete(false)
        }
    }

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        setProgress(0)

        // Create form data to send the file
        const formData = new FormData()
        formData.append("file", file)

        try {
            // Simulate progress updates
            const progressInterval = setInterval(() => {
                setProgress((prev) => {
                    if (prev >= 90) {
                    clearInterval(progressInterval)
                    return 90
                    }
                    return prev + 10
                })
            }, 300)

            // Send the file to the backend
            const response = await api.post("/uploadFile", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            })

            clearInterval(progressInterval)
            setProgress(100)

            // Handle successful upload
            if (response.status === 200) {
                setTimeout(() => {
                    setUploading(false)
                    setUploadComplete(true)
                    onUploadComplete(file.name)
                }, 500)
            }
        } catch (err) {
            console.error("Error uploading file:", err)
            setError("Failed to upload file. Please try again or check server connection.")
            setUploading(false)
            setProgress(0)
        }
    }

    return (
        <div className="space-y-6">
            <div
            className="border-2 border-dashed border-purple-500/50 rounded-lg p-8 text-center hover:bg-purple-950/20 transition-colors cursor-pointer"
            onClick={() => document.getElementById("file-upload")?.click()}
            >
                <input id="file-upload" type="file" accept=".pdf" className="hidden" onChange={handleFileChange} />

                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="p-3 rounded-full bg-purple-900/50">
                        <Upload className="h-8 w-8 text-purple-400" />
                    </div>
                    <div className="space-y-2">
                        <p className="text-white font-medium">
                            {file ? file.name : "Drag & drop your PDF here or click to browse"}
                        </p>
                        <p className="text-sm text-purple-300/70">Supports PDF files up to 10MB</p>
                    </div>
                </div>
            </div>

            {error && (
            <div className="flex items-center gap-2 text-red-400 bg-red-950/20 p-3 rounded-md">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
            </div>
            )}

            {file && !uploadComplete && !uploading && (
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-purple-200">
                    <FileText className="h-5 w-5" />
                    <span className="text-sm truncate max-w-[200px]">{file.name}</span>
                </div>
                <Button onClick={handleUpload} className="bg-purple-600 hover:bg-purple-700 text-white">
                    Upload PDF
                </Button>
            </div>
            )}

            {uploading && (
            <div className="space-y-2">
                <div className="flex justify-between text-sm text-purple-300">
                    <span>Uploading to server...</span>
                    <span>{progress}%</span>
                </div>
                <Progress value={progress} className="h-2 bg-purple-950" />
            </div>
            )}

            {uploadComplete && (
            <div className="flex items-center gap-2 text-green-400 bg-green-950/20 p-3 rounded-md">
                <Check className="h-5 w-5" />
                <span>Upload complete! PDF successfully sent to server.</span>
            </div>
            )}
        </div>
    )
}