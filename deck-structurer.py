import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def deck_to_structured_json(raw_deck: str) -> str:
    """Convert one raw deck text into structured JSON using Gemini."""
    prompt = f"""
    You are an AI that converts unstructured slide text into structured proposal JSON following a fixed outline.
 
    The JSON must strictly follow this structure with exactly these sections:

    1. Cover Slide
       - Client name
       - Project title
       - Company branding
       - Proposal date
       - Version

    2. Executive Summary
       - Problem Statement
       - Opportunity
       - Unique Position
       - Proposed Outcomes

    3. Client Context & Needs
    4. Our Understanding of the Objectives
    5. Company Solution Approach
    6. Value Proposition & Business Impact
    7. Engagement Model
    8. Project Plan & Timeline
    9. Commercials / Pricing
    10. Risk Management & Mitigation
    11. Support & Next Steps
    12. About Company
    13. Closing Slide
 
    Each section should be represented as a JSON object with meaningful keys and values. 
    If information is missing, fill with "TBD".
 
    Now convert the following deck into this structured JSON:
 
    {raw_deck}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    txt_file = "deck_texts.txt"  # multiple decks, one per line
    output_file = "output.txt"

    with open(txt_file, "r", encoding="utf-8") as f:
        all_decks = [line.strip() for line in f if line.strip()]

    with open(output_file, "w", encoding="utf-8") as file:
        for i, raw_deck in enumerate(all_decks, start=1):
            print(f"Processing deck {i}/{len(all_decks)}...")
            try:
                structured_json = deck_to_structured_json(raw_deck)
                file.write(f"--- Deck {i} ---\n")
                file.write(structured_json + "\n\n")
            except Exception as e:
                print(f"❌ Error processing deck {i}: {e}")
                file.write(f"--- Deck {i} ---\nERROR: {e}\n\n")

    print(f"✅ All decks processed. Results saved in {output_file}")
