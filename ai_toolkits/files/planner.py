from dataclasses import dataclass, field
from openai import AsyncClient
from ai_toolkits.llms.openai_provider import (
    create_async_client,
)


PLAN_PROMPT = """
Given a document, you need to generate a plan on how to split it into chunks.

Principles:
1. If the document has section headers, explain how sections look like, the pattern of section headers.
2. Based on the section content, determine the granularity of splitting, for example, split on top-level headers like 1. 2. 3. or 1.1 1.2 ....
3. IF the document does not have section headers, explain how to split it based on the content(Semantical chunking)
3. briefly explain the main content of the document.

Output:
Your output should contain the following parts:
1. split strategy: a brief description of how to split the document, section header patterns, and granularity.
2. document summary: a brief summary of the document content.

Note:
Your output should be less than 300 Chinese characters, So you have to make it brief and concise.

Here is the document you need to plan for chunking
<document>
{document}
</document>
"""

@dataclass
class SplitPlanner:
    
    client: AsyncClient = field(default_factory=create_async_client)
    
    async def run(self, document:str) -> str:
        """
        Create a split plan for the given document.
        
        Args:
            document (str): The document to create a split plan for.
        
        Returns:
            str: The split plan as a string.
        """
        prompt = PLAN_PROMPT.format(document=document)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0)
        
        if response:
            response = response.choices[0].message.content
            
        return response
