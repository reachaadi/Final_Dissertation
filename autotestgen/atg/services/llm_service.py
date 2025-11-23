import json
from atg.services.prompts import build_generation_prompt, build_verification_prompt
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
        )["test_cases"]
        return test_cases

    def verify_and_modify_test_cases(self, requirements: str, test_cases: list) -> list:
        """
        Verifies and improves the generated test cases using LLM.

        Args:
            requirements: The original requirements text
            test_cases: List of generated test cases to verify and improve

        Returns:
            List of verified and improved test cases
        """
        prompt = build_verification_prompt(requirements, test_cases)
        verification_config = types.GenerateContentConfig(
            temperature=0.3,  # Slightly higher temperature for more creative improvements
        )
        response = self.llm_client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=verification_config,
        )
        response_dict = response.model_dump()
        verified_test_cases = json.loads(
            response_dict["candidates"][0]["content"]["parts"][0]["text"]
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )["test_cases"]
        return verified_test_cases
