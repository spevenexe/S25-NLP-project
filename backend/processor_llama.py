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
from transformers.pipelines.base import Pipeline
import numpy as np
import traceback
from typing import List

document_vectorstore = None
document_text = ""
text_chunks = []

questions = []

question_gen_model = None
question_gen_tokenizer = None
evaluation_model = None
evaluation_tokenizer = None

def initialize_models():
    global question_gen_model, question_gen_tokenizer, evaluation_model, evaluation_tokenizer
    
    question_model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    bnb_config = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    question_gen_model = AutoModelForCausalLM.from_pretrained(question_model_name,quantization_config=bnb_config)
    question_gen_tokenizer = AutoTokenizer.from_pretrained(question_model_name)
    
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
    global document_vectorstore, text_chunks, question_gen_model, question_gen_tokenizer, questions
    
    if not document_vectorstore or not text_chunks:
        return generate_dummy_questions(count)
    
    question_gen_pipe = pipeline(
        "text-generation",
        model=question_gen_model, 
        tokenizer=question_gen_tokenizer,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    terminators = [
        question_gen_pipe.tokenizer.eos_token_id,
        question_gen_pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    
    categories = [
        "Explain Concept",
        "Definition",
        "Application",
        "Compare/Contrast"
    ]
    
    category_prompts = {
        "Explain Concept": "Generate a question asking to explain a concept from this excerpt",
        "Definition": "Generate a question asking for a definition from this excerpt",
        "Application": "Generate a question about applying concepts from this excerpt",
        "Compare/Contrast": "Generate a question comparing or contrasting ideas from this excerpt"
    }
    
    prompt_template = "Consider the following excerpt, which is surrounded by lines of \"###\":\n###\n{text}\n###\n{category}. Do not print anything else. Do not mention the excerpt, the text, or the author. The question should be standalone."
    
    questions = []
    
    sample_size = min(count, len(text_chunks))
    selected_chunks = np.random.choice(text_chunks, size=sample_size, replace=False)
    
    for i, chunk in enumerate(selected_chunks):
        if i >= count:
            break
            
        category = np.random.choice(categories)
        
        category_question = category_prompts[category]
        prompt = prompt_template.format(text=chunk[:200],category=category_question)
        
        messages = [
            {"role": "system", "content": "You are a helpful chatbot who generates flashcard-like quiz questions."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            outputs = question_gen_pipe(
                    messages,
                    max_new_tokens=64,
                    eos_token_id=terminators,
                    pad_token_id = question_gen_pipe.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )[0]["generated_text"]
            
            question_text = outputs[-1]['content']
            
            if not question_text.endswith("?"):
                question_text += "?"
            
            questions.append({
                "id": i + 1,
                "text": question_text,
                "category": category,
                "dialogue" : outputs
            })
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            questions.append({
                "id": i + 1,
                "text": f"What is the main point of this excerpt: '{chunk[:50]}...'?",
                "category": category,
                "dialogue" : []
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

def regenerate_tailored_questions(count: int, weaknesses: List[str]):
    global document_vectorstore, text_chunks, question_gen_model, question_gen_tokenizer, questions
    print(weaknesses) 
    
    if not document_vectorstore or not text_chunks:
        return generate_dummy_questions(count)
    
    question_gen_pipe = pipeline(
        "text-generation",
        model=question_gen_model, 
        tokenizer=question_gen_tokenizer,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    terminators = [
        question_gen_pipe.tokenizer.eos_token_id,
        question_gen_pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    
    categories = [
        "Explain Concept",
        "Definition",
        "Application",
        "Compare/Contrast"
    ]
    
    category_prompts = {
        "Explain Concept": "Generate a question asking to explain a concept from this excerpt",
        "Definition": "Generate a question asking for a definition from this excerpt",
        "Application": "Generate a question about applying concepts from this excerpt",
        "Compare/Contrast": "Generate a question comparing or contrasting ideas from this excerpt"
    }
    
    prompt_template = "Consider the following excerpt, which is surrounded by lines of \"###\":\n###\n{text}\n###\n{category}. The question should be focused on one of the listed topcs:\n{weaknesses}\n Do not print anything else. Do not mention the excerpt, the text, or the author. The question should be standalone."
    
    bulleted_weak_topics = '- ' + '\n- '.join(w for w in weaknesses)
    
    questions = []
    
    sample_size = min(count, len(text_chunks))
    selected_chunks = np.random.choice(text_chunks, size=sample_size, replace=False)
    
    for i, chunk in enumerate(selected_chunks):
        if i >= count:
            break
            
        category = np.random.choice(categories)
        
        category_question = category_prompts[category]
        prompt = prompt_template.format(text=chunk[:200],category=category_question,weaknesses=bulleted_weak_topics)
        
        messages = [
            {"role": "system", "content": "You are a helpful chatbot who generates flashcard-like quiz questions."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            outputs = question_gen_pipe(
                    messages,
                    max_new_tokens=64,
                    eos_token_id=terminators,
                    pad_token_id = question_gen_pipe.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )[0]["generated_text"]
            
            question_text = outputs[-1]['content']
            
            if not question_text.endswith("?"):
                question_text += "?"
            
            questions.append({
                "id": i + 1,
                "text": question_text,
                "category": category,
                "dialogue" : outputs
            })
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            questions.append({
                "id": i + 1,
                "text": f"What is the main point of this excerpt: '{chunk[:50]}...'?",
                "category": category,
                "dialogue" : []
            })
    
    if len(questions) < count:
        dummy_questions = generate_dummy_questions(count - len(questions))
        for i, q in enumerate(dummy_questions):
            q["id"] = len(questions) + i + 1
        questions.extend(dummy_questions)
        
    return questions

def evaluate_answers(answers):
    global document_vectorstore, evaluation_model, evaluation_tokenizer, questions
    
    if not document_vectorstore:
        return _generate_random_evaluation(answers)
    
    try:
        eval_pipe = pipeline(
            "text-generation",
            model=question_gen_model, 
            tokenizer=question_gen_tokenizer,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
        terminators = [
            eval_pipe.tokenizer.eos_token_id,
            eval_pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        retriever = document_vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        scores = []
        answer_analysis = {}
        topics = []
        
        for i, answer_obj in enumerate(answers):
            answer_id = i + 1
            answer_text = answer_obj.text
            question_i = [q for q in questions if q["id"] == answer_id][0]
            question_text = question_i["text"]
            category = question_i["category"]
            dialogue = question_i["dialogue"]
            
            try:
                # contexts = retriever.get_relevant_documents(question_text)
                # context_text = " ".join([doc.page_content for doc in contexts])
                
                eval_prompt = f"""
                This is my answer:
                {answer_text}
                
                Evaluate the answer on a scale from 0 to 5, where:
                0: Completely incorrect or irrelevant
                1: Mostly incorrect with minor relevant elements
                2: Partially correct but missing key information
                3: Mostly correct with minor errors or omissions
                4: Correct but could be more comprehensive
                5: Completely correct and comprehensive
                
                Return only the numeric score.
                """
                
                messages = dialogue + [{
                    "role":"user",
                    "content":eval_prompt
                }]
                
                outputs = eval_pipe(
                    messages,
                    max_new_tokens=64,
                    eos_token_id=terminators,
                    pad_token_id = eval_pipe.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )[0]["generated_text"]
                
                eval_result:str = outputs[-1]['content']
                
                score_text = eval_result.strip()
                if score_text.replace('.', '', 1).isdigit():
                    score = float(score_text) 
                else:
                    digits = ''.join(filter(lambda c: c.isdigit() or c == '.', score_text))
                    score = float(digits) if digits else 3.0
                
                score = max(0, min(5, score))
                
                # get study topics
                topic_prompt = \
                """
                What specific field of study would you say this topic is in? {existing}Just print the field of study and nothing else.
                """
                existing = '' if len(answer_analysis) == 0 else \
                    "This is a list of idenitified topics:\n{categories}\nIf the field of study matches one of these, print the element exactly. Otherwise, list its field of study. "
                cat_list = '- ' + '\n- '.join(c for c in answer_analysis.keys())
                existing = existing.format(categories=cat_list)
                topic_prompt = topic_prompt.format(existing=existing)
                    
                messages = outputs
                messages.append(
                    {
                        "role": "user", 
                        "content": topic_prompt
                    },
                    )
                
                outputs = eval_pipe(
                    messages,
                    max_new_tokens=64,
                    eos_token_id=terminators,
                    pad_token_id = eval_pipe.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )[0]["generated_text"]
                
                category = outputs[-1]['content']
                if category not in answer_analysis:
                    answer_analysis[category] = {"scores": [], "total": 0}
                
                answer_analysis[category]["scores"].append(score)
                answer_analysis[category]["total"] += score
                
            except Exception as e:
                print(f"Error evaluating answer {answer_id}:")
                print(traceback.format_exc())
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