# processor.py
import PyPDF2, os, uuid
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM, BitsAndBytesConfig, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from transformers import pipeline
import numpy as np
from typing import List, Dict, Any

document_vectorstore = None
document_text = ""
text_chunks = []

device = "cuda:0" if torch.cuda.is_available() else "cpu"
pipeline_type = "text-generation" if torch.cuda.is_available() else "text2text-generation"
question_gen_model = None
question_gen_tokenizer = None
evaluation_model = None
evaluation_tokenizer = None

def initialize_models():
    global question_gen_model, question_gen_tokenizer, evaluation_model, evaluation_tokenizer
    
    if torch.cuda.is_available():
        question_model_name = "meta-llama/Llama-3.1-8B"
        bnb_config = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
        question_gen_model = AutoModelForCausalLM.from_pretrained(question_model_name,quantization_config=bnb_config)
    else:
        question_model_name = "google/flan-t5-base"
        question_gen_model = AutoModelForSeq2SeqLM.from_pretrained(question_model_name)

    question_gen_tokenizer = AutoTokenizer.from_pretrained(question_model_name)
    
    # eval_model_name = "google/flan-t5-base"  
    # evaluation_tokenizer = AutoTokenizer.from_pretrained(eval_model_name)
    # evaluation_model = AutoModelForSeq2SeqLM.from_pretrained(eval_model_name)
    evaluation_tokenizer = question_gen_tokenizer
    evaluation_model = question_gen_model
    
    print("Hugging Face models initialized successfully")

initialize_models()

async def save_file(file):
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_mapping = {}
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        contents = await file.read()
        buffer.write(contents)
    
    file_mapping[file.filename] = file_path
    
    process_pdf(file_path)
    
    return file_path
    
def process_pdf(file_path):
    global document_text, document_vectorstore, text_chunks
    
    document_text = extract_text_from_pdf(file_path)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    text_chunks = text_splitter.split_text(document_text)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    document_vectorstore = FAISS.from_texts(
        texts=text_chunks,
        embedding=embeddings
    )
    
    print(f"Processed document into {len(text_chunks)} chunks and created vector store")
    
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

def generate_questions(count: int):
    global document_vectorstore, text_chunks, question_gen_model, question_gen_tokenizer,device,pipeline_type
    
    if not document_vectorstore or not text_chunks:
        return generate_dummy_questions(count)
    
    question_gen_pipe = pipeline(
        pipeline_type, 
        model=question_gen_model, 
        tokenizer=question_gen_tokenizer,
        max_length=64,
        device=device
    )
    
    categories = [
        "Explain Concept",
        "Definition",
        "Application",
        "Compare/Contrast"
    ]
    
    category_prompts = {
        "Explain Concept": "Generate a question asking to explain a concept in this text: {text}",
        "Definition": "Generate a question asking for a definition from this text: {text}",
        "Application": "Generate a question about applying concepts from this text: {text}",
        "Compare/Contrast": "Generate a question comparing or contrasting ideas from this text: {text}"
    }
    
    questions = []
    
    sample_size = min(count, len(text_chunks))
    selected_chunks = np.random.choice(text_chunks, size=sample_size, replace=False)
    
    for i, chunk in enumerate(selected_chunks):
        if i >= count:
            break
            
        category = np.random.choice(categories)
        
        prompt_template = category_prompts[category]
        prompt = prompt_template.format(text=chunk[:200])
        
        try:
            question_text = question_gen_pipe(prompt)[0]["generated_text"]
            
            if not question_text.endswith("?"):
                question_text += "?"
            
            questions.append({
                "id": i + 1,
                "text": question_text,
                "category": category
            })
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            questions.append({
                "id": i + 1,
                "text": f"What is the main point of this excerpt: '{chunk[:50]}...'?",
                "category": category
            })
    
    if len(questions) < count:
        dummy_questions = generate_dummy_questions(count - len(questions))
        for i, q in enumerate(dummy_questions):
            q["id"] = len(questions) + i + 1
        questions.extend(dummy_questions)
        
    return questions

def generate_dummy_questions(count: int):
    # Keep original dummy question generation as fallback
    import random
    
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
    global document_vectorstore, evaluation_model, evaluation_tokenizer
    
    if not document_vectorstore:
        return _generate_random_evaluation(answers)
    
    try:
        eval_pipe = pipeline(
            "text2text-generation",
            model=evaluation_model,
            tokenizer=evaluation_tokenizer,
            max_length=100
        )
        
        retriever = document_vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        scores = []
        answer_analysis = {}
        
        for i, answer_obj in enumerate(answers):
            answer_id = i + 1
            answer_text = answer_obj.get("text", "")
            question_text = answer_obj.get("question", "Question not provided")
            category = answer_obj.get("category", "Unknown")
            
            try:
                contexts = retriever.get_relevant_documents(question_text)
                context_text = " ".join([doc.page_content for doc in contexts])
                
                eval_prompt = f"""
                Context: {context_text}
                
                Question: {question_text}
                
                Answer to evaluate: {answer_text}
                
                Evaluate the answer on a scale from 0 to 5, where:
                0: Completely incorrect or irrelevant
                1: Mostly incorrect with minor relevant elements
                2: Partially correct but missing key information
                3: Mostly correct with minor errors or omissions
                4: Correct but could be more comprehensive
                5: Completely correct and comprehensive
                
                Return only the numeric score.
                """
                
                eval_result = eval_pipe(eval_prompt)[0]["generated_text"]
                
                score_text = eval_result.strip()
                if score_text.replace('.', '', 1).isdigit():
                    score = float(score_text) 
                else:
                    digits = ''.join(filter(lambda c: c.isdigit() or c == '.', score_text))
                    score = float(digits) if digits else 3.0
                
                score = max(0, min(5, score))
                
                if category not in answer_analysis:
                    answer_analysis[category] = {"scores": [], "total": 0}
                
                answer_analysis[category]["scores"].append(score)
                answer_analysis[category]["total"] += score
                
            except Exception as e:
                print(f"Error evaluating answer {answer_id}: {str(e)}")
                score = 3.0  
            
            scores.append({"id": answer_id, "score": score})
        
        for category in answer_analysis:
            if answer_analysis[category]["scores"]:
                answer_analysis[category]["average"] = answer_analysis[category]["total"] / len(answer_analysis[category]["scores"])
            else:
                answer_analysis[category]["average"] = 0
        
        sorted_categories = sorted(
            [(cat, data["average"]) for cat, data in answer_analysis.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        strengths = [cat for cat, score in sorted_categories if score >= 3.0][:2]
        weaknesses = [cat for cat, score in sorted_categories if score < 3.0]
        
        if not strengths:
            strengths = ["None identified"]
        if not weaknesses:
            weaknesses = ["None identified"]
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "scores": scores
        }
        
    except Exception as e:
        print(f"Error in evaluation process: {str(e)}")
        return _generate_random_evaluation(answers)

def _generate_random_evaluation(answers):
    import random
    
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