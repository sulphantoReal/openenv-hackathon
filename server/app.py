from fastapi import FastAPI, Request
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