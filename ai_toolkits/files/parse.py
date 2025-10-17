from markitdown import MarkItDown
from abc import ABC, abstractmethod

class BaseFileReader(ABC):
    
    @abstractmethod
    def read(self, fp:str) -> str:
        ...
        
class MarkDownFileReader(BaseFileReader):
    
    def __init__(self, **kwargs):
        if not kwargs.get("enable_plugins"):
            kwargs["enable_plugins"] = False
        self.md = MarkItDown(**kwargs)

    def read(self, fp: str) -> str:
        return self.md.convert(fp).text_content
    
    



