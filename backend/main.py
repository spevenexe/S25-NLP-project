import uvicorn, os, uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from processor import process_pdf, generate_dummy_questions, evaluate_answers
from schemas import GenerateQuestionsRequest, GenerateQuestionsResponse, SubmitAnswersRequest, SubmitAnswersResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store mapping between original filenames and their unique IDs
file_mapping = {}

@app.post("/uploadFile")
async def upload_file(file: UploadFile = File(...)) -> None:
    # Validate that the file is a PDF
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate a unique filename to prevent overwrites
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Store the mapping between original filename and path
        file_mapping[file.filename] = file_path
        
        # Process the PDF file (NLP processing)
        process_pdf(file_path)
        
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