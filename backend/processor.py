import PyPDF2, random

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
    
    questions = []
    for i in range(count):
        question_type = random.choice(question_types)
        topic = random.choice(topics)
        question_text = f"{question_type} {topic}?"
        
        questions.append({
            "id": i + 1,
            "text": question_text,
            "difficulty": random.choice(["Easy", "Medium", "Hard"]),
            "category": random.choice(["Comprehension", "Analysis", "Application", "Evaluation"])
        })
    
    return questions