import asyncio
import os
import json
from openai import OpenAI
from env import SupportEnv
from models import TriageAction

# Mandatory Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
TASK_NAME = os.getenv("SUPPORT_TASK_LEVEL", "hard")
BENCHMARK = "support_triage"

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = SupportEnv()
    
    rewards = []
    steps_taken = 0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        obs = await env.reset()
        max_possible_reward = len(env.inbox) * 1.0
        
        while len(obs.inbox) > 0 and steps_taken < 10:
            steps_taken += 1
            ticket = obs.inbox[0]
            
            prompt = f"Ticket ID: {ticket['id']}, Text: '{ticket['text']}'. \nClassify into category (refund, tech_support, billing, spam) and priority (low, high). Draft a short reply. Return ONLY a JSON like: {{\"category\": \"...\", \"priority\": \"...\", \"reply\": \"...\"}}"
            
            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                raw_response = completion.choices[0].message.content.strip()
                # quick and dirty parsing since LLMs sometimes add markdown
                clean_json = raw_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                
                action_str = f"tag_and_route({ticket['id']}, {data.get('category')})"
                action = TriageAction(
                    ticket_id=ticket['id'],
                    category=data.get('category', 'spam'),
                    priority=data.get('priority', 'low'),
                    reply_draft=data.get('reply', 'Hello.')
                )
                
                result = await env.step(action)
                obs = result.observation
                reward = result.reward
                done = result.done
                error = None
                
            except Exception as e:
                action_str = "error"
                reward = 0.0
                done = False
                error = str(e)
            
            rewards.append(reward)
            log_step(step=steps_taken, action=action_str, reward=reward, done=done, error=error)
            
            if done:
                break
                
        total_score = sum(rewards)
        normalized_score = total_score / max_possible_reward if max_possible_reward > 0 else 0.0
        success = normalized_score > 0.8
        
        log_end(success=success, steps=steps_taken, score=normalized_score, rewards=rewards)
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())