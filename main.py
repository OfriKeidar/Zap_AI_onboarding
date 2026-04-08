import os
import json
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

def get_text_from_html(file_path):
    """
    helper function: reads an html file and extracts only the text, 
    stripping away all the <div>, <p> etc. tags.
    """
    if not os.path.exists(file_path):
        print(f"error: file not found - {file_path}")
        return ""
        
    with open(file_path, 'r', encoding='utf-8') as f:
        # load the html content into beautifulsoup
        soup = BeautifulSoup(f, 'html.parser')
        
        # extract text and clean up weird spacing
        clean_text = soup.get_text(separator=' ', strip=True)
        return clean_text

def scrape_mock_website(directory_path):
    """
    simulates a web scraper. it iterates over all html files in the given folder
    and combines their text into one large string for the LLM to process later.
    """
    all_pages_text = []
    
    # iterate over all files in our mock site folder
    for filename in os.listdir(directory_path):
        if filename.endswith(".html"):
            full_path = os.path.join(directory_path, filename)
            page_text = get_text_from_html(full_path)
            
            # add a header so the LLM knows which page this text belongs to
            all_pages_text.append(f"--- Page: {filename} ---")
            all_pages_text.append(page_text)
            all_pages_text.append("\n") # add some spacing
            
    # join everything together
    return "\n".join(all_pages_text)

# load environment variables from the .env file (security best practice)
load_dotenv()

# securely fetch the API key
# if it's missing, the script will crash here instead of failing silently later
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API Key not found. Please set GEMINI_API_KEY in your .env file.")

# initialize the gemini client with the new SDK syntax
client = genai.Client(api_key=GEMINI_API_KEY)

def process_with_ai(website_text):
    """
    this is the core logic where we use gemini to:
    1. extract structured data (customer card)
    2. generate an onboarding script
    
    includes a robust retry mechanism for ALL server-side issues.
    """
    prompt = f"""
    You are an AI assistant for Zap (Dapei Zahav). 
    I will provide you with text scraped from a client's website (an AC technician).
    
    Tasks:
    1. Extract: Business name, Phone, Address, Service Areas, and main Service Categories.
    2. Generate: A personal, professional onboarding phone script in Hebrew.
    
    Website Text:
    {website_text}

    Return the output ONLY as a JSON object with these keys: 
    'customer_card' (containing the extracted info) and 'onboarding_script' (the text for the call).
    Ensure the JSON is valid.
    """

    max_retries = 3
    
    for current_attempt in range(max_retries):
        try:
            print(f"sending request to AI... (attempt {current_attempt + 1}/{max_retries})")
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            raw_output = response.text.strip()
            return json.loads(raw_output)
            
        except Exception as e:
            error_message = str(e)
            
            # Catching ALL rate limits (429) and server loads (503) cleanly
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "503" in error_message or "UNAVAILABLE" in error_message:
                print(f"server busy or rate limit (429/503). waiting 40 seconds... (attempt {current_attempt + 1}/{max_retries})")
                
                # Only sleep if we have retries left
                if current_attempt < max_retries - 1:
                    time.sleep(40) 
            else:
                # A genuine error (e.g., bad API key, no internet)
                print(f"critical processing error: {e}")
                return None
                
    print("failed to process with AI after multiple retries.")
    return None

def simulate_crm_update(customer_data):
    """
    mock function to demonstrate CRM integration as requested in the assignment.
    """
    print("\n--- CRM Update Simulation ---")
    business_name = customer_data.get('customer_card', {}).get('business_name', 'Unknown')
    print(f"Status: Success - Created lead for '{business_name}'")
    print(f"Log: Digital assets analyzed, AI script generated and stored in database.")

if __name__ == "__main__":

    target_folder = "Data"
    
    print("starting local web scraping...")
    website_content = scrape_mock_website(target_folder)
    
    if website_content:
        print("done! moving to AI processing phase...")
        
        result = process_with_ai(website_content)
        
        if result:
            print("\n--- Extracted Customer Card (JSON) ---")
            # print nicely formatted json, ensure hebrew chars display correctly
            print(json.dumps(result['customer_card'], indent=4, ensure_ascii=False))
            
            print("\n--- Generated Onboarding Script ---")
            print(result['onboarding_script'])
            
            simulate_crm_update(result)
        else:
            print("failed to get results from AI.")