import uvicorn
from fastapi import FastAPI, Request
# We need to import from the parent directory since this is now in the server/ folder
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import SupportEnv
from models import TriageAction

app = FastAPI()
env = SupportEnv()

@app.post("/reset")
async def reset(request: Request):
    return await env.reset()

@app.post("/step")
async def step(action: TriageAction):
    return await env.step(action)

@app.post("/state")
async def state_post(request: Request):
    return env.state()

@app.get("/state")
async def state_get():
    return env.state()

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()