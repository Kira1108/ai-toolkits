import instructor
from pydantic import BaseModel
from openai import Client

def create_object_openai(
    output_cls:BaseModel, 
    prompt:str, 
    client:Client = None):
    if not client:
        raise ValueError("Please provide an OpenAI client.")
    
    client = instructor.from_openai(client)
    return client.chat.completions.create(
        model="gpt-4o",
        response_model=output_cls,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    

class ErrorResponse(BaseModel):
    error: str


async def acreate_object_openai(
    output_cls:BaseModel, 
    prompt:str, 
    client:Client = None) -> BaseModel:
    if not client:
        raise ValueError("Please provide an OpenAI client.")
    
    client = instructor.from_openai(client)
    return await client.chat.completions.create(
        model="gpt-4o",
        response_model=output_cls,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    
async def acreate_object_openai_safe(
    output_cls:BaseModel,
    prompt:str,
    client:Client = None):
    try:
        return await acreate_object_openai(output_cls, prompt, client)
    except Exception as e:
        return ErrorResponse(error=str(e))