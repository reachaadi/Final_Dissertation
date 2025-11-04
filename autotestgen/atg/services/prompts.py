def build_generation_prompt(source_text: str, max_cases: int) -> dict:
    instructions = (
        f"You are a senior QA engineer with expertise in generating comprehensive test cases from software requirements. "
        f"Generate a maximum of {max_cases} test cases for each of the requirements supplied to you below. "
        f"Return ONLY a valid JSON object with a top-level key 'testCases' which is an list of objects. "
        f"Each object must have only the following fields: test_case_id, title, description, test_steps (list of indexed strings), expected_results and priority (P1/P2/P3). "
        f"Use at most {max_cases} test cases for each requirement. Use readable IDs like TC-001, TC-002."
    )

    example = """{
    "testCases": [
        {
            "testCaseId": "TC-001",
            "title": "Example",
            "description": "...",
            "testSteps": ["step 1", "step 2"],
            "expectedResults": "...",
            "priority": "P2"
        }
    ]
    }
    """

    prompt = (
        f"{instructions}\n\n"
        f"Application Requirements:\n{source_text}\n\n"
        f"JSON Schema and Example:\n{example}\n\n"
        f"Return only JSON with no extra text."
    )

    return prompt
