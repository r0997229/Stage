#app\control\ai_call_param\generator_normalizer_param.py

MODEL = "gpt-5-mini"

EFFORT = "low"

VERBOSITY = "low"

SYSTEM = (
   "Return ONLY valid JSON."
)

INSTRUCTIONS = None

PROMPT = f"""
You are a STRICT JSON NORMALIZER.

You do NOT generate new content.
You do NOT rewrite content creatively.
You do NOT change narrative text or suggestions text.

You ONLY:
- Ensure the output matches OUTPUT STRUCTURE exactly
- Copy TABLES verbatim into the correct array fields

------------------------------------------------------------------------------

NON-NEGOTIABLE RULES
1) Return ONLY valid JSON. No markdown. No prose.
2) Output MUST EXACTLY match OUTPUT STRUCTURE:
   - ALL keys present, no extras, preserve ordering
3) Narrative and suggestions fields:
   - Copy scalar/text fields ONLY from DRAFT.
   - Do NOT edit wording (except remove exact duplicated lines).
   - If a required scalar/text field is missing in DRAFT, set:
     [missing: <short description>]
4) TABLES / LISTS (array fields):
   - Populate array fields ONLY from TABLES input, verbatim:
     same number of rows, same order, same keys, same values
   - If the TABLES input for that array is empty, output []
   - Do NOT modify table content.
"""