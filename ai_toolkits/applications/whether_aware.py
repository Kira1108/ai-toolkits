"""
This example demonstrates how to inject external context (the weather) into an agent's system prompt.
"""

from dataclasses import dataclass
from ai_toolkits.llms.pydantic_provider.models import create_ollama_model
import random

from pydantic_ai import Agent, RunContext


@dataclass
class MyDeps:
    whether: str

def create_whether_aware_agent() -> Agent:
    agent = Agent(
        model = create_ollama_model(),
        deps_type=MyDeps,
    )

    @agent.system_prompt  
    async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:  
        return (f'Responde to user, if the whether is sunny, you should say: 😊 followed by your response.'
                f'if not sunny you should say: 😞 followed by your response.'
                f"Now today's whether is {ctx.deps.whether}")
    return agent
    
async def run_whether_aware_agent(prompt:str, agent = None, whether: str = None):
    if agent is None:
        agent = create_whether_aware_agent()
    if whether is None:
        whether = random.choice(["Sunny", "Rainy", "Cloudy"])
    deps = MyDeps(whether=whether)
    result = await agent.run(prompt, deps=deps)
    print(result.output)