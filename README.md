# Zap AI Onboarding Pipeline - Prototype

## Overview
This project is a prototype for an automated AI-driven pipeline designed to streamline the onboarding process for new clients at Zap. The system simulates scraping a client's digital assets (a 5-page mock website), extracts structured business data using a Generative AI model, and automatically generates a personalized onboarding script for the sales/service representative.

## Architecture & Workflow
The pipeline is divided into three main logical steps:
1. **Data Ingestion (Mock Web Scraper):** Iterates over a local directory (`Data`) containing HTML files, parses them using `BeautifulSoup`, and extracts clean, raw text while stripping HTML tags.
2. **AI Processing Layer (Gemini 2.5 Flash):** - Takes the raw scraped text as input.
   - Prompts the LLM to extract key business entities (Name, Phone, Service Areas, Categories).
   - Forces the LLM to return a strict JSON output (`application/json` mime type) to prevent parsing errors.
   - Generates a personalized, professional onboarding script in Hebrew based on the extracted entities.
3. **CRM Integration (Simulation):** Parses the generated JSON and logs the successful creation of a client card, simulating an API push to Zap's CRM.

## Key Design Decisions
* **Hebrew Data Processing:** The mock HTML files were deliberately kept in Hebrew. Since Zap targets the Israeli local market, evaluating the LLM's capability to understand context, extract entities, and generate natural text in Hebrew is critical for a real-world scenario.
* **Robust Error Handling (Retry Mechanism):** When working with third-party APIs (like Google Gemini), rate limits (429) and server overloads (503) are common. The script includes a custom retry loop that detects these specific exceptions, applies a 40-second sleep timeout to clear the quota, and attempts the request again without crashing the application.
* **Security:** API keys are never hardcoded. The project utilizes `python-dotenv` to securely load the key from a local `.env` file.

## Prerequisites
To run this project locally, ensure you have Python 3.10+ installed. 

## Setup & Installation

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
## Install dependencies:
pip install -r requirements.txt
## Environment Variables:
Create a .env file in the root directory and add your Google Gemini API key:
GEMINI_API_KEY=your_api_key_here
Run the pipeline:
python main.py
## Future Improvements (Production Grade)
If this were to be deployed to production, I would recommend:
- Replacing the local HTML parser with a headless browser (e.g., Selenium/Playwright) or a dedicated scraping API to handle dynamic SPA websites.
- Replacing the mocked simulate_crm_update function with real REST API calls (e.g., Salesforce / HubSpot endpoints).
- Adding comprehensive Unit Tests for the JSON parsing logic.