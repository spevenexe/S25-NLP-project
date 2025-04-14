import PyPDF2, random, os, uuid

async def save_file(file):
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_mapping = {}
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

def process_pdf(file_path):
    text = extract_text_from_pdf(file_path)

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        text = ""
    return text

def generate_dummy_questions(count: int):
    question_types = [
        "What is the main idea of",
        "Explain the concept of",
        "How does the author describe",
        "What evidence supports",
        "Compare and contrast",
        "Analyze the relationship between",
        "What are the implications of",
        "Describe the significance of",
        "How would you apply the concept of",
        "What conclusions can be drawn about"
    ]
    
    topics = [
        "the introduction",
        "the methodology",
        "the results section",
        "the discussion",
        "the literature review",
        "the theoretical framework",
        "the case study",
        "the author's argument",
        "the data analysis",
        "the conclusion"
    ]

    categories = [
        "Explain Concept",
        "Definition",
        "Application",
        "Compare/Contrast"
    ]
    
    questions = []
    for i in range(count):
        question_type = random.choice(question_types)
        topic = random.choice(topics)
        category = random.choice(categories)
        question_text = f"{question_type} {topic}?"
        
        questions.append({
            "id": i + 1,
            "text": question_text,
            "category": category
        })
    
    return questions

def evaluate_answers(answers):
    # Answer scores is rated on a scale from 0 to 5
    scores = [random.randint(0, 5) for _ in answers]
    ids = [i + 1 for i in range(len(answers))]
    score_list = [{"id": i, "score": float(s)} for i, s in zip(ids, scores)]

    strengths = ["Biology", "Computer Science"]
    weaknesses = ["Mathematics"]

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "scores": score_list
    }
