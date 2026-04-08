from pydantic import BaseModel
from typing import List, Dict, Optional

class TriageAction(BaseModel):
    ticket_id: str
    category: str  # Options: 'refund', 'tech_support', 'billing', 'spam'
    priority: str  # Options: 'low', 'high'
    reply_draft: str

class TriageObservation(BaseModel):
    inbox: List[Dict[str, str]]
    system_message: str
    tickets_resolved: int

class StepResult(BaseModel):
    observation: TriageObservation
    reward: float
    done: bool
    info: Optional[Dict] = None