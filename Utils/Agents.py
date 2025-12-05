from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load .env every time
load_dotenv()

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

    def create_prompt_template(self):
        if self.role == "MultidisciplinaryTeam":
            template = f"""
                Act like a multidisciplinary healthcare team.

                Analyze these specialist reports and produce:
                - 5 combined possible diagnoses
                - Reasons for each
                - Recommended next steps

                Cardiologist Report:
                {self.extra_info.get('cardio', '')}

                Psychologist Report:
                {self.extra_info.get('psycho', '')}

                Pulmonologist Report:
                {self.extra_info.get('pulmo', '')}

                Neurologist Report:
                {self.extra_info.get('neuro', '')}

                Gastroenterologist Report:
                {self.extra_info.get('gastro', '')}
            """
        else:
            templates = {
                "Cardiologist": """
                    Act as a Cardiologist.
                    Identify cardiac issues, causes, and next steps.
                    Report:
                    {medical_report}
                """,
                "Psychologist": """
                    Act as a Psychologist.
                    Identify psychological issues, causes, and treatments.
                    Report:
                    {medical_report}
                """,
                "Pulmonologist": """
                    Act as a Pulmonologist.
                    Identify breathing/lung disorders and next steps.
                    Report:
                    {medical_report}
                """,
                "Neurologist": """
                    Act as a Neurologist.
                    Identify neurological disorders such as migraine, seizure,
                    nerve issues, or brain-related symptoms.
                    Provide probable causes and recommendations.
                    Report:
                    {medical_report}
                """,
                "Gastroenterologist": """
                    Act as a Gastroenterologist.
                    Analyze digestive symptoms, stomach issues, liver or gut problems.
                    Provide diagnosis, causes, and next steps.
                    Report:
                    {medical_report}
                """
            }
            template = templates[self.role]

        return PromptTemplate.from_template(template)

    def run(self):
        print(f"🔍 Running {self.role}...")
        prompt = self.prompt_template.format(medical_report=self.medical_report)
        response = self.model.invoke(prompt)
        return response.content


# ------------ INDIVIDUAL SPECIALIST CLASSES -------------

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


# ------------ MULTIDISCIPLINARY TEAM --------------------

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
