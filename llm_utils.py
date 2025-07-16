import logging
import litellm
from dotenv import load_dotenv

load_dotenv()

# A dictionary to hold service instances, keyed by model name.
_service_instances = {}

# A list of supported models that can be exported and used elsewhere. visit https://docs.litellm.ai/docs/providers for more providers.


SUPPORTED_MODELS = ["gemini/gemini-2.0-flash"]


class LLMService:
    """
    A generic class to handle interactions with a specific LLM.
    Instances are managed by the get_llm_service factory function.
    """

    def __init__(self, model_name: str):
        if model_name not in SUPPORTED_MODELS:
            raise ValueError(
                f"Model '{model_name}' is not supported. Please choose from: {SUPPORTED_MODELS}"
            )

        logging.info(f"Initializing LLMService for model: {model_name}")
        self.model = model_name
        self.temperature = 0.2
        self.max_tokens = 1024


    def get_response(self, user_prompt: str, system_prompt: str = None) -> str | None:
        """
        A generic method to get a response from the configured LLM.

        Args:
            user_prompt: The main prompt/question from the user.
            system_prompt: An optional prompt to set the context or role for the AI.

        Returns:
            The AI's response as a string, or None if an error occurs.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            logging.info(f"Sending request to LLM model: {self.model}")
            response = litellm.completion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"LiteLLM API call failed for model {self.model}: {e}")
            return None


def get_llm_service(model_name: str = SUPPORTED_MODELS[0]) -> LLMService:
    """
    Factory function to get an LLMService instance for a specific model.
    """
    if model_name not in _service_instances:
        logging.info(f"No existing service for '{model_name}'. Creating a new one.")
        _service_instances[model_name] = LLMService(model_name=model_name)
    
    return _service_instances[model_name]