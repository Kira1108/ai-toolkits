from pydantic import BaseModel
from pydantic_ai import Agent
from ai_toolkits.llms.pydantic_provider.models import create_ollama_model

class HangupPhoneCall(BaseModel):
    """create a action to hangup the phone call"""
    
class MailBoxMessage(BaseModel):
    """
    An outbound call to the user but not answered, encountered a voicemail system, in this case, we need to 
    leave a message in the mailbox, the message will be send to the user later
    
    """
    message: str = "您好，这里是兴业银行，给你致电想了解一下资金需求，有空可以回电，电话是13512345678"
    
class TransferToHumanCustomerService(BaseModel):
    """Transfer the call to a human customer service"""

def create_call_agent():
    return Agent(
        create_ollama_model(), 
        output_type= HangupPhoneCall | MailBoxMessage | TransferToHumanCustomerService | str,
        system_prompt=("You are a customer service representative in a bank, the name of bank is `北京银行`. "
                    "Answer the question as best as you can. If you want to end the call,"
                    "or the user says goodbye, call the HangupPhoneCall action with do_hangup=True"  
                    "If the phone is not answered and you encounter a voicemail system,  do create a MailBoxMessage"
                    "If the user asks to talk to a human customer service, do create a TransferToHumanCustomerService action"
                    "otherwise, just answer the question."
    ))