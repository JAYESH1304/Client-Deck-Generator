import os
from dotenv import load_dotenv
import json
from neo4j import GraphDatabase
import google.generativeai as genai

# ----------------------------
# 1. Load environment variables
# ----------------------------
load_dotenv()
NEO4J_URI =  "bolt://localhost:7687"
NEO4J_USER =  "neo4j"
NEO4J_PASSWORD = "auxothon25"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------
# 2. Neo4j connection
# ----------------------------
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ----------------------------
# 3. Gemini setup
# ----------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ----------------------------
# 4. Prompt template
# ----------------------------
CYPHER_GUIDE = """
You are an expert Cypher query generator for Neo4j.

The graph contains these entities and relationships:

Entities:
- (:Client {name})
- (:Deck {deck_id, title, version, proposalDate})
- (:Company {name})
- (:Section {
    name,
    text,
    problem_statement,
    opportunity,
    unique_position,
    proposed_outcomes,
    client_name,
    company_branding,
    proposal_date,
    deck_id,
    version
})
- (:Phase {
    name,
    duration,
    objectives,
    deliverables,
    order,
    deck_id
})

Relationships:
- (:Client)-[:HAS_DECK]->(:Deck)
- (:Company)-[:BRANDED]->(:Deck)
- (:Deck)-[:HAS_SECTION]->(:Section)
- (:Section)-[:HAS_PHASE]->(:Phase)

Rules:
- Always generate **pure Cypher query**, no explanation, no markdown.
- Use MATCH / OPTIONAL MATCH properly.
- Return only relevant fields, not whole nodes.
- ProposalDate is stored as a Neo4j `date`.
- Be flexible: if user asks "tell me about client X", join sections like "Executive Summary", "Client Context & Needs", "About Company".
- If the question is about timeline, fetch from `:Phase`.
- If it’s about risks, pricing, engagement, support, or similar, fetch from `:Section` by its `name`.

Examples:
1. User: "List all decks for client ADI"
   Cypher: MATCH (c:Client {name:"ADI"})-[:HAS_DECK]->(d:Deck) RETURN d.title, d.version, d.proposalDate

2. User: "What is the project plan for ADI?"
   Cypher: MATCH (c:Client {name:"ADI"})-[:HAS_DECK]->(d:Deck)-[:HAS_SECTION]->(s:Section {name:"Project Plan & Timeline"})-[:HAS_PHASE]->(p:Phase) RETURN p.name, p.duration, p.objectives, p.deliverables ORDER BY p.order

3. User: "Tell me about ADI"
   Cypher: MATCH (c:Client {name:"ADI"})-[:HAS_DECK]->(d:Deck)-[:HAS_SECTION]->(s:Section) 
           WHERE s.name IN ["Executive Summary","Client Context & Needs","About Company"]
           RETURN s.name, s.text, s.problem_statement, s.opportunity, s.unique_position, s.proposed_outcomes
"""

def generate_cypher(user_request: str) -> str:
    """Generate Cypher query from natural language request."""
    prompt = f"""{CYPHER_GUIDE}

User request: {user_request}

Write only the Cypher query (no markdown, no explanation)."""
    response = model.generate_content(prompt)
    cypher = response.text.strip()

    # Clean Gemini output if it adds ```cypher fences
    if cypher.startswith("```"):
        cypher = cypher.strip("`")
        cypher = cypher.replace("cypher", "").strip()
    return cypher


def clean_results(raw_results: list, user_request: str) -> str:
    """Use Gemini to summarize/clean Neo4j results."""
    prompt = f"""
Neo4j raw query results:
{json.dumps(raw_results, default=str, indent=2)}

User request: "{user_request}"

Reformat these results into a clean, human-friendly JSON grouped by client name,
removing nulls/duplicates. Only include useful fields relevant to the request.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def run_cypher(query: str):
    """Run Cypher query in Neo4j and return results."""
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]
    
class KGAssistant:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, user_request: str):
        cypher = generate_cypher(user_request)
        # print(f"Generated Cypher: {cypher}")

        with self.driver.session() as session:
            results = session.run(cypher)
            raw = [r.data() for r in results]

        # Post-process with Gemini
        final = clean_results(raw, user_request)
        return final
    

# ---------------- Example Run ----------------
if __name__ == "__main__":
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "auxothon25"

    kg = KGAssistant(uri, user, password)

    try:
        while True:
            user_question = input("\nAsk a question (or type 'exit' to quit): ")
            if user_question.lower() in ["exit", "quit", "q"]:
                break

            answer = kg.query(user_question)
            print("\n--- Final Answer ---")
            print(answer)
    finally:
        kg.close()
