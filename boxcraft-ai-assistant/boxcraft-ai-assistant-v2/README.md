# BoxCraft AI: B2B Custom Packaging & Carton Quote Assistant

An intelligent customer service agent built with Gradio, SQLite, and OpenAI API (connecting to NKUST Furen-large / Gemini) for corrugated cardboard box price quotation, rule retrieval, and order logging.

## Features
- **Tool Calling**: Automated box area calculation, tiered pricing formula, and SQLite database recording (`quotes` table).
- **RAG & Rule Verification**: Retrieves production lead times, flute burst-strength standards, and shipping policies from `factory_policy.md`.
- **Anti-Hallucination & Scope Enforcement**: Restricts answering scope strictly to carton packaging inquiries and politely refuses out-of-scope queries (e.g. weather, non-existent order inquiries).

## Project Structure
```
boxcraft-ai-assistant/
├── app.py                 # Gradio Chat Interface and Real Agent Tool Calling logic
├── factory_policy.md      # Manufacturing specifications and policies (RAG source)
├── requirements.txt       # Dependencies list (gradio, openai, python-dotenv, pandas)
├── .env.example           # Example environment template (Never commit real .env)
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

3. Setup environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and put your real API_KEY
   ```

4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:7860`.
