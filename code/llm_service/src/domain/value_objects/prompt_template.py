from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class PromptTemplate:
    """Prompt template value object"""
    template: str
    variables: Dict[str, Any]
    
    def render(self) -> str:
        """Render template with variables"""
        return self.template.format(**self.variables)
