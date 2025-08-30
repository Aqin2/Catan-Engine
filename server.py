from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from catan import Game
from actions import create_action
from typing import Any
import json

app = FastAPI()

g = Game(['a', 'b', 'c', 'd'])

@app.get('/')
async def root():
    return {'message': json.dumps(g.to_json_obj())}

class ClientAction(BaseModel):
    action_type: str
    kwargs: dict[str, Any]

@app.post('/')
async def submit_action(client_action: ClientAction):
    action = create_action(client_action.action_type, client_action.kwargs)
    if action:
        return {}
    else:
        raise HTTPException(422)