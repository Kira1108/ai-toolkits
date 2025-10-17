# pydantic_models.py
from typing import List

from pydantic import BaseModel, Field

from ai_toolkits.files.planner import SplitPlanner
from ai_toolkits.structured.extractor import acreate_object_openai_safe
from ai_toolkits.llms.openai_provider import create_async_client


ANCHOR_FINDER_PROMPT = """
Semantically split the following text into smaller chunks by identifying the optimal split points(anchors).

Constraints:
1. when splitting based on the resulting anchors, each chunk should be between 500 - 1000 Chinese characters.
2. anchors are found according to the splitting plan provided.
3. do not need to add split anchors at the beginning or end of the text.

<splitting-plan>
{plan}
</splitting-plan>

Here is the text you need to semantically split:
<text>
{text}
</text>

You need to return a strcutured json object defined by SemanticSplitAnchors.
NOTE: each anchor sentence should be quoted EXACTLY from the original text, and it should be short enough(LESS THAN 15 Chinese characters is preferred) to be unique, but long enough to be meaningful.
UNIQUE SECTION HEADERS AS ANCHOR TEXTS ARE ALWAYS PREFERRED over other sentences.
"""




class SemanticSplitAnchors(BaseModel):
    """
    Identifies a full sentence within a text that serves as the optimal semantic split point.
    MOST IMPORTANT: the anchoor sentence shoule be shortest possible, but long enough to be unique.(LESS THAN 15 CHINESE CHARACTERS)
    """
    anchor_sentences: List[str] = Field(..., 
        description="A list of short strings, each quoted EXACTLY from the original text, where the split should occur. These sentence will be the begining of a new chunk."
    )
    
    
class AnchorFinder:
    
    def __init__(self):
        self.planner = SplitPlanner()
        self.client = create_async_client()

    async def run(self, text: str) -> SemanticSplitAnchors:
        
        print("Planning the split...")
        plan = await self.planner.run(document = text)
        print(f"Split plan: {plan}\n")
        print("Finding anchors based on the plan...")
        
        response = await acreate_object_openai_safe(
            output_cls=SemanticSplitAnchors,
            prompt=ANCHOR_FINDER_PROMPT.format(plan=plan, text=text),
            client=self.client
        )
        print(f"Anchor sentences found: {response.anchor_sentences}\n")
        return response
