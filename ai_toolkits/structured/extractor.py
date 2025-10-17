import asyncio

import instructor
from openai import Client, AsyncClient
from pydantic import BaseModel
from ai_toolkits.llms import create_async_client
import logging

logger = logging.getLogger(__name__)

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

    logger.info(f"Creating object of type {output_cls.__name__} with prompt: {prompt[:30]}...")  # Log the prompt (truncated for brevity)
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
        print("Object Creation failed:", str(e))
        return ErrorResponse(error=str(e))


async def acreate_objects_openai_safe(
    prompt:str, 
    output_classes:list[BaseModel],
    client:AsyncClient = None) -> dict:
    
    if client is None:
        client = create_async_client()
    
    """
    Give a conversation between a police officer and a civilian, classify the case into multiple categories.
    The output is defined by a series of pydantic models.
    
    Args:
        conversation (str): The conversation text to be analyzed.

    Returns: A dictionary where keys are the names of the classification categories
        and values are the corresponding classification results.
    """
    class_names = [cls.__name__ for cls in output_classes]
    
    tasks = [
        acreate_object_openai_safe(
            output_cls=cls, 
            prompt=prompt,
            client=client
        )
        for cls in output_classes
    ]
    
    objects = await asyncio.gather(*tasks)
    
    return {
        class_name: obj.model_dump() 
        for class_name, obj in zip(class_names, objects)
    }
