import random
from dataclasses import dataclass, field
from typing import List, Optional, Protocol
from ai_toolkits.llms.openai_provider import create_sync_client
from faker import Faker

class PersonalAxis(Protocol):
    axis_name: str
    
    def get(self) -> str:
        """Get axis value as string"""


@dataclass
class DiscreteAxis:
    
    axis_name: str
    options: Optional[List[str]] = None
    
    def get(self):
        return random.choice(self.options)
    
@dataclass
class FakerAxis:
    axis_name: str
    lang:str = "zh_CN"
    faker_method: str = "name"
    
    def __post_init__(self):
        self.faker = Faker(self.lang)
        if not hasattr(self.faker, self.faker_method):
            raise ValueError(f"Faker does not have method {self.faker_method}")
    
    def get(self):
        method = getattr(self.faker, self.faker_method)
        return method()
    
    
@dataclass
class IntAxis:
    axis_name: str
    min_value: int = 0
    max_value: int = 10
    
    def get(self):
        return str(random.randint(self.min_value, self.max_value))
    
PATIENCE = DiscreteAxis(
    axis_name="patience",
    options = [
        "Serene",
        "Extremely Patient",
        "Very Forbearing",
        "Understanding",
        "Composed",
        "Tolerant",
        "Easygoing",
        "Relaxed",
        "Neutral",
        "A Bit Hurried",
        "Restless",
        "Fidgety",
        "Eager",
        "In a Rush",
        "Demanding",
        "Insistent",
        "Agitated",
        "Edgy",
        "Short-tempered",
        "Extremely Impatient"
  ])

CLARITY = DiscreteAxis(
    axis_name="clarity",
    options =  [
    "Eloquent",
    "Lucid",
    "Articulate",
    "Extremely Clear",
    "Precise",
    "Coherent",
    "Methodical",
    "Straightforward",
    "Focused",
    "Generally Clear",
    "Slightly Hesitant",
    "Vague",
    "Ambiguous",
    "Disorganized",
    "Muddled",
    "Scattered",
    "Jumbled",
    "Rambling",
    "Confusing",
    "Incoherent"
  ])

VERBOSITY = DiscreteAxis(
    axis_name="verbosity",
    options = [
    "Garrulous (Extremely Talkative)",
    "Loquacious",
    "Story-telling",
    "Very Chatty",
    "Expressive",
    "Descriptive",
    "Communicative",
    "Slightly Wordy",
    "Balanced",
    "To the Point",
    "Concise",
    "Succinct",
    "Brief",
    "Pithy",
    "Terse",
    "Reserved",
    "Reticent",
    "Quiet",
    "Taciturn (Almost Silent)",
    "Mute"
  ])

POLITENESS = DiscreteAxis(
    axis_name="politeness",
    options = [
    "Gracious",
    "Extremely Courteous",
    "Charming",
    "Respectful",
    "Cordial",
    "Friendly",
    "Considerate",
    "Formal",
    "Neutral / Business-like",
    "Informal",
    "Casual",
    "Direct",
    "Blunt",
    "Curt",
    "Abrupt",
    "Sarcastic",
    "Demanding",
    "Disrespectful",
    "Hostile",
    "Aggressive"
  ])

EXPERTISE = DiscreteAxis(
    axis_name="expertise",
    options = [
    "Subject Matter Expert",
    "Masterful",
    "Authoritative",
    "Highly Experienced",
    "Professional",
    "Well-versed",
    "Knowledgeable",
    "Informed",
    "Confident",
    "Has Basic Understanding",
    "Average User",
    "Inexperienced",
    "Beginner",
    "Novice",
    "Uncertain",
    "Guessing",
    "Misinformed",
    "Confused",
    "Uninformed",
    "Completely Clueless"
  ])


MBTI = DiscreteAxis(
    axis_name="mbti",
    options = [
        "INTJ-known as the Architect, is characterized by high independence, strategic thinking, and a strong focus on long-term goals.",
        "INTP-known as the Thinker, is characterized by a love of problem-solving and a desire to understand the world around them.",
        "ENTJ-known as the Commander, is characterized by strong leadership skills and a focus on efficiency and results.",
        "ENTP-known as the Debater, is characterized by a love of intellectual challenge and a desire to explore new ideas.",
        "INFJ-known as the Advocate, is characterized by a deep sense of empathy and a desire to help others.",
        "INFP-known as the Mediator, is characterized by a strong sense of idealism and a desire for harmony.",
        "ENFJ-known as the Protagonist, is characterized by strong leadership skills and a desire to inspire and motivate others.",
        "ENFP-known as the Campaigner, is characterized by a love of adventure and a desire to explore new possibilities.",
        "ISTJ-known as the Logistician, is characterized by a strong sense of duty and a focus on practicality and reliability.", 
        "ISFJ-known as the Defender, is characterized by a strong sense of loyalty and a desire to protect and care for others.",
        "ESTJ-known as the Executive, is characterized by strong leadership skills and a focus on organization and efficiency.", 
        "ESFJ-known as the Consul, is characterized by a strong sense of community and a desire to help others.",
        "ISTP-known as the Virtuoso, is characterized by a love of hands-on problem-solving and a desire for independence.",
        "ISFP-known as the Adventurer, is characterized by a love of beauty and a desire for new experiences.",
        "ESTP-known as the Entrepreneur, is characterized by a love of excitement and a desire for action.",
        "ESFP-known as the Entertainer, is characterized by a love of fun and a desire to connect with others."
    ]
)

NAME = FakerAxis(
    axis_name="name",
    faker_method="name"
)

ADDRESS = FakerAxis(
    axis_name="address",
    faker_method="address"
)

JOB = FakerAxis(
    axis_name="job",
    faker_method="job"
)

AGE = IntAxis(axis_name="age", min_value=18, max_value=70)

@dataclass
class PersonaProfile:
    """
    A persona profile consisting of various personality axes.
    """
    axes: List[PersonalAxis] = field(
        default_factory=lambda: [
            PATIENCE, CLARITY, VERBOSITY, 
            POLITENESS, EXPERTISE, MBTI, NAME, 
            ADDRESS, JOB, AGE]
    )
    language:str = "简体中文"
    
    def __post_init__(self):
        self.persona = self.generate()
        
    def generate(self):
        return {axis.axis_name: axis.get() for axis in self.axes}
    
    def __getitem__(self, key):
        if not key in self.persona:
            raise KeyError(f"Key {key} not in persona profile")
        return self.persona[key]
    
    @property
    def name(self):
        return self.persona.get("name", "Unknown")
        
    def as_list(self):
        persona_items = [f"{k.title()}: {v}" for k,v in self.persona.items()]
        persona_items.append(f"Language: {self.language}.")
        return persona_items
    
    def as_prompt(self, 
            identifier:str = "Persona Profile"):
        profile = "\n".join(self.as_list())
        profile = f"<{identifier}>\n" + profile + f"\n</{identifier}>"
        return profile
    

@dataclass
class OpenAIChatter:
    
    persona:str = None
    opponent_persona:str = "Unknown"
    scenario:str = "Undefined"
    
    def __post_init__(self):
        if not self.persona:
            self.persona = PersonaProfile().as_prompt()

        if not self.opponent_persona:
            self.opponent_persona = "Unknown"
            
        self.client = create_sync_client()

        self.system_prompt = (
            "You are chatting with someone, do talk like a human in colloquial style, continue the conversation. your persona is given by:\n"
            f"{self.persona}"
            f"Mimic real human conversations, be engaging and interesting."
            f"The person you are talking to has the following profile:\n"
            f"{self.opponent_persona}"
            f"Conversation scenario is given by:\n"
            f"{self.scenario}\n"
            "Since you are talking via telephone, do not reply long messages, keep it simple, short and communicative. less than 50 Chinese characters is preferred."
            "Do follow your persona instruction"
        )
        self.messages = [
            {'role': "system","content": self.system_prompt}
        ]
        
    def greeting(self):
        return self.client.chat.completions.create(
            model = 'gpt-4.1',
            messages= self.messages + [{'role':"user", "content":"First, generate a greeting message to start a conversation."}],
        ).choices[0].message.content
    
    def add_user_message(self, message:str):
        self.messages.append({"role":"user", "content":message})
        
    def add_assistant_message(self, message:str):
        self.messages.append({'role':"assistant", "content": message})
        
        
    def _retry_chat(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"Retrying chat, attempt {attempt+1}...")
                response = self.client.chat.completions.create(
                    model = 'gpt-4.1',
                    messages= self.messages,
                )
                if response.choices[0].message.content:
                    return response
                
                raise ValueError("Empty response content")
            except Exception as e:
                print(f"Chat attempt {attempt+1} failed: {e}")
        raise RuntimeError("Max retries exceeded for chat.")
    
    def chat(self, message:str = None):
        self.add_user_message(message)
        response = self._retry_chat()
        content = response.choices[0].message.content
        
        self.add_assistant_message(content)
        return content
    
    
class ConversationSimulator:
    
    def __init__(self):
        self.persona1 = PersonaProfile()
        self.persona2 = PersonaProfile()
        self.scenario = self.create_scenerio(self.persona1.as_prompt(), self.persona2.as_prompt())
        self.chatter1 = OpenAIChatter(persona=self.persona1.as_prompt(), opponent_persona=self.persona2.as_prompt(), scenario=self.scenario)
        self.chatter2 = OpenAIChatter(persona=self.persona2.as_prompt(), opponent_persona=self.persona1.as_prompt(), scenario=self.scenario)
        
    def create_scenerio(self,persona1, persona2):

        client = create_sync_client()

        return client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': f"Give person1 with persona:\n{persona1}\n and person2 with persona:\n{persona2}\n I want you to generate a scenerio for them to chat with each other in Chinese, 50 characters.(Note they are taking via telephone"},
            ]
        ).choices[0].message.content

    def start_conversation(self, max_turns=10):
        greeting = self.chatter1.greeting()
        self.chatter1.add_assistant_message(greeting)
        reply2 = self.chatter2.chat(greeting)
        print(f"{self.persona1.name} (A):", greeting)
        print(f"{self.persona2.name} (B):", reply2)

        for turn in range(max_turns):
            reply1 = self.chatter1.chat(reply2)
            print(f"{self.persona1.name} (A):", reply1)
            reply2 = self.chatter2.chat(reply1)
            print(f"{self.persona2.name} (B):", reply2)

            if "再见" in reply1 or "再见" in reply2:
                print("Conversation ended.")
                break
            if "拜拜" in reply1 or "拜拜" in reply2:
                print("Conversation ended.")
                break