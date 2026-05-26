from fastapi import APIRouter, Depends
import logging
from pydantic import BaseModel
from typing import Optional

from app.engines.llm_layer import gemini_model, extract_json_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter()

class GenerateTestcasesRequest(BaseModel):
    code: str
    language: str
    problem_desc: Optional[str] = None

@router.post("/testcases/generate", summary="AI-generated Test Cases")
def generate_ai_testcases(payload: GenerateTestcasesRequest):
    """
    POST /api/testcases/generate
    Calls Gemini to generate 5 edge cases based on given code.
    """
    problem_ctx = f"The student is trying to solve: {payload.problem_desc}\n" if payload.problem_desc else ""
    
    prompt = f"Given the following {payload.language} code, generate exactly 5 diverse test inputs. " \
             f"Return ONLY a JSON array, where each object has 'input', 'expected_output', and 'label'.\n" \
             f"{problem_ctx}" \
             f"CODE:\n{payload.code}"
    
    if not gemini_model:
        return [{"input": "", "expected_output": "?", "label": "Mock LLM test case (API missing)"}]
        
    try:
        import google.generativeai as genai
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=600,
                temperature=0.3,
            )
        )
        text = response.text
        
        # We can loosely reuse extract JSON, but it expects a dict. Here we expect a list.
        # Let's do a simple parse:
        import json, re
        try:
            return json.loads(text)
        except Exception:
            text = re.sub(r'```(?:json)?', '', text).strip()
            # Try find array
            match = re.search(r'(\[.*\])', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return [{"input": "", "expected_output": "?", "label": "Failed to parse generated cases"}]
            
    except Exception as e:
        logger.error("LLM Testcase generation failed: %s", e)
        return [{"input": "", "expected_output": "?", "label": f"API Error: {e}"}]
