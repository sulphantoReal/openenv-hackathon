import os
from models import TriageAction, TriageObservation, StepResult

class SupportEnv:
    def __init__(self):
        self.task_level = os.getenv("SUPPORT_TASK_LEVEL", "easy")
        self.state_data = {}
        self._load_task()

    def _load_task(self):
        # 3 tasks with difficulty range
        if self.task_level == "easy":
            self.inbox = [
                {"id": "T1", "text": "My screen is cracked, need a replacement ASAP!!"}
            ]
            self.expected = {"T1": {"cat": "tech_support", "pri": "high"}}
        elif self.task_level == "medium":
            self.inbox = [
                {"id": "T1", "text": "My screen is cracked, need a replacement ASAP!!"},
                {"id": "T2", "text": "Can I get a refund for my last invoice?"},
                {"id": "T3", "text": "Win a free iPhone click here"}
            ]
            self.expected = {
                "T1": {"cat": "tech_support", "pri": "high"},
                "T2": {"cat": "billing", "pri": "low"},
                "T3": {"cat": "spam", "pri": "low"}
            }
        else: # hard
            self.inbox = [
                {"id": "T1", "text": "Screen cracked."},
                {"id": "T2", "text": "Refund invoice #4421."},
                {"id": "T3", "text": "Win a free iPhone."},
                {"id": "T4", "text": "The app keeps crashing when I try to upload a PDF."},
                {"id": "T5", "text": "I was charged twice yesterday, I am furious and will sue!"}
            ]
            self.expected = {
                "T1": {"cat": "tech_support", "pri": "low"},
                "T2": {"cat": "billing", "pri": "low"},
                "T3": {"cat": "spam", "pri": "low"},
                "T4": {"cat": "tech_support", "pri": "high"},
                "T5": {"cat": "billing", "pri": "high"}
            }
        
        self.total_tickets = len(self.inbox)
        self.resolved = 0
        self.current_score = 0.0
        self.state_data = {"episode_id": "ep_1", "step_count": 0}

    async def reset(self):
        self._load_task()
        return TriageObservation(
            inbox=self.inbox, 
            system_message="Inbox loaded. Triage tickets.", 
            tickets_resolved=self.resolved
        )

    async def step(self, action: TriageAction):
        self.state_data["step_count"] += 1
        reward = 0.0
        
        # Check if ticket exists in current inbox
        target = next((t for t in self.inbox if t["id"] == action.ticket_id), None)
        
        if target:
            # Grader logic: Partial progress reward
            exp = self.expected[action.ticket_id]
            if action.category == exp["cat"]:
                reward += 0.5
            if action.priority == exp["pri"]:
                reward += 0.3
            if len(action.reply_draft) > 10: # basic check for drafted text
                reward += 0.2

            self.inbox.remove(target)
            self.resolved += 1
            self.current_score += reward

        done = len(self.inbox) == 0
        
        # Normalize reward between 0.0 and 1.0 for the step grader requirement
        normalized_step_reward = max(0.01, min(reward, 0.99))

        obs = TriageObservation(
            inbox=self.inbox, 
            system_message=f"Processed {action.ticket_id}", 
            tickets_resolved=self.resolved
        )
        
        return StepResult(observation=obs, reward=normalized_step_reward, done=done)

    def state(self):
        return self.state_data