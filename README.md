#  AI Client Proposal Deck Generator

This project is a CLI-driven assistant that helps create professional proposal decks with AI support (Gemini). It also includes optional utilities for structuring decks into JSON and storing/querying them in Neo4j.

## What it does
- Collects client context (problem + solution) and iteratively finalizes the solution.
- Generates proposal slides (cover, executive summary, pricing, timeline, etc.).
- Tracks versions, logs sessions/changes, and exports a full proposal text file.
- Optional knowledge-graph utilities to store decks in Neo4j and query them via natural language.

## Requirements
- Python 3.7+
- Gemini API key (for AI generation)
- Dependencies in `requirements.txt`
- Optional: Neo4j running locally for the KG utilities

## Setup
```bash
pip install -r requirements.txt
```

Set environment variables (see `config.py` or `.env.sample`):
- `GEMINI_API_KEY` (required for AI generation)
- `GEMINI_MODEL` (default: gemini-1.5-flash)
- `OUTPUT_DIR` (default: proposals)
- `LOGS_DIR` (default: logs)
- `MEMORY_FILE` (default: proposal_agent_memory.json)
- `MAX_RETRIES`, `RETRY_DELAY`

Optional setup helper:
```bash
python setup.py
```

## Usage
### 1) Main interactive pipeline
```bash
python main.py
```
Input prompts:
- Client name (>= 2 chars)
- Problem statement (>= 20 chars)
- Tentative solution (>= 20 chars)
- Your company name

The assistant will:
1. Start a session and check prerequisites.
2. Suggest solution improvements and ask you to finalize.
3. Generate slides based on your commands (or full deck).
4. Export proposal and logs to `proposals/`.

### 2) Quick start (non-interactive inputs)
```bash
python main.py --client "Acme Logistics" \
  --problem "Manual scheduling causes delays and cost overruns" \
  --solution "AI-driven route optimization and predictive dispatch" \
  --company "AuxoAI"
```

### 3) Batch mode
```bash
python main.py --batch proposals.json
```
Batch file format (list of objects):
```json
[
  {
    "client_name": "TechCorp",
    "problem_statement": "Manual data processing causes errors and delays",
    "tentative_solution": "Automated data pipeline with AI validation",
    "company_name": "DataSolutions Pro"
  }
]
```

### 4) Trial/example run (no input needed)
```bash
python main.py --example
```
This runs `cli_interface.run_example()` with a hardcoded example:
- Client: TechCorp Industries
- Problem: manual data processing and compliance risks
- Solution: automated pipeline + AI validation + dashboard
It generates a few key slides and writes `example_proposal.txt`.

### 5) Generate dummy user input (testing)
```bash
python generate_user_input.py
```
Returns JSON with keys: `industry`, `problem_statement`, `user_approach`.

## Pipeline overview
### A) Proposal generation pipeline (main)
Entry point: `main.py`

1. `main.py` parses CLI args and routes to mode.
2. `cli_interface.ProposalDeckCLI` drives user interaction.
3. `conversational_agent.ConversationalAgent` handles the session:
   - Initializes `ProposalAgent`, `FlexibleCommandParser`, `OutputManager`.
   - Finalizes solution first (required).
4. `proposal_agent.ProposalAgent`:
   - Uses `MemoryManager` to load/save `proposal_agent_memory.json`.
   - Uses `AIGenerator` to call Gemini (or fallback).
   - Builds prompts and generates slide content.
5. `output_manager.OutputManager` writes logs and exports:
   - Session log and change log to `proposals/`.
   - Final proposal text via `export_proposal()`.

Execution flow for the default interactive run:
`main.py` -> `cli_interface.py` -> `conversational_agent.py` ->
`proposal_agent.py` -> (`ai_generator.py`, `memory_manager.py`, `command_parser.py`) ->
`output_manager.py` -> output files.

### B) Knowledge graph pipeline (optional)
This pipeline is separate from the proposal generator.

1. `deck-structurer.py`
   - Converts raw deck text (from `deck_texts.txt`) into structured JSON.
   - Writes results into `output.txt` (example outputs: `output1.txt`, `output2.txt`).
2. `storing.py`
   - Reads deck JSON blocks from `output2.txt` and upserts them into Neo4j.
   - Creates nodes for Client, Deck, Section, Phase.
3. `fetching.py`
   - Takes a natural-language question.
   - Gemini generates Cypher, runs query in Neo4j, then cleans results.
4. `delete_data.py`
   - Clears the Neo4j database (use with caution).

## Inputs and outputs
### Main pipeline inputs
- Interactive prompts or CLI flags `--client`, `--problem`, `--solution`, `--company`.
- Batch JSON list (see example above).

### Outputs
- `proposals/<Client>_session_<timestamp>.txt`
- `proposals/<Client>_changes_<timestamp>.txt`
- `proposals/<Client>_proposal_<timestamp>.txt`
- `proposals/<Client>_summary_<timestamp>.txt`
- `proposal_agent_memory.json` (persisted state)
- Logs: `proposal_generator.log`, `logs/app.log`

## File structure (key files)
```
.
|-- main.py
|-- cli_interface.py
|-- conversational_agent.py
|-- proposal_agent.py
|-- command_parser.py
|-- data_models.py
|-- ai_generator.py
|-- memory_manager.py
|-- output_manager.py
|-- config.py
|-- setup.py
|-- test_basic.py
|-- generate_user_input.py
|-- deck-structurer.py
|-- storing.py
|-- fetching.py
|-- delete_data.py
|-- local_connector.py
|-- requirements.txt
|-- proposals/
|-- logs/
|-- Auxo Proposals/
|-- deck_texts.txt
|-- deck_example.json
|-- demo_deck.json
|-- example_proposal.txt
|-- output1.txt
|-- output2.txt
```

## Notes
- If `GEMINI_API_KEY` is not set or the SDK is missing, the system falls back to placeholder content.
- Neo4j utilities assume a local database and hardcoded credentials in `fetching.py`, `storing.py`, `delete_data.py`.

## Quick sanity checks
```bash
python main.py --check
python test_basic.py
```
