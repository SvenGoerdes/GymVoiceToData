from __future__ import annotations
import os
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field

class ExtractionResult(BaseModel):
    category: str = Field(..., description="The category of the data point, e.g., 'Körpergewicht'")
    value: float = Field(..., description="The numerical value, e.g., 80")
    unit: Optional[str] = Field(None, description="The unit of the value, e.g., 'kg'")

def extract_structured(text: str) -> ExtractionResult:
    """Return a structured dict from free-form text using OpenAI."""
    
    client = OpenAI()
    
    completion = client.beta.chat.completions.parse(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts structured data from text."},
            {"role": "user", "content": text},
        ],
        response_format=ExtractionResult,
    )
    
    return completion.choices[0].message.parsed
