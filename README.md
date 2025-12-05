# AI-Agents-for-Medical-Diagnostics

<img width="900" alt="image" src="https://github.com/user-attachments/assets/b7c87bf6-dfff-42fe-b8d1-9be9e6c7ce86">

A Python project that uses **LLM-powered multi-specialist AI agents** to analyze complex medical cases.  
Each agent simulates a real medical specialist, and together they provide a combined diagnostic summary.

⚠️ **Disclaimer:**  
This project is strictly for **research and educational purposes** and is **NOT intended for real medical diagnosis**.

---

## ✨ What’s New (Latest Update)

- Added **Neurologist Agent**  
- Added **Gastroenterologist Agent**  
- Expanded to a **5-agent multidisciplinary system**  
- Improved PDF reporting  
- Updated `.gitignore` and project structure  
- Upgraded to **Groq Llama 3.1 8B Instant** for ultra-fast inference  
- Added better prompt templates for specialists  
- UI and backend improvements  

---

## 🚀 How It Works

A medical report is processed by **five AI specialists**, each reviewing symptoms from their own medical viewpoint.

### 🫀 1. Cardiologist  
Analyzes:  
- Chest pain  
- Blood pressure  
- ECG abnormalities  
- Circulation issues  

### 🧠 2. Psychologist  
Analyzes:  
- Anxiety  
- Panic disorder  
- Stress levels  
- Psychosomatic symptoms  

### 🌬 3. Pulmonologist  
Analyzes:  
- Breathing issues  
- Wheezing  
- Chronic cough  
- Asthma/COPD risks  

### ⚡ 4. Neurologist *(NEW)*  
Analyzes:  
- Headaches  
- Dizziness  
- Numbness/tingling  
- Migraine / Neurological deficits  

### 🍽 5. Gastroenterologist *(NEW)*  
Analyzes:  
- Gastritis  
- Acid reflux  
- Abdominal pain  
- Liver/GI-related symptoms  

---

## 🧩 Multidisciplinary Team Agent

After all five specialists finish analysis, their reports are merged into a **final unified diagnosis**, which includes:

- Top 3–5 possible diagnoses  
- Combined reasoning  
- Recommended next steps  

---

## ⚡ Quickstart Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/MRPREM31/AI-Medical-Diagnostics.git
cd AI-Medical-Diagnostics
```
### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
```
### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt       # Windows
```

### 4️⃣ Create .env File
```bash
GROQ_API_KEY=your_api_key_here       
```
### 5️⃣ Run the Web App

```bash
python app.py
```
### 6️⃣ Run CLI Diagnosis

```bash
python main.py
```

## 🔮 Future Enhancements

Planned improvements for upcoming versions include:

- **Specialist Expansion**: Add new agents for Neurology, Endocrinology, Immunology, and other fields.  
- **Local LLM Support**: Integrate models such as **Llama 4** via Ollama, vLLM, or llama.cpp, with function-calling style hooks and safe code execution.  
- **Vision Capabilities**: Enable multimodal decision-making with agents that analyze **radiology images** and other medical scans.  
- **Live Data Tools**: Incorporate LLM-based tools for **real-time search** and querying structured **medical datasets**.  
- **Advanced Parsing**: Improve handling of complex medical reports with structured outputs (e.g., JSON schema validation).  
- **Automated Testing**: Add evaluation pipelines and smoke-test CI with mocked LLM calls for reproducibility.  
---

## 🧑‍💻 Made By — QuantumCoders Team

- 🌟 Team Leader: Prem Prasad Pradhan

- 🔗 Website: https://www.mrprem.in

**Innovators building next-generation AI tools for healthcare and automation.**