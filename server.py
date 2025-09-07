from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from catan import Game
from actions import create_action
from typing import Any
import json
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

g = Game(['a', 'b', 'c', 'd'])

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    #TODO: wait for user credentials here (eventually)

    await websocket.send_json(g.to_json_obj())

    while True:
        action = await websocket.receive_json()
        action = create_action(action['action_type'], action['kwargs'])
        g.step(action)
        await websocket.send_json(g.to_json_obj())
