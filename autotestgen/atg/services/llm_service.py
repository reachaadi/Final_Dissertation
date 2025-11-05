import json
from atg.services.prompts import build_generation_prompt
from google import genai
from google.genai import types
import os


class TestCaseGenerator:
    def __init__(self):
        # self.llm_client = OpenAI()
        self.llm_client = genai.Client(api_key=os.getenv("GENAI_KEY"))

    def generate_test_cases(self, requirements: str, max_cases: int = 10) -> dict:
        prompt = build_generation_prompt(requirements, max_cases)
        generation_config = types.GenerateContentConfig(
            temperature=0.2,  # Set your desired temperature here (e.g., 0.7)
            # You can also set other parameters like top_p, top_k, max_output_tokens, etc.
            # top_p=0.9,
            # max_output_tokens=2048,
        )
        response = self.llm_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=generation_config,  # Or 'gemini-2.5-pro' for more complex tasks
        )
        response_dict = response.model_dump()
        test_cases = json.loads(
            response_dict["candidates"][0]["content"]["parts"][0]["text"]
            .replace("```json", "")
            .replace("```", "")
        )["testCases"]
        return test_cases
