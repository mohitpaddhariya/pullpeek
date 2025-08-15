import logging
from typing import List, Optional, Dict, Any
import json
import re

# --- Pydantic Imports ---
from pydantic import BaseModel, Field

# --- Import utilities and prompts ---
from context_builder import ContextBuilder
from llm_utils import get_llm_service
from prompts import PROMPT_LIBRARY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)

# --- Pydantic Models for Slide Plan Validation ---
class CodeBlockModel(BaseModel):
    language: str
    code: str

class SlideModel(BaseModel):
    slide_type: str
    title: str
    subtitle: Optional[str] = None
    content: Optional[List[str]] = None
    code_block: Optional[CodeBlockModel] = None
    speaker_notes: Optional[str] = None

class SlidePlanModel(BaseModel):
    presentation_title: str
    slides: List[SlideModel]


class SlidePlanner:
    """
    A class to orchestrate the process of planning presentation slides
    from a detailed context blueprint.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = get_llm_service()

    def plan(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        The main public method to generate a slide plan from a context blueprint.
        """
        self.logger.info("Starting slide planning process...")
        
        # 1. Make the initial LLM call to get the slide plan
        llm_response_str = self._get_initial_plan(context)
        if not llm_response_str:
            self.logger.error("LLM did not return an initial response.")
            return None

        # 2. Try to parse and validate the initial response
        try:
            self.logger.info("First attempt to validate the slide plan.")
            return self._validate_and_parse(llm_response_str)
        except Exception as e:
            self.logger.warning(f"Initial validation failed: {e}. Attempting self-correction.")
            
            # 3. If validation fails, attempt self-correction
            corrected_response_str = self._attempt_self_correction(llm_response_str, str(e))
            if not corrected_response_str:
                self.logger.error("Self-correction failed: LLM did not return a corrected response.")
                return None
            
            # 4. Try to validate the corrected response
            try:
                self.logger.info("Second attempt to validate the corrected slide plan.")
                return self._validate_and_parse(corrected_response_str)
            except Exception as final_e:
                self.logger.error(f"Self-correction failed. Final validation error: {final_e}")
                self.logger.debug(f"Original response: {llm_response_str}")
                self.logger.debug(f"Corrected response: {corrected_response_str}")
                return None

    def _get_initial_plan(self, context: Dict[str, Any]) -> Optional[str]:
        """Makes the first call to the LLM to generate the slide plan."""
        task = 'slide_planner'
        prompt_template = PROMPT_LIBRARY.get(task)
        if not prompt_template:
            self.logger.error(f"No prompt template found for task: {task}")
            return None
        
        context_json_string = json.dumps(context, indent=2)
        user_prompt = prompt_template['user'].format(full_context_blueprint_json=context_json_string)
        
        return self.llm.get_response(user_prompt, prompt_template['system'])

    def _attempt_self_correction(self, broken_json: str, validation_error: str) -> Optional[str]:
        """Makes a second LLM call to fix a malformed JSON response."""
        task = 'json_fixer'
        fixer_prompt_template = PROMPT_LIBRARY.get(task)
        if not fixer_prompt_template:
            self.logger.error("JSON fixer prompt not found.")
            return None

        schema_str = json.dumps(SlidePlanModel.model_json_schema(), indent=2)
        fixer_user_prompt = fixer_prompt_template["user"].format(
            desired_schema=schema_str,
            broken_json=broken_json,
            validation_error=validation_error
        )
        
        return self.llm.get_response(fixer_user_prompt, fixer_prompt_template["system"])

    def _validate_and_parse(self, response_str: str) -> dict:
        """A helper method to clean, parse, and validate a JSON string."""
        cleaned_response = self._extract_json_from_text(response_str)
        slide_plan_dict = json.loads(cleaned_response)
        
        for slide in slide_plan_dict.get("slides", []):
            if "content" in slide and isinstance(slide["content"], str):
                slide["content"] = [slide["content"]]
        
        validated_plan = SlidePlanModel.model_validate(slide_plan_dict)
        return validated_plan.model_dump()

    def _extract_json_from_text(self, text: str) -> str:
        """A helper method for robust JSON extraction."""
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```', '', text)
        brace_count = 0
        start_idx = text.find('{')
        if start_idx == -1: return text.strip()
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{': brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0: return text[start_idx:i+1]
        
        return text.strip()


# --- Main Execution Block ---
if __name__ == "__main__":
    pr_to_analyze = "https://github.com/apache/beam/pull/33711"
    
    # --- Phase 1: Build the Context ---
    print("--- Running Phase 1: Context Builder ---")
    builder = ContextBuilder(pr_url=pr_to_analyze)
    final_context_json = builder.build()
    
    if final_context_json:
        # --- Phase 2: Plan the Slides ---
        print("\n--- Running Phase 2: Slide Planner ---")
        
        # (MODIFIED) Instantiate and use the new SlidePlanner class
        planner = SlidePlanner()
        slide_plan = planner.plan(json.loads(final_context_json))
        
        if slide_plan:
            with open('slide_plan.json', 'w') as f:
                json.dump(slide_plan, f, indent=2)
            
            print("\n✅ --- Slide Plan Generated Successfully --- ✅")
            print(json.dumps(slide_plan, indent=2))
        else:
            print("\n❌ Failed to generate the slide plan.")
    else:
        print("\n❌ Failed to build the context blueprint.")