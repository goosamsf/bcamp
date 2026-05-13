from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ConceptExplanation(BaseModel):
    difficulty: DifficultyLevel
    explanation: str
    analogy: Optional[str] = None


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER


class EducationalContent(BaseModel):
    protocol_name: str
    what_it_is: str = ""
    what_it_does_in_this_capture: str = ""
    layered_explanations: List[ConceptExplanation] = Field(default_factory=list)
    real_world_analogy: str = ""
    why_it_matters: str = ""
    interesting_fact: str = ""
    quiz_questions: List[QuizQuestion] = Field(default_factory=list)
    related_protocols: List[str] = Field(default_factory=list)
    rag_sources: List[str] = Field(default_factory=list)
