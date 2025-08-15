import logging
import json
from typing import Dict, Any, Optional

# --- Import utilities and prompts ---
from llm_utils import get_llm_service
from prompts import PROMPT_LIBRARY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)

class SlideWriter:
    """
    Generates a complete Slidev Markdown file from a slide plan using a single AI call.
    """
    def __init__(self, slide_plan: Dict[str, Any]):
        self.slide_plan = slide_plan
        self.llm = get_llm_service()

    def generate_markdown(self) -> Optional[str]:
        """
        Orchestrates the Markdown generation.
        """
        logging.info("Generating final Slidev Markdown via single AI call...")

        task = "slide_writer"
        prompt_template = PROMPT_LIBRARY.get(task)
        if not prompt_template:
            logging.error(f"Prompt for task '{task}' not found.")
            return None

        # Convert the slide plan dict to a JSON string for the prompt
        slide_plan_json_string = json.dumps(self.slide_plan, indent=2)

        # Format the user prompt
        user_prompt = prompt_template["user"].format(slide_plan_json=slide_plan_json_string)

        # Make the single LLM call to generate the entire file
        markdown_output = self.llm.get_response(
            user_prompt=user_prompt,
            system_prompt=prompt_template["system"]
        )

        if markdown_output:
            logging.info("Successfully generated Markdown content.")
            # Clean up any unwanted wrapping that might still be present
            cleaned_output = markdown_output.strip()
            
            # Remove any code block wrapping
            if cleaned_output.startswith('```') and cleaned_output.endswith('```'):
                lines = cleaned_output.split('\n')
                # Remove first line (opening ```) and last line (closing ```)
                cleaned_output = '\n'.join(lines[1:-1]).strip()
            
            # Remove any XML-style tags
            if cleaned_output.startswith('<slide_markdown>'):
                cleaned_output = cleaned_output.replace('<slide_markdown>', '').strip()
            if cleaned_output.endswith('</slide_markdown>'):
                cleaned_output = cleaned_output.replace('</slide_markdown>', '').strip()
            
            return cleaned_output
        else:
            logging.error("Failed to generate Markdown from the LLM.")
            return None

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        with open('slide_plan.json', 'r') as f:
            slide_plan_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: 'slide_plan.json' not found. Please run the slide_planner.py first.")
        exit()

    # 1. Create an instance of the generator
    # print("Slide Plan : ", slide_plan_data)
    generator = SlideWriter(slide_plan=slide_plan_data)

    # 2. Generate the final Markdown content
    final_markdown = generator.generate_markdown()

    if final_markdown:
        # 3. Save the content to a .md file
        with open("presentation.md", "w") as f:
            f.write(final_markdown)

        print("\n✅ Slidev Markdown file 'presentation.md' created successfully.")
        print("\n--- To view your presentation, run the following commands in your terminal: ---")
        print("1. npm install -g @slidev/cli")
        print("2. slidev presentation.md --open")