import uvicorn, os, uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from processor import process_pdf, generate_dummy_questions
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/hello")
def get_hello():
    return {
        "message": "hello world"
    }

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store mapping between original filenames and their unique IDs
file_mapping = {}

@app.post("/uploadFile")
async def upload_file(file: UploadFile = File(...)):
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
        
        return {
            "filename": file.filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


class QuestionGenerationRequest(BaseModel):
    fileName: str
    questionCount: int

@app.post("/generateQuestions")
async def generate_questions(request: QuestionGenerationRequest):
    try:
        # Check if the file exists in our mapping
        if request.fileName not in file_mapping:
            raise HTTPException(status_code=404, detail="File not found. Please upload the file first.")
        
        # Get the file path
        file_path = file_mapping[request.fileName]
        
        # For now, generate dummy questions
        questions = generate_dummy_questions(request.questionCount)
        
        return questions
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 