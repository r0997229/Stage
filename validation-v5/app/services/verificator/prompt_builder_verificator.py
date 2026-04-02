from app.control.resources.gamp_text import GAMP_TEXT
from app.control.ai_call_param.verificator_param import PROMPT

def build_verificator_prompt() -> str:
    """
    Compose the full prompt sent to GPT-4o.

    The GAMP 5 reference text is prepended as grounding context so the model
    can only draw conclusions anchored in ISPE GAMP 5 Second Edition.
    """
    return (
        "You are a pharmaceutical IT validation expert. "
        "You must base every suggestion exclusively on the GAMP 5 Second Edition "
        "reference text provided below. Do not use any external knowledge.\n\n"
        "=== GAMP 5 REFERENCE TEXT (start) ===\n"
        f"{GAMP_TEXT}\n"
        + PROMPT
    )