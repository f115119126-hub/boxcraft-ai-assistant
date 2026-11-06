# BoxCraft AI: B2B Custom Packaging & Carton Quote Assistant

An intelligent customer service agent built with Gradio, SQLite, and Gemini for corrugated cardboard box price quotation, rule retrieval, and order logging.

## Features
- **Tool Calling**: Automated box area calculation, tiered pricing formula, and SQLite database recording (`quotes` table).
- **RAG & Rule Verification**: Retrieves production lead times, flute burst-strength standards, and shipping policies from `factory_policy.md`.
- **Anti-Hallucination & Scope Enforcement**: Restricts answering scope strictly to carton packaging inquiries and politely refuses out-of-scope queries (e.g. weather, non-existent order inquiries).

## Project Structure
```
boxcraft-ai-assistant/
├── app.py                 # Gradio Chat Interface and Agent logic
├── factory_policy.md      # Manufacturing specifications and policies (RAG source)
├── requirements.txt       # Dependencies list
├── .env.example           # Example environment template
├── .gitignore             # Git ignore rules (prevents uploading .env and DB)
└── README.md              # Project documentation
```

## How to Install and Run

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/boxcraft-ai-assistant.git
   cd boxcraft-ai-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:7860`.
