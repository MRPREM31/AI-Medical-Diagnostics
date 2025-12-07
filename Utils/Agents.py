from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------------------------
#   GLOBAL SETTINGS FOR RATE-LIMIT SAFE MODE
# ---------------------------------------------------------
MAX_RETRIES = 5
BASE_WAIT = 3       # base wait time between retries
MAX_TOKENS = 300    # limits Groq usage and avoids 429 errors


# ---------------------------------------------------------
#   AGENT BASE CLASS
# ---------------------------------------------------------
class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        # Shrink large reports for cheaper token usage
        self.medical_report = (medical_report or "")[:2500]

        self.role = role
        self.extra_info = extra_info or {}

        # Load Groq API key
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY missing in .env")

        # Create prompt
        self.prompt_template = self.create_prompt_template()

        # LLM Model
        self.model = ChatGroq(
            temperature=0.2,
            model="llama-3.1-8b-instant",
            groq_api_key=self.api_key,
            max_tokens=MAX_TOKENS   # prevents huge output
        )

    # ---------------------------------------------------------
    #   CREATE PROMPTS FOR ALL DOCTORS
    # ---------------------------------------------------------
    def create_prompt_template(self):

        SHORT = """
Respond in **short, concise medical points**.
Maximum 4–5 lines. Avoid long explanation.
"""

        templates = {
            "Cardiologist": SHORT + """
Act as a Cardiologist.
Identify possible heart-related issues, causes, and next steps.
Report:
{medical_report}
""",
            "Psychologist": SHORT + """
Act as a Psychologist.
Identify possible mental health conditions and next steps.
Report:
{medical_report}
""",
            "Pulmonologist": SHORT + """
Act as a Pulmonologist.
Identify lung or breathing-related problems and recommendations.
Report:
{medical_report}
""",
            "Neurologist": SHORT + """
Act as a Neurologist.
Identify brain/nerve-related issues and steps to follow.
Report:
{medical_report}
""",
            "Gastroenterologist": SHORT + """
Act as a Gastroenterologist.
Identify digestive, liver, or stomach-related disorders and next steps.
Report:
{medical_report}
"""
        }

        # ---------------------------------------------------------
        # MULTIDISCIPLINARY TEAM PROMPT
        # ---------------------------------------------------------
        if self.role == "MultidisciplinaryTeam":
            template = SHORT + """
You are a 5-specialist multidisciplinary team:
- Cardiologist
- Psychologist
- Pulmonologist
- Neurologist
- Gastroenterologist

Combine expert reports and output:

1. EXACTLY **3 Possible Diagnoses**
2. One-line reason for each
3. One-line recommendation for each

--- Cardiologist Report ---
{cardio}

--- Psychologist Report ---
{psycho}

--- Pulmonologist Report ---
{pulmo}

--- Neurologist Report ---
{neuro}

--- Gastroenterologist Report ---
{gastro}
"""
        else:
            template = templates[self.role]

        return PromptTemplate.from_template(template)

    # ---------------------------------------------------------
    #   AUTO-RETRY + RATE-LIMIT HANDLING
    # ---------------------------------------------------------
    def run(self):
        print(f"🔍 Running {self.role}...")

        prompt = self.prompt_template.format(
            medical_report=self.medical_report,
            **self.extra_info
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.model.invoke(prompt)
                time.sleep(1.5)  # safety cooldown
                return response.content

            except Exception as e:
                error_msg = str(e)

                # RATE LIMIT
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    wait = BASE_WAIT * attempt
                    print(f"⚠️ Rate limit for {self.role}. Retrying in {wait}s…")
                    time.sleep(wait)
                    continue

                # OTHER ERRORS
                print(f"❌ Error in {self.role}: {error_msg}")
                return "Error generating diagnosis."

        return "❌ Failed after multiple retries due to rate limits."


# ---------------------------------------------------------
#   INDIVIDUAL SPECIALIST CLASSES
# ---------------------------------------------------------
class Cardiologist(Agent):
    def __init__(self, report):
        super().__init__(report, "Cardiologist")


class Psychologist(Agent):
    def __init__(self, report):
        super().__init__(report, "Psychologist")


class Pulmonologist(Agent):
    def __init__(self, report):
        super().__init__(report, "Pulmonologist")


class Neurologist(Agent):
    def __init__(self, report):
        super().__init__(report, "Neurologist")


class Gastroenterologist(Agent):
    def __init__(self, report):
        super().__init__(report, "Gastroenterologist")


# ---------------------------------------------------------
#   MULTIDISCIPLINARY TEAM
# ---------------------------------------------------------
class MultidisciplinaryTeam(Agent):
    def __init__(self, cardio, psycho, pulmo, neuro, gastro):
        info = {
            "cardio": cardio,
            "psycho": psycho,
            "pulmo": pulmo,
            "neuro": neuro,
            "gastro": gastro
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=info)
