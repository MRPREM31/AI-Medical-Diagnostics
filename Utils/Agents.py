from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
import time
from dotenv import load_dotenv

# Load .env every time
load_dotenv()


# ---------------------------------------------------------
#  AGENT BASE CLASS WITH AUTO-RETRY TO FIX RATE LIMIT ERRORS
# ---------------------------------------------------------
class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info

        # Load Groq API key
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY missing. Add it to your .env file.")

        # Build prompt
        self.prompt_template = self.create_prompt_template()

        # Model
        self.model = ChatGroq(
            temperature=0.2,
            model="llama-3.1-8b-instant",
            groq_api_key=self.api_key
        )

    # ---------------------------------------------------------
    # CREATE PROMPTS FOR ALL SPECIALISTS
    # ---------------------------------------------------------
    def create_prompt_template(self):
        if self.role == "MultidisciplinaryTeam":
            template = f"""
                You are a Multidisciplinary Medical Team consisting of:
                - Cardiologist
                - Psychologist
                - Pulmonologist
                - Neurologist
                - Gastroenterologist

                Combine all reports and produce:

                1. **Five Possible Diagnoses**
                2. **Reasoning for each**
                3. **Recommended Next Steps**

                --- Cardiologist Report ---
                {self.extra_info.get('cardio', '')}

                --- Psychologist Report ---
                {self.extra_info.get('psycho', '')}

                --- Pulmonologist Report ---
                {self.extra_info.get('pulmo', '')}

                --- Neurologist Report ---
                {self.extra_info.get('neuro', '')}

                --- Gastroenterologist Report ---
                {self.extra_info.get('gastro', '')}
            """
        else:
            templates = {
                "Cardiologist": """
                    Act as a Cardiologist.
                    Identify cardiac issues based on the report:
                    - Possible causes
                    - Expected symptoms
                    - Recommended next steps

                    Report:
                    {medical_report}
                """,
                "Psychologist": """
                    Act as a Psychologist.
                    Identify mental health concerns:
                    - Possible conditions
                    - Emotional factors
                    - Recommended next steps

                    Report:
                    {medical_report}
                """,
                "Pulmonologist": """
                    Act as a Pulmonologist.
                    Identify breathing/lung-related issues:
                    - Disorders
                    - Possible causes
                    - Next steps

                    Report:
                    {medical_report}
                """,
                "Neurologist": """
                    Act as a Neurologist.
                    Identify neurological concerns:
                    - Migraine, nerve issues, seizure patterns
                    - Causes
                    - Next steps

                    Report:
                    {medical_report}
                """,
                "Gastroenterologist": """
                    Act as a Gastroenterologist.
                    Identify digestive/abdominal issues:
                    - Liver, stomach, intestinal problems
                    - Causes
                    - Treatment or investigation steps

                    Report:
                    {medical_report}
                """
            }

            template = templates[self.role]

        return PromptTemplate.from_template(template)

    # ---------------------------------------------------------
    # AUTO-RETRY LOGIC TO FIX RATE LIMIT ERROR
    # ---------------------------------------------------------
    def run(self):
        print(f"🔍 Running {self.role}...")

        prompt = self.prompt_template.format(medical_report=self.medical_report)

        MAX_RETRIES = 5

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.model.invoke(prompt)
                return response.content

            except Exception as e:
                error_msg = str(e)

                # Only retry if it's a rate limit
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    wait_time = attempt * 2
                    print(f"⚠️ Rate limit hit for {self.role}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                print(f"❌ Error in {self.role}: {error_msg}")
                return "Error occurred while generating diagnosis."

        return "❌ Failed after multiple retries due to rate limits."


# ---------------------------------------------------------
# SPECIALIST CLASSES
# ---------------------------------------------------------

class Cardiologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Cardiologist")


class Psychologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Psychologist")


class Pulmonologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Pulmonologist")


class Neurologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Neurologist")


class Gastroenterologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Gastroenterologist")


# ---------------------------------------------------------
# MULTIDISCIPLINARY TEAM AGGREGATOR
# ---------------------------------------------------------

class MultidisciplinaryTeam(Agent):
    def __init__(self, cardio, psycho, pulmo, neuro, gastro):
        extra = {
            "cardio": cardio,
            "psycho": psycho,
            "pulmo": pulmo,
            "neuro": neuro,
            "gastro": gastro
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=extra)
