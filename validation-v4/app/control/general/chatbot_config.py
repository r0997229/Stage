#app\control\general\chatbot_config.py

# Max exchange history for chatbot
MAX_EXCHANGES: int = 20

# Max chars for chatbot input
MAX_QUESTION_CHARS: int = 2000

# Max loading time (seconds)
LOADING_MAX_TIME_SEC: int = 30

# Loading messages for chatbot
LOADING_MESSAGES = [
    "Sending…",
    "Thinking…",
    "Analyzing GAMP content…",
    "Checking references…",
    "Almost done…",

    # --- terminal messages ---
    "Sorry, something seems off…",
    "Trying again…",
    "Please wait… just a bit more",
]

# Number of terminal messages at the end
LOADING_TERMINAL_COUNT: int = 3