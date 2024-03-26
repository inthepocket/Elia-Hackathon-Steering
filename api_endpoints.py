import json
import datetime
from typing import Union, List
from fastapi import APIRouter
from fastapi import Request
from pydantic import BaseModel

router = APIRouter()



@router.post("/process")
async def process(request: Request):
    
    body_dict = await request.json()
    print(body_dict)
    
    summary = body_dict.get("issue", {}).get("fields", {}).get("summary", None)
    
    with open(f"temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(body_dict, f)

    return {"summary": summary}


