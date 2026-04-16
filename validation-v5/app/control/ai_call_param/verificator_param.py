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
    "- Return a JSON object with one key: 'suggestions'.\n"
    "- 'suggestions' is a list of objects, each with exactly these four keys:\n"
    "    'section'     : the exact section title found in the document.\n"
    "    'title'       : a short title for the suggestion (max 10 words).\n"
    "    'description' : a detailed explanation of the suggestion.\n"
    "    'source'      : the exact verbatim text copied from the document that "
    "justifies this suggestion. Do NOT paraphrase or summarize — copy the text word for word as it appears in the document.\n"
    "- If a section has no suggestions, do not include it.\n\n"
    "Example:\n"
    '{"suggestions": [\n'
    '    {\n'
    '        "section": "1 Introduction",\n'
    '        "title": "Add GxP impact statement",\n'
    '        "description": "The introduction lacks a clear GxP impact statement explaining how this system affects product quality.",\n'
    '        "source": "This document describes the validation of the LIMS system used in the QC laboratory."\n'
    '    },\n'
    '    {\n'
    '        "section": "2 Scope",\n'
    '        "title": "Clarify system boundaries",\n'
    '        "description": "The scope does not define the boundaries of the validated system.",\n'
    '        "source": "The scope of this validation covers all modules of the LIMS system."\n'
    '    }\n'
    "]}"
)