'''
    @file: slide_planner.py
    @brief: Currently this file is empty, but it is intended to contain the json blueprint for the markdown slides.
'''

import logging
from typing import List, Optional, Dict, Any
import json
import re

# --- Pydantic Imports --- (used to validate the LLM's output)
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


def plan_slides(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Takes a detailed context blueprint and uses an LLM to generate a simple slide plan.

    Args:
        context_blueprint: The dictionary parsed from the ContextBuilder's JSON output.

    Returns:
        A dictionary representing the validated slide plan, or None if an error occurs.
    """
    
    logging.info("Starting slide planning process...")
    
    # 1. Get the prompt template for the 'slide planner' task
    task = 'slide_planner'
    prompt_template = PROMPT_LIBRARY.get(task)
    
    if not prompt_template:
        logging.error(f"No prompt template found for task: {task}")
        return None
    
    # 2. Get the LLm service instance
    llm = get_llm_service()
    
    # 3. Format the user prompt with the full context blueprint
    # The blueprint must be converted to a JSON string to be inserted into the prompt
    context_json_string = json.dumps(context, indent=2)
    user_prompt = prompt_template['user'].format(full_context_blueprint_json=context_json_string)
    
    # 4. Call the LLM to get the slide plan
    llm_response_str = llm.get_response(
        user_prompt=user_prompt,
        system_prompt=prompt_template['system'],
    )
    
    if not llm_response_str:
        logging.error("LLM did not return a response for the slide plan.")
        return None
    
    # 4.1 Extract JSON from markdown code blocks if present
    def extract_json_from_text(text: str) -> str:
        """More robust JSON extraction."""
        # Remove markdown code blocks
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```', '', text)
        
        # Find the first complete JSON object
        brace_count = 0
        start_idx = text.find('{')
        if start_idx == -1:
            return text.strip()
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx:i+1]
        
        return text.strip()
    
    def validate_and_parse(response_str: str) -> dict:
        """Nested helper function to clean, parse, and validate the JSON string."""
        cleaned_response = extract_json_from_text(response_str)
        slide_plan_dict = json.loads(cleaned_response)
        
        # Pre-process to fix common errors (e.g., content being a string)
        for slide in slide_plan_dict.get("slides", []):
            if "content" in slide and isinstance(slide["content"], str):
                slide["content"] = [slide["content"]]
        
        validated_plan = SlidePlanModel.model_validate(slide_plan_dict)
        return validated_plan.model_dump()    
    
    # 5. Parse and validate the LLM's JSON output
    try:
        logging.info("First attempt to validate the slide plan.")
        return validate_and_parse(llm_response_str)
    except json.JSONDecodeError as e:
        logging.warning(f"Initial validation failed: {e}. Attempting self-correction.")
        
        # --- Self-Correction Logic ---
        task = 'json_fixer'
        fixer_prompt_template = PROMPT_LIBRARY.get('json_fixer')
        if not fixer_prompt_template:
            logging.error("JSON fixer prompt not found.")
            return None

        # Get the Pydantic schema as a string to pass to the fixer prompt
        schema_str = json.dumps(SlidePlanModel.model_json_schema(), indent=2)

        # Format the user prompt for the fixer
        fixer_user_prompt = fixer_prompt_template["user"].format(
            desired_schema=schema_str,
            broken_json=llm_response_str,
            validation_error=str(e)
        )
        
        # Make the second LLM call to correct the JSON
        corrected_response_str = llm.get_response(
            user_prompt=fixer_user_prompt,
            system_prompt=fixer_prompt_template["system"]
        )
        
        if not corrected_response_str:
            logging.error("Self-correction failed: LLM did not return a corrected response.")
            return None
        
        try:
            # Second and final attempt to validate
            logging.info("Second attempt to validate the corrected slide plan.")
            return validate_and_parse(corrected_response_str)
        except Exception as final_e:
            logging.error(f"Self-correction failed. Final validation error: {final_e}")
            logging.debug(f"Original response: {llm_response_str}")
            logging.debug(f"Corrected response: {corrected_response_str}")
            return None


# --- Example: Shows the end-to-end flow from PR URL to Slide Plan ---
if __name__ == "__main__":
# Ensure API keys (GITHUB_TOKEN, GEMINI_API_KEY, etc.) are set as environment variables
    
    # pr_to_analyze = "https://github.com/apache/beam/pull/35564"
    # pr_to_analyze = "https://github.com/mohitpaddhariya/mohitp.me/pull/4"
    pr_to_analyze = "https://github.com/apache/beam/pull/33711"
    
    # --- Phase 1: Build the Context ---
    print("--- Running Phase 1: Context Builder ---")
    builder = ContextBuilder(pr_url=pr_to_analyze)
    final_context_json = builder.build()
    
    if final_context_json:
        # --- Phase 2: Plan the Slides ---
        print("\n--- Running Phase 2: Slide Planner ---")
        # context_dict = json.loads(final_context_json)
        slide_plan = plan_slides(final_context_json)
        
        if slide_plan:
            
            # store the final slide plan in a JSON file
            with open('slide_plan.json', 'w') as f:
                json.dump(slide_plan, f, indent=2)
            
            print("\n✅ --- Slide Plan Generated Successfully --- ✅")
            print(json.dumps(slide_plan, indent=2))
            
            # This 'slide_plan' dictionary is now ready for the final Markdown Generator
        else:
            print("\n❌ Failed to generate the slide plan.")
    else:
        print("\n❌ Failed to build the context blueprint.")