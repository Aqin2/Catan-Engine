from fastapi import FastAPI, HTTPException
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
    allow_methods=['*']
)

g = Game(['a', 'b', 'c', 'd'])

@app.get('/')
async def root():
    return g.to_json_obj()

class ClientAction(BaseModel):
    action_type: str
    kwargs: dict[str, Any]

@app.post('/')
async def submit_action(client_action: ClientAction):
    print(client_action)
    action = create_action(client_action.action_type, client_action.kwargs)
    if action:
        return g.step(action)
    else:
        raise HTTPException(422)