from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    id: int
    text: str
    category: str

class Answer(BaseModel):
    id: int
    text: str

class Score(BaseModel):
    id: int
    score: float

'''
    Request and Response Objects Start Here
'''
class GenerateQuestionsRequest(BaseModel):
    questionCount: int

class GenerateQuestionsResponse(BaseModel):
    questions: List[Question]

class SubmitAnswersRequest(BaseModel):
    answers: List[Answer]

class SubmitAnswersResponse(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    scores: List[Score]