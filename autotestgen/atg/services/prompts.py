import json


def build_generation_prompt(source_text: str, max_cases: int) -> dict:
    instructions = (
        f"You are a senior QA engineer with expertise in generating comprehensive test cases from software requirements. "
        f"Generate a maximum of {max_cases} test cases for each of the requirements supplied to you below. "
        f"Return ONLY a valid JSON object with a top-level key 'test_cases' which is an list of objects. "
        f"Each object must have only the following fields: test_case_id, requirement_id, title, description, test_steps (list of indexed strings), expected_results and priority (P1/P2/P3). "
        f"Use at most {max_cases} test cases for each requirement. Use readable IDs like TC-001, TC-002."
    )

    example = """{
    "test_cases": [
        {
            "test_case_id": "TC-001",
            "requirement_id": "REQ-123",
            "title": "Example",
            "description": "...",
            "test_steps": ["step 1", "step 2"],
            "expected_results": "...",
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


def build_verification_prompt(requirements: str, test_cases: list) -> str:
    """
    Builds a detailed prompt for verifying and improving test cases.

    Args:
        requirements: The original requirements text
        test_cases: List of generated test cases to verify

    Returns:
        A comprehensive verification prompt string
    """
    test_cases_json = json.dumps({"test_cases": test_cases}, indent=2)

    instructions = """You are an expert QA Lead and Test Architect with extensive experience in test case review and quality assurance.
Your task is to thoroughly verify, validate, and improve the generated test cases against the original requirements.

VERIFICATION CRITERIA:
1. COMPLETENESS: Ensure all requirements are adequately covered by test cases
2. ACCURACY: Verify that test cases accurately reflect the requirements
3. CLARITY: Check that test steps are clear, unambiguous, and executable
4. COVERAGE: Ensure positive, negative, and edge case scenarios are included where appropriate
5. CONSISTENCY: Verify consistent formatting, naming conventions, and structure
6. PRIORITY ASSIGNMENT: Validate that priority levels (P1/P2/P3) are correctly assigned based on business impact
7. TRACEABILITY: Ensure each test case properly references requirement IDs
8. TESTABILITY: Verify that test cases are actually testable and not vague or abstract

IMPROVEMENT GUIDELINES:
- Add missing test cases if requirements are not fully covered
- Enhance test steps with more specific details if they are too generic
- Correct any inaccuracies or misalignments with requirements
- Improve expected results to be more specific and measurable
- Adjust priorities if they don't reflect business criticality
- Fix any formatting inconsistencies
- Ensure test case IDs follow a consistent pattern
- Add edge cases or boundary conditions if missing
- Include negative test cases where appropriate (invalid inputs, error handling)

OUTPUT FORMAT:
Return ONLY a valid JSON object with a top-level key 'test_cases' which is a list of objects.
Each object must have exactly these fields: test_case_id, requirement_id, title, description, test_steps (list of strings), expected_results, and priority (P1/P2/P3).

IMPORTANT:
- If test cases are already good, return them with minor improvements
- If test cases need significant changes, modify them accordingly
- If test cases are missing, add new ones
- Maintain the order of test cases ordered by requirement_id and test_case_id
- Maintain the same JSON structure as the input
- Preserve test_case_id values unless you're adding new test cases (use TC-XXX format)
- Return only the JSON object, no explanatory text before or after"""

    example = """{
    "test_cases": [
        {
            "test_case_id": "TC-001",
            "requirement_id": "REQ-123",
            "title": "Verify user login with valid credentials",
            "description": "Test that a user can successfully log in with valid username and password",
            "test_steps": [
                "1. Navigate to the login page",
                "2. Enter valid username in the username field",
                "3. Enter valid password in the password field",
                "4. Click the 'Login' button"
            ],
            "expected_results": "User is successfully authenticated and redirected to the dashboard page. Welcome message is displayed.",
            "priority": "P1"
        }
    ]
}"""

    prompt = (
        f"{instructions}\n\n"
        f"ORIGINAL REQUIREMENTS:\n{requirements}\n\n"
        f"GENERATED TEST CASES TO VERIFY:\n{test_cases_json}\n\n"
        f"JSON SCHEMA AND EXAMPLE:\n{example}\n\n"
        f"Please verify, validate, and improve the test cases above. Return only the improved JSON with no extra text."
    )

    return prompt
