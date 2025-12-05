# Importing the needed modules 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from Utils.Agents import (
    Cardiologist,
    Psychologist,
    Pulmonologist,
    Neurologist,
    Gastroenterologist,
    MultidisciplinaryTeam
)
import os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Loading API key from a dotenv file.
load_dotenv()

with open(r"Medical Reports\Medical Rerort - Michael Johnson - Panic Attack Disorder.txt", "r") as file:
    medical_report = file.read()

# Create all 5 agents
agents = {
    "Cardiologist": Cardiologist(medical_report),
    "Psychologist": Psychologist(medical_report),
    "Pulmonologist": Pulmonologist(medical_report),
    "Neurologist": Neurologist(medical_report),
    "Gastroenterologist": Gastroenterologist(medical_report)
}

# Function to run each agent and return response
def get_response(agent_name, agent):
    response = agent.run()
    return agent_name, response

# Run all agents concurrently
responses = {}
with ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(get_response, name, agent): name
        for name, agent in agents.items()
    }

    for future in as_completed(futures):
        agent_name, response = future.result()
        responses[agent_name] = response

# Create multidisciplinary final diagnosis
team_agent = MultidisciplinaryTeam(
    cardiologist_report=responses["Cardiologist"],
    psychologist_report=responses["Psychologist"],
    pulmonologist_report=responses["Pulmonologist"],
    neurologist_report=responses["Neurologist"],
    gastro_report=responses["Gastroenterologist"]
)

# Run the MultidisciplinaryTeam agent to generate the final diagnosis
final_diagnosis = team_agent.run()
final_diagnosis_text = "### Final Diagnosis:\n\n" + final_diagnosis
txt_output_path = "results/final_diagnosis.txt"

# Ensure the directory exists
os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

# Write the final diagnosis to the text file
with open(txt_output_path, "w") as txt_file:
    txt_file.write(final_diagnosis_text)

print(f"Final diagnosis has been saved to {txt_output_path}")


