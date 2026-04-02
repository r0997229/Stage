#app\control\ai_call_param\chatbot_param.py

MODEL = "gpt-5-mini"

EFFORT = None

VERBOSITY = None

SYSTEM = (
  "You are an expert in GAMP 5 Second Edition. "
  "Answer strictly based on the provided GAMP context. "
  "Return ONLY valid JSON."
)

INSTRUCTIONS = None

PROMPT = (
    "=== GAMP 5 REFERENCE TEXT (end) ===\n\n"
    "Analyze the attached document against the GAMP 5 principles above.\n\n"
    "For each section of the document, provide actionable suggestions to improve "
    "its compliance with GAMP 5.\n\n"
    "Output format requirements:\n"
    "- The response must be valid JSON only — no markdown, no prose outside the JSON.\n"
    "- Each key must be the exact section title found in the document.\n"
    "- Each value must be a list of suggestion strings for that section.\n"
    "- If a section has no suggestions, return an empty list as its value.\n\n"
    '- Example: {"1 Introduction": ["Add a GxP impact statement."], "2 Scope": []}'
)