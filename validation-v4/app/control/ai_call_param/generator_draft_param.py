#app\control\ai_call_param\generator_draft_param.py

MODEL = "gpt-5-mini"

EFFORT = "high"

VERBOSITY = "medium"

SYSTEM = (
   "You are an expert in GAMP 5 Second Edition."
   "Content strictly based on the provided GAMP context."
   "Return ONLY valid JSON."
)

INSTRUCTIONS = None

PROMPT = f"""
RULES (DRAFT MODE)
1) Return ONLY valid JSON. No markdown. No prose outside JSON.
2) Output JSON MUST EXACTLY match the OUTPUT STRUCTURE keys and nesting:
   - ALL keys must exist
   - NO additional keys
   - Preserve key order
3) TABLES / LISTS:
   - Any field that is an array in the OUTPUT STRUCTURE is a table/list.
   - Output those fields as empty arrays [] (do NOT create items/rows).
   - Do NOT reproduce table content inside narrative fields.
   - If table content is relevant, write: "See corresponding table."
4) TEMPLATE MARKERS:
   - @...@ keep inner text, remove @
   - [...] fill or write [missing: <short description>]
   - [(...)] include only if relevant
   - #...# remove completely
5) CONTENT:
   - Never invent regulatory/technical content, IDs, SOP numbers, or reference codes.
   - Use GAMP 5 only as framing language; do not add new requirements beyond inputs.
   - Use [missing: <short description>] exactly (lowercase).
6) SUGGESTIONS FIELDS:
   - For each <field>_suggestions:
      Write 2–5 actionable bullets based on GAMP 5 good practice and the provided inputs. (IF POSSIBLE)
      Each bullet MUST start with "• "
   - Suggestions MUST NOT include invented SOP IDs or document numbers.
"""