# app/control/general/generator_config.py

# Doc types appearing in the dropdown
DOC_TYPES = {
    "VP": "Validation Plan",
    "RA": "Risk Assessment",
    "VR": "Validation Report",
}

# Max loading time (seconds)
LOADING_MAX_TIME_SEC: int = 250

# Loading messages
LOADING_MESSAGES = [
    "Preparing document structure…",
    "Validating inputs…",
    "Generating GAMP-compliant content…",
    "Cross-checking terminology and definitions…",
    "Aligning sections and tables…",
    "Inserting authoritative tables…",
    "Normalizing formatting and section numbering…",
    "Applying consistency checks…",
    "Ensuring audit-ready wording…",
    "Rendering DOCX output…",
    "Finalizing document…",
    "Almost done…",

    # terminal
    "Sorry, something seems off…",
    "Trying again…",
    "Please wait… just a bit more",
]

# Number of terminal messages at the end
LOADING_TERMINAL_COUNT: int = 3