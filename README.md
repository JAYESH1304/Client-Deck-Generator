# 🎯 AI Client Proposal Deck Generator

A CLI tool that generates professional client proposals in minutes using Google Gemini AI. Collect client context → AI refines solution → Generate slides → Export proposal.

---

## 🎯 Goal

Automate proposal creation by:
- Guiding users through client context (problem, solution)
- Iteratively refining solutions with AI suggestions
- Generating professional slides (cover, executive summary, pricing, ROI, etc.)
- Maintaining version history and session logs
- Optionally storing proposals in Neo4j for querying

---

## 🏗️ System Architecture

```
User Input
    ↓
┌────────────────────────────────────┐
│  cli_interface.py                  │  Input collection & validation
│  conversational_agent.py           │  Session orchestration
└────────────┬───────────────────────┘
             ↓
┌────────────────────────────────────┐
│  proposal_agent.py                 │  AI-powered slide generation
│  command_parser.py                 │  Command routing
└────────────┬───────────────────────┘
             ↓
┌────────────────────────────────────┐
│  ai_generator.py                   │  Gemini API calls
│                                    │  Retry logic & fallbacks
└────────────┬───────────────────────┘
             ↓
┌────────────────────────────────────┐
│  memory_manager.py                 │  State persistence (JSON)
│  output_manager.py                 │  File writing & logs
└────────────┬───────────────────────┘
             ↓
        Output Files
    proposals/ + logs/
```

---

## 📝 File Descriptions

| File | Purpose |
|------|---------|
| **main.py** | CLI entry point, mode routing (interactive/batch/example/check) |
| **cli_interface.py** | Display menus, collect/validate user input (min length checks) |
| **conversational_agent.py** | Orchestrate session, finalize solution, command loop |
| **proposal_agent.py** | Generate slides via Gemini (cover, summary, pricing, etc.) |
| **command_parser.py** | Parse commands (generate, export, list, edit) |
| **ai_generator.py** | Call Gemini with retry logic (max 3), fallback placeholders |
| **memory_manager.py** | Load/save session state to proposal_agent_memory.json |
| **output_manager.py** | Write proposals, logs, changes to disk |
| **data_models.py** | ClientInfo, Slide, ProposalData classes |
| **config.py** | Load .env variables, set defaults |
| **deck-structurer.py** | (Optional KG) Convert raw deck text → JSON |
| **storing.py** | (Optional KG) Store proposals in Neo4j |
| **fetching.py** | (Optional KG) Query Neo4j with natural language |

---

## 🔄 Complete Flow (User Query → Proposal)

### 1. **Input** (main.py, cli_interface.py)
```
python main.py  OR  python main.py --client "..." --problem "..." --solution "..." --company "..."

Collect:
- Client name (≥2 chars)
- Problem statement (≥20 chars)
- Solution (≥20 chars)
- Company name
```

### 2. **Initialization** (conversational_agent.py)
```
- Create session ID (timestamp)
- Initialize all components
- Validate API key & directories
- Load previous state if exists
```

### 3. **Solution Refinement** (proposal_agent.py)
```
Loop (max 5 iterations):
  1. Send to Gemini: "Suggest improvements to [solution]"
  2. Display suggestions to user
  3. User chooses: yes/no/edit
  4. If edit: update and loop
  5. If yes/no: finalize and exit
```

### 4. **Slide Generation** (command_parser.py → proposal_agent.py → ai_generator.py)
```
User commands:
  "generate cover" → Build prompt → Call Gemini → Parse → Store → Log
  "generate executive_summary" → ...
  "generate full_deck" → Generate all slides sequentially
  "export proposal" → Assemble all slides → Write to file
```

**For each slide:**
```
Build prompt:
  System: "You are a proposal writer"
  Context: client_name, problem, solution, company
  Task: "Create [slide_type]"
        ↓
Call ai_generator.generate(prompt)
  - Send to Gemini
  - If error: Retry (wait 1s, 2s, 4s)
  - If all fail: Return placeholder template
        ↓
Parse response & store in memory
        ↓
Log action to file
        ↓
Display to user
```

### 5. **Export** (output_manager.py)
```
Files created:
- proposals/<Client>_proposal_<timestamp>.txt          (Full deck)
- proposals/<Client>_session_<timestamp>.txt            (Session log)
- proposals/<Client>_changes_<timestamp>.txt            (Change log)
- proposals/<Client>_summary_<timestamp>.txt            (Summary)
- proposal_agent_memory.json                            (State)
- logs/app.log, proposal_generator.log                  (Logs)
```

---

## 📊 Usage Modes

| Mode | Command | When to Use |
|------|---------|------------|
| **Interactive** | `python main.py` | Default, guided experience |
| **Quick Start** | `python main.py --client "X" --problem "Y" --solution "Z" --company "W" --auto-export` | Non-interactive, full pipeline |
| **Batch** | `python main.py --batch proposals.json` | Process multiple clients |
| **Example** | `python main.py --example` | Demo with hardcoded data |
| **Check** | `python main.py --check` | Validate setup (API key, directories, packages) |

---

## ⚙️ Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env
cp .env.sample .env

# 3. Edit .env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
OUTPUT_DIR=proposals
LOGS_DIR=logs
MEMORY_FILE=proposal_agent_memory.json
MAX_RETRIES=3
RETRY_DELAY=1

# 4. Verify
python main.py --check

# 5. Run
python main.py
```

---

## 🔍 Example Flow

```bash
$ python main.py

Client name: TechCorp Industries
Problem: Manual data processing causes errors and risks
Solution: Automated pipeline with AI validation
Company: DataSolutions Pro

AI suggests:
  "Add real-time monitoring dashboard"
  "Include compliance reporting"
  "Add data quality metrics"

Accept? (yes/no/edit): yes
✓ Solution finalized

Available commands:
> generate cover
> generate executive_summary
> generate full_deck
> export proposal
> help
> exit

Command: generate full_deck
✓ Generating all slides...
  ✓ Cover slide
  ✓ Executive summary
  ✓ Problem statement
  ✓ Solution overview
  ✓ Implementation timeline
  ✓ Pricing
  ✓ ROI analysis

Command: export proposal
✓ Proposal exported:
  - proposals/TechCorp_Industries_proposal_20240315_143022.txt
  - proposals/TechCorp_Industries_session_20240315_143022.txt

Command: exit
Session ended.
```

---

## ⚠️ Limitations

1. **API Dependent** - Requires Gemini API key, no offline mode
2. **No Parallelization** - Batch processing is sequential
3. **Neo4j Optional** - KG features require local/remote Neo4j with hardcoded credentials
4. **Fixed Slide Types** - Can't add custom sections, only AI-generated content
5. **Basic Version Control** - No branching, only latest state saved
6. **No Content Caching** - Every slide calls Gemini (same request = new API call)
7. **Limited Customization** - No branding/styling options
8. **Input Constraints** - Client ≥2 chars, Problem ≥20 chars, Solution ≥20 chars

---

## 🚀 Future Improvements

### Performance & Scalability
- [ ] Add response caching (Redis) to avoid repeated Gemini calls
- [ ] Batch API calls (1 request for multiple slides instead of N)
- [ ] Parallel batch processing (4+ proposals simultaneously)
- [ ] Pre-built template library for common slides

### User Experience
- [ ] Web UI (Flask/React) instead of CLI-only
- [ ] Real-time proposal preview
- [ ] Undo/redo functionality
- [ ] Custom slide templates
- [ ] Branding & styling options (logo, colors, fonts)

### Content Quality
- [ ] Few-shot examples in prompts (better output quality)
- [ ] Industry-specific templates (fintech, healthcare, SaaS)
- [ ] Multi-language support
- [ ] Content review/approval workflow before export
- [ ] Tone/style options (formal vs conversational)

### Data Management
- [ ] Cloud storage (Google Drive, S3)
- [ ] Proposal versioning with git-like branches
- [ ] Full-text search across proposals
- [ ] Save as template → reuse
- [ ] Analytics (generation time, approval rates, win rates)

### Advanced Features
- [ ] PDF export (not just text)
- [ ] Email delivery
- [ ] Proposal signing/approval workflow
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] A/B testing different proposals
- [ ] Client feedback loops

### Neo4j Enhancement
- [ ] Auto-structure proposals to Neo4j (no manual deck-structurer.py)
- [ ] Advanced queries (similarity, clustering)
- [ ] Credential abstraction (environment variables)

### AI Model Support
- [ ] Support multiple LLMs (Claude, GPT-4, LLaMA)
- [ ] Fine-tuning on company's historical proposals
- [ ] Hybrid approach: templates + AI customization

### Production Readiness
- [ ] Authentication & multi-user support
- [ ] Audit logging (who did what, when)
- [ ] Rate limiting per user
- [ ] Database persistence (PostgreSQL instead of JSON)
- [ ] Load testing & resilience testing

---

## 🧪 Testing

```bash
python main.py --check                 # Health check
python test_basic.py                   # Unit tests
python main.py --example               # Test run with example
python generate_user_input.py          # Generate test data
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "GEMINI_API_KEY not configured" | Add key to .env: `GEMINI_API_KEY=your_key` |
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| "Permission denied" | `chmod 755 proposals/ logs/` |
| "JSON decode error" | Delete corrupted `proposal_agent_memory.json`, recreates on next run |
| "API rate limit" | Increase `RETRY_DELAY` in .env, use cheaper model |
| "Neo4j connection failed" | KG features optional, main pipeline works without it |

---

## 📁 Output Structure

```
proposals/
  ├─ <Client>_proposal_<timestamp>.txt       Full proposal
  ├─ <Client>_session_<timestamp>.txt        Session log
  ├─ <Client>_changes_<timestamp>.txt        Change history
  ├─ <Client>_summary_<timestamp>.txt        Summary
  └─ example_proposal.txt                    Example output

logs/
  ├─ app.log                                 General logs
  └─ proposal_generator.log                  Specific logs

proposal_agent_memory.json                   Session state (JSON)
```

---

## 📌 Quick Start

```bash
# Setup
pip install -r requirements.txt
cp .env.sample .env
# Edit .env with GEMINI_API_KEY

# Run
python main.py                    # Interactive
python main.py --example          # Test with example
python main.py --check            # Verify setup

# Output
ls proposals/                      # View generated proposals
```

---

**Version:** 1.0 | **Status:** Production-Ready
