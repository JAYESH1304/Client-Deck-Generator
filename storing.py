
"""
End-to-end example: store ONE deck JSON in Neo4j, then retrieve pieces for LLM use.
"""

import os
import re
import json
from datetime import datetime
from typing import Any, Optional
from neo4j import GraphDatabase


def slugify(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def snake(s: str) -> str:
    s = re.sub(r'[^0-9a-zA-Z]+', ' ', s).strip()
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s)
    return '_'.join(s.lower().split())


def parse_date_to_iso(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    fmts = ["%B %Y", "%b %Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y"]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.date().isoformat()
        except Exception:
            pass
    try:
        dt = datetime(int(s), 1, 1)
        return dt.date().isoformat()
    except Exception:
        return None

def load_decks_from_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to match JSON blocks inside ```json ... ```
    pattern = r"```json\s*(\{.*?\})\s*```"
    matches = re.findall(pattern, content, flags=re.DOTALL)

    decks = []
    for m in matches:
        try:
            deck_json = json.loads(m)
            decks.append(deck_json)
        except json.JSONDecodeError as e:
            print("⚠️ Failed to parse deck JSON:", e)
    return decks


class DeckKG:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def ensure_constraints(self):
        queries = [
            "CREATE CONSTRAINT deck_id IF NOT EXISTS FOR (d:Deck) REQUIRE d.deck_id IS UNIQUE",
            "CREATE CONSTRAINT client_name IF NOT EXISTS FOR (c:Client) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE"
        ]
        with self.driver.session() as s:
            for q in queries:
                s.run(q)

    def upsert_deck(self, deck_json: Any) -> str:
        data = json.loads(deck_json) if isinstance(deck_json, str) else deck_json
        cover = data.get("Cover Slide", {})
        client = cover.get("Client name") or "Unknown"
        title = cover.get("Project title") or "Untitled Deck"
        version = cover.get("Version") or "1.0"
        company_branding = cover.get("Company branding") or None
        proposal_date_iso = parse_date_to_iso(cover.get("Proposal date") or "")

        deck_id = f"{slugify(title)}::{slugify(client)}::{version}"

        with self.driver.session() as s:
            s.execute_write(
                self._create_deck_tx,
                deck_id, title, version, proposal_date_iso, client, company_branding
            )

            for section_name, value in data.items():
                if section_name == "Cover Slide":
                    props = {
                        "client_name": client,
                        "company_branding": company_branding,
                        "proposal_date": proposal_date_iso,
                        "version": version,
                    }
                    s.execute_write(self._upsert_section_tx, deck_id, section_name, props)
                    continue

                if section_name == "Project Plan & Timeline" and isinstance(value, dict):
                    s.execute_write(self._upsert_section_tx, deck_id, section_name, {})
                    for phase_key, phase_obj in value.items():
                        if not isinstance(phase_obj, dict):
                            continue
                        order = None
                        m = re.search(r'(\d+)', phase_key)
                        if m:
                            order = int(m.group(1))
                        phase_props = {snake(k): v for k, v in phase_obj.items()}
                        phase_props["name"] = phase_key
                        if order is not None:
                            phase_props["order"] = order
                        s.execute_write(self._upsert_phase_tx, deck_id, section_name, phase_props)
                    continue

                if isinstance(value, dict):
                    props = {snake(k): v for k, v in value.items()}
                else:
                    props = {"text": str(value)}
                s.execute_write(self._upsert_section_tx, deck_id, section_name, props)

        return deck_id

    # ---------------- FIXED METHOD ----------------
    @staticmethod
    def _create_deck_tx(tx, deck_id, title, version, proposal_date_iso, client, company_branding):
        query = """
        MERGE (c:Client {name:$client})
        MERGE (d:Deck {deck_id:$deck_id})
        SET d.title=$title,
            d.version=$version,
            d.proposalDate = CASE WHEN $proposal_date IS NOT NULL 
                                  THEN date($proposal_date) 
                                  ELSE d.proposalDate END
        MERGE (c)-[:HAS_DECK]->(d)
        
        // ✅ Conditional merge for company branding without deprecated CALL
        WITH d, $company_branding AS company_branding
        FOREACH (_ IN CASE WHEN company_branding IS NOT NULL THEN [1] ELSE [] END |
            MERGE (co:Company {name:company_branding})
            MERGE (co)-[:BRANDED]->(d)
        )
        RETURN d
      """
        tx.run(
        query,
        deck_id=deck_id,
        title=title,
        version=version,
        proposal_date=proposal_date_iso,
        client=client,
        company_branding=company_branding,
        )
        # tx.run(
        #     """
        #     MERGE (c:Client {name:$client})
        #     MERGE (d:Deck {deck_id:$deck_id})
        #     SET d.title=$title,
        #         d.version=$version,
        #         d.proposalDate = CASE WHEN $proposal_date IS NOT NULL THEN date($proposal_date) ELSE d.proposalDate END
        #     MERGE (c)-[:HAS_DECK]->(d)
        #     WITH d
        #     CALL {
        #       WITH d
        #       WITH d WHERE $company_branding IS NOT NULL
        #       MERGE (co:Company {name:$company_branding})
        #       MERGE (co)-[:BRANDED]->(d)
        #       RETURN 1 AS dummy
        #     }
        #     RETURN d
        #     """,
        #     deck_id=deck_id,
        #     title=title,
        #     version=version,
        #     proposal_date=proposal_date_iso,
        #     client=client,
        #     company_branding=company_branding,
        # )


    @staticmethod
    def _upsert_section_tx(tx, deck_id, section_name, props):
        tx.run(
            """
            MATCH (d:Deck {deck_id:$deck_id})
            MERGE (s:Section {deck_id:$deck_id, name:$name})
            SET s += $props
            MERGE (d)-[:HAS_SECTION]->(s)
            """,
            deck_id=deck_id,
            name=section_name,
            props=props,
        )

    @staticmethod
    def _upsert_phase_tx(tx, deck_id, parent_section_name, props):
        tx.run(
            """
            MATCH (d:Deck {deck_id:$deck_id})-[:HAS_SECTION]->(s:Section {name:$parent})
            MERGE (p:Phase {deck_id:$deck_id, name:$name})
            SET p += $props
            MERGE (s)-[:HAS_PHASE]->(p)
            """,
            deck_id=deck_id,
            parent=parent_section_name,
            name=props.get("name"),
            props=props,
        )

    # ---------- Retrieval helpers ----------
    def get_deck_structure(self, deck_id: str):
        with self.driver.session() as s:
            res = s.run(
            """
            MATCH (d:Deck {deck_id:$deck_id})-[:HAS_SECTION]->(s:Section)
            OPTIONAL MATCH (s)-[:HAS_PHASE]->(p:Phase)
            WITH d, s, p
            ORDER BY coalesce(p.order, 999)  // order phases first
            WITH d, s, collect(p { .name, .order, .duration, .objectives, .deliverables }) AS phases
            RETURN d.title AS title,
                   s.name AS section,
                   phases
            ORDER BY section
            """,
            deck_id=deck_id,
    )
        return res.data()


    def get_executive_summary(self, deck_id: str):
        with self.driver.session() as s:
            res = s.run(
                """
                MATCH (:Deck {deck_id:$deck_id})-[:HAS_SECTION]->(s:Section {name:'Executive Summary'})
                RETURN s.problem_statement AS problem_statement,
                       s.opportunity AS opportunity,
                       s.unique_position AS unique_position,
                       s.proposed_outcomes AS proposed_outcomes
                """,
                deck_id=deck_id,
            )
            return res.single()

    def get_phases(self, deck_id: str):
        with self.driver.session() as s:
            res = s.run(
                """
                MATCH (:Deck {deck_id:$deck_id})-[:HAS_SECTION]->(:Section {name:'Project Plan & Timeline'})-[:HAS_PHASE]->(p:Phase)
                RETURN p.name AS name,
                       p.order AS order,
                       p.duration AS duration,
                       p.objectives AS objectives,
                       p.deliverables AS deliverables
                ORDER BY p.order
                """,
                deck_id=deck_id,
            )
            return [r.data() for r in res]

    def build_llm_fewshot_example(self, deck_id: str):
        with self.driver.session() as s:
            deck_meta = s.run(
                """
                MATCH (c:Client)-[:HAS_DECK]->(d:Deck {deck_id:$deck_id})
                OPTIONAL MATCH (co:Company)-[:BRANDED]->(d)
                RETURN d.title AS title,
                       d.version AS version,
                       d.proposalDate AS proposalDate,
                       c.name AS client,
                       co.name AS branding
                """,
                deck_id=deck_id,
            ).single()

        exec_sum = self.get_executive_summary(deck_id)
        phases = self.get_phases(deck_id)

        return {
            "meta": dict(deck_meta) if deck_meta else {},
            "executive_summary": dict(exec_sum) if exec_sum else {},
            "phases": phases,
        }


# ---------------- MAIN ----------------
def main():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "auxothon25"

    # deck_path = "demo_deck.json"
    # if deck_path and os.path.exists(deck_path):
    #     with open(deck_path, "r", encoding="utf-8") as f:
    #         deck_json = f.read()
#     else:
#         # Fallback to embedded sample deck JSON
#         deck_json = r"""{
#   "Cover Slide": {
#     "Client name": "ADI",
#     "Project title": "Agentic AI Proposal",
#     "Company branding": "AuxoAI",
#     "Proposal date": "April 2025",
#     "Version": "1.0"
#   },
#   "Executive Summary": {
#     "Problem Statement": "Current data processes are slow, require specialized skills, and limit data accessibility for non-technical users.",
#     "Opportunity": "Unified self-service platform for data ingestion, transformation, governance, and analytics via multi-agent orchestration, enabling faster time-to-insight and data democratization.",
#     "Unique Position": "AI-powered platform offering a conversational interface for non-technical users, automating tasks across the data lifecycle, and integrating with existing tools (Fivetran, dbt, Snowflake, Dataiku, Atlan/Immuta, Datadog).",
#     "Proposed Outcomes": "Improved data accessibility, faster insights, reduced operational costs, enhanced data governance, improved data quality."
#   },
#   "Project Plan & Timeline": {
#     "Phase 1": {
#       "duration": "1.5 months",
#       "objectives": "Establish core knowledge base for Fivetran, implement basic NLU for ingestion requests, create fundamental API integration framework.",
#       "deliverables": "Core knowledge base, basic NLU implementation, fundamental API integration framework."
#     },
#     "Phase 2": {
#       "duration": "2 months",
#       "objectives": "AI-based relationship insights, support for top connectors, schema mapping recommendations, monitoring capabilities, AI-based custom connector build.",
#       "deliverables": "AI-based insights, connector support, schema mapping, monitoring dashboard, custom connector capability."
#     },
#     "Phase 3": {
#       "duration": "1 month",
#       "objectives": "Testing, refinement, and final deployment.",
#       "deliverables": "Production-ready agent, user documentation, training module."
#     }
#   }
# }"""

    deck_file_path = "output2.txt"
    decks = load_decks_from_file(deck_file_path)

    # for i, deck in enumerate(decks, start=1):
    #     print(f"\n--- Processing deck {i} ---")

        
        # print(json.dumps(deck, indent=2)[:500] + ("..." if len(json.dumps(deck, indent=2)) > 500 else ""))

    kg = DeckKG(uri, user, password)
    try:
        kg.ensure_constraints()

        for i, deck in enumerate(decks, start=1):
            deck_id = kg.upsert_deck(deck)
            print(f"✅ Stored deck {i}: deck_id={deck_id}")

    finally:
        kg.close()



if __name__ == "__main__":
    main()
