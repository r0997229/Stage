#app\control\ai_call_param\template_param.py

MODEL = "gpt-4o"

EFFORT = None

VERBOSITY = None

SYSTEM = (
  "Return ONLY valid JSON."
)

INSTRUCTIONS = f"""
INSTRUCTIONS (EXTRACT-ONLY, NO REWRITE)

You are given raw text extracted from a regulated GxP template.

Goal:
Convert ONLY the main body numbered chapters into ONE JSON object where each heading has:
- "content": verbatim prewritten narrative from the template
- "guidance": verbatim author instructions/prompts from the template

ABSOLUTE RULES (CRITICAL):
1) NO PARAPHRASING, NO REWRITING, NO SUMMARIZING.
   - You must NEVER invent or rephrase guidance (e.g., do NOT output "Describe…", "Ensure…", etc. unless those exact words exist in the input).
2) VERBATIM ONLY:
   - Every character you output in "content" and "guidance" MUST be copied EXACTLY from the input text.
   - Keep placeholders exactly as-is (e.g., "[system name]", "[version]", "(ref)", "xxxx", "TBD").
3) If you cannot find explicit guidance text in the input for a heading, set:
   - "guidance": ""
   (Do NOT generate guidance from your own interpretation.)
4) Do NOT move text between fields unless the input clearly contains both types. Do NOT “clean up” or “improve” wording.

Boundary rules:
1) START at the first real numbered chapter heading in the body (e.g., "1 PURPOSE" or "1.0 PURPOSE"). Ignore everything before it (cover page, approvals, TOC, etc.).
2) STOP after the last numbered chapter/subchapter in the main body. Ignore trailing non-body material (appendices/annexes/attachments/signature pages/distribution lists) unless they continue the same numbering scheme.

Heading detection:
- A heading is any standalone line that starts with a numeric outline pattern + title:
  Examples: "1 PURPOSE", "2 Scope", "3.1 System Description", "4.2.3 Interfaces"
- The numeric outline determines hierarchy:
  - "1" => section_1
  - "2.1" => belongs under section_2 (same section container)

Output structure:
- Top-level keys: "section_1", "section_2", ... for each main chapter number.
- Inside each section, create one object per heading (main heading and any subheadings).
- Use the normalized heading text as the key:
  - lowercase
  - trim
  - replace spaces with underscores
  - remove punctuation/special characters (keep underscores)
  - collapse multiple underscores

Each heading key maps to exactly:
{{
  "content": "<VERBATIM text copied from input>",
  "guidance": "<VERBATIM text copied from input OR empty string>"
}}

How to split content vs guidance (EXTRACTION RULES):
- "content" = sentences/paragraphs that are written as final narrative (template-ready text).
- "guidance" = ONLY text that is explicitly written as instruction/prompt in the template, such as:
  - lines starting with imperatives that are present in input: "Specify…", "Describe…", "Provide…", "List…", "Include…", "Do not…"
  - labels like "For example:", "Example:", "Guidance:", "Instruction:"
  - bullet lists that are clearly prompts/directions (and are present in input)
- IMPORTANT: Placeholders like "[system name]" do NOT automatically mean guidance. They stay where they appear.

Assignment rule:
- All text after a heading belongs to that heading until the next heading of the same or higher level appears.

Nesting rule:
- Do not nest deeper than one level.
  Put all subheadings (2.1, 2.2, 2.2.1, etc.) as siblings inside "section_2" with their own keys.

Return format:
- Return ONLY valid JSON. No commentary, no markdown, no extra keys.
"""