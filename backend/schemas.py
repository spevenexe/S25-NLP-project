from pydantic import BaseModel
from typing import List, Optional, Union

class GenerateQuestionsRequest(BaseModel):
    questionCount: int

class RegenerateTailoredQuestionsRequest(BaseModel):
    questionCount: int
    weaknesses: List[str]

class Question(BaseModel):
    id: int
    text: str
    category: str

class ExtendedQuestion(Question):
    dialogue: List[str]

class GenerateQuestionsResponse(BaseModel):
    questions: List[Union[Question, ExtendedQuestion]]

class AnswerSubmission(BaseModel):
    id: Optional[int] = None
    text: str
    question: Optional[str] = None
    category: Optional[str] = None

class ScoreItem(BaseModel):
    id: int
    score: float

class SubmitAnswersRequest(BaseModel):
    answers: List[AnswerSubmission]

class SubmitAnswersResponse(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    scores: List[ScoreItem]

class GenerateAnswerRequest(BaseModel):
    question: str

class GenerateAnswerResponse(BaseModel):
    answer: str