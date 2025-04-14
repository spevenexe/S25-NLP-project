import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from processor import save_file, generate_dummy_questions, evaluate_answers
from schemas import GenerateQuestionsRequest, GenerateQuestionsResponse, SubmitAnswersRequest, SubmitAnswersResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



@app.post("/uploadFile")
async def upload_file(file: UploadFile = File(...)) -> None:
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    try:
        await save_file(file)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/generateQuestions", response_model = GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest):
    try:
        questions = generate_dummy_questions(request.questionCount)
        return {
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/submitAnswers", response_model = SubmitAnswersResponse)
async def submit_answers(request: SubmitAnswersRequest):
    try:
        results = evaluate_answers(request.answers)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 