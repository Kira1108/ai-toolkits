"""This is an exmaple of agent-as-tool pattern, where one agent calls another agent as a tool to complete a task."""

from pydantic_ai import Agent, RunContext, UsageLimits
from ai_toolkits.llms.pydantic_provider.models import create_ollama_model

def create_joke_agents():
    # first, create a joke selection agent
    joke_selection_agent = Agent(  
        create_ollama_model(),
        system_prompt=(
            'Use the `joke_factory` to generate some jokes, then choose the best. '
            'You must return just a single joke.'
        ),
    )
    
    # then create a joke generation agent, this agent will be called by the first agent as a tool 
    joke_generation_agent = Agent(  
        create_ollama_model(), 
        output_type=list[str]
    )


    # wrap the joke generation agent as a tool for the joke selection agent
    @joke_selection_agent.tool
    async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
        r = await joke_generation_agent.run(  
            f'Please generate {count} jokes. The jokes should be short and funny in Chinese.',
            usage=ctx.usage,  
        )
        return r.output  
    
    # we only need to run the joke selection agent
    return joke_selection_agent

def run_joke_generation():
    return create_joke_agents().run_sync(
        'Tell me a joke.',
        usage_limits=UsageLimits(request_limit=5, total_tokens_limit=5000),
    )
