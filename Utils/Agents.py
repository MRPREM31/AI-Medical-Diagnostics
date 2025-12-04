from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os

class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info

        # Load Groq key
        self.api_key = os.getenv("GROQ_API_KEY")

        # Build prompt
        self.prompt_template = self.create_prompt_template()

        # 👉 NEW, WORKING GROQ MODEL (2025)
        self.model = ChatGroq(
            temperature=0.2,
            model="llama-3.1-8b-instant",
            groq_api_key=self.api_key
        )

    def create_prompt_template(self):
        if self.role == "MultidisciplinaryTeam":
            templates = f"""
                Act like a multidisciplinary healthcare team.

                Analyze the following specialist reports and produce exactly 3 possible health issues
                with reasoning.

                Cardiologist Report:
                {self.extra_info.get('cardiologist_report', '')}

                Psychologist Report:
                {self.extra_info.get('psychologist_report', '')}

                Pulmonologist Report:
                {self.extra_info.get('pulmonologist_report', '')}
            """
        else:
            templates = {
                "Cardiologist": """
                    Act like a cardiologist.

                    Review the patient’s cardiac findings and identify:
                    - Possible cardiac causes of symptoms
                    - Recommended next steps

                    Medical Report:
                    {medical_report}
                """,
                "Psychologist": """
                    Act like a psychologist.

                    Identify psychological factors such as anxiety, depression, panic disorder, etc.
                    Provide next steps.

                    Report:
                    {medical_report}
                """,
                "Pulmonologist": """
                    Act like a pulmonologist.

                    Identify respiratory issues such as asthma, COPD, or breathing dysfunction.
                    Provide next steps.

                    Report:
                    {medical_report}
                """
            }
            templates = templates[self.role]

        return PromptTemplate.from_template(templates)

    def run(self):
        print(f"{self.role} is running...")
        prompt = self.prompt_template.format(medical_report=self.medical_report)
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print("Error occurred:", e)
            return None


class Cardiologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Cardiologist")


class Psychologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Psychologist")


class Pulmonologist(Agent):
    def __init__(self, medical_report):
        super().__init__(medical_report, "Pulmonologist")


class MultidisciplinaryTeam(Agent):
    def __init__(self, cardiologist_report, psychologist_report, pulmonologist_report):
        extra_info = {
            "cardiologist_report": cardiologist_report,
            "psychologist_report": psychologist_report,
            "pulmonologist_report": pulmonologist_report
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=extra_info)
