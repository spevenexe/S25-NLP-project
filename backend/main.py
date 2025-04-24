import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from processor import save_file, generate_questions, evaluate_answers, auto_generate_answer
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
from processor import save_file, evaluate_answers
from schemas import GenerateQuestionsRequest, GenerateQuestionsResponse, SubmitAnswersRequest, SubmitAnswersResponse, GenerateAnswerResponse, GenerateAnswerRequest 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/uploadFile")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        file_path = await save_file(file)
        return {"status": "success", "message": "File processed successfully", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/generateQuestions", response_model=GenerateQuestionsResponse)
async def generate_questions_endpoint(request: GenerateQuestionsRequest):
    try:
        questions = generate_questions(request.questionCount)
        return {
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/submitAnswers", response_model=SubmitAnswersResponse)
async def submit_answers_endpoint(request: SubmitAnswersRequest):
    try:
        results = evaluate_answers(request.answers)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)