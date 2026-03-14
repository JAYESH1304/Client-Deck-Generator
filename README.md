# 🎯 AI Client Proposal Deck Generator - Comprehensive Guide

A sophisticated CLI-driven assistant that leverages AI (Google Gemini) to generate professional proposal decks for clients. The system handles proposal generation with iterative refinement, version tracking, and optional knowledge graph storage using Neo4j.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [What It Does](#what-it-does)
3. [System Architecture](#system-architecture)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [Core Components](#core-components)
8. [Data Models](#data-models)
9. [Workflow Examples](#workflow-examples)
10. [Advanced Features](#advanced-features)
11. [Knowledge Graph Pipeline](#knowledge-graph-pipeline)
12. [Error Handling & Fallbacks](#error-handling--fallbacks)
13. [File Structure](#file-structure)
14. [Testing & Validation](#testing--validation)
15. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

The **AI Client Proposal Deck Generator** is an enterprise-grade tool designed to streamline the proposal creation process. Instead of manually crafting proposal documents, users interact with an intelligent CLI assistant that:

- Gathers client context through guided prompts
- Uses AI (Google Gemini) to generate high-quality proposal content
- Maintains conversation history and version tracking
- Exports professional proposal documents
- Optionally stores proposals in a Neo4j knowledge graph for querying

### Key Innovation

This system combines **interactive CLI workflows** with **LLM intelligence** to create professional proposals in minutes instead of hours. The iterative refinement process ensures the solution fits the client's needs before full proposal generation.

---

## 🚀 What It Does

### 1. **Proposal Generation Pipeline** (Main)

The core workflow collects information and generates proposal slides:

```
User Input (Client Context)
    ↓
Session Initialization
    ↓
Solution Finalization (Iterative)
    ↓
Slide Generation (Multiple Types)
    ↓
Proposal Export
    ↓
Output Files (Text, Logs, Summary)
```

### 2. **Key Capabilities**

#### A. Context Collection
- Client name validation (≥ 2 characters)
- Problem statement capture (≥ 20 characters)
- Tentative solution description (≥ 20 characters)
- Company name specification

#### B. Solution Refinement
- AI suggests improvements to the initial solution
- Interactive back-and-forth to finalize approach
- Ensures alignment before proposal generation

#### C. Slide Generation
The system can generate various slide types:
- **Cover Slide** - Client name, company, date
- **Executive Summary** - High-level overview of solution
- **Problem Statement** - Detailed problem context
- **Solution Overview** - Proposed approach
- **Key Benefits** - Value proposition
- **Implementation Timeline** - Phases and milestones
- **Pricing** - Cost structure
- **Case Studies** - Similar project examples
- **Risk Mitigation** - Contingency planning
- **Technical Architecture** - Solution design
- **ROI Analysis** - Return on investment
- **Closing Slide** - Call to action

#### D. Version Tracking
- Maintains session logs with timestamps
- Tracks all changes and iterations
- Enables proposal history and rollback
- Stores memory in persistent JSON file

#### E. Export & Documentation
- Generates comprehensive proposal text files
- Creates change logs for audit trails
- Produces summaries for quick reference
- Logs all actions for compliance

### 3. **Knowledge Graph Pipeline** (Optional)

For organizations wanting to store and query proposals:

- **Structure** - Convert raw deck text to JSON format
- **Store** - Persist proposals in Neo4j database
- **Query** - Retrieve proposals using natural language
- **Manage** - Delete data and maintain database

---

## 🏗️ System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│                     (CLI - main.py)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Interaction Layer                             │
│              (cli_interface.py & conversational_agent.py)       │
│                                                                  │
│  ├─ Session management                                          │
│  ├─ User input validation                                       │
│  ├─ Command routing                                             │
│  └─ Interactive prompts                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Proposal    │  │  Command     │  │  Memory          │
│  Agent       │  │  Parser      │  │  Manager         │
│              │  │              │  │                  │
│ - AI calls   │  │ - Parse user │  │ - Load state     │
│ - Prompts    │  │   commands   │  │ - Save state     │
│ - Generation │  │ - Route to   │  │ - Persistence    │
│              │  │   modules    │  │                  │
└──────────────┘  └──────────────┘  └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Integration Layer                          │
│                  (ai_generator.py)                              │
│                                                                  │
│  ├─ Gemini API calls                                            │
│  ├─ Prompt engineering                                          │
│  ├─ Response parsing                                            │
│  └─ Fallback mechanisms                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Google       │  │ Response     │  │ Error            │
│ Gemini API   │  │ Formatting   │  │ Handling         │
│              │  │              │  │                  │
│ - LLM calls  │  │ - Parse JSON │  │ - Retries        │
│ - Models     │  │ - Validate   │  │ - Fallbacks      │
│              │  │   structure  │  │ - Logging        │
└──────────────┘  └──────────────┘  └──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output Layer                                  │
│                (output_manager.py)                              │
│                                                                  │
│  ├─ File writing                                                │
│  ├─ Log management                                              │
│  ├─ Export formatting                                           │
│  └─ Directory organization                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Proposal     │  │ Session      │  │ Change           │
│ Text Files   │  │ Logs         │  │ Logs             │
│              │  │              │  │                  │
│ proposals/   │  │ logs/        │  │ proposals/       │
│ <client>_    │  │ app.log      │  │ <client>_changes │
│ proposal_    │  │ proposal_    │  │ _<timestamp>.txt │
│ <time>.txt   │  │ generator.log│  │                  │
└──────────────┘  └──────────────┘  └──────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Input Sources                                                    │
├─────────────────────────────────────────────────────────────────┤
│ • Interactive CLI prompts                                       │
│ • Command-line arguments (--client, --problem, etc.)           │
│ • Batch JSON file (proposals.json)                             │
│ • Example hardcoded data (--example flag)                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Validation & Normalization                                      │
├─────────────────────────────────────────────────────────────────┤
│ • Input length validation                                       │
│ • Character encoding checks                                     │
│ • Data type validation                                          │
│ • Whitespace normalization                                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Session Initialization                                          │
├─────────────────────────────────────────────────────────────────┤
│ • Create unique session ID (timestamp-based)                    │
│ • Initialize memory manager                                     │
│ • Load previous state (if exists)                               │
│ • Check prerequisites (API keys, directories)                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Solution Finalization Loop                                      │
├─────────────────────────────────────────────────────────────────┤
│ 1. AI suggests improvements to solution                         │
│ 2. User reviews and edits                                       │
│ 3. Loop until user confirms (or max iterations)                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Slide Generation (User-Initiated)                               │
├─────────────────────────────────────────────────────────────────┤
│ • User issues command: "generate cover slide"                   │
│ • Parser routes to appropriate generator                        │
│ • AI creates content based on context                           │
│ • Content validated and stored                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Version Management & Persistence                                │
├─────────────────────────────────────────────────────────────────┤
│ • Store generated slides in memory                              │
│ • Track changes in change log                                   │
│ • Save state to JSON file                                       │
│ • Log all actions to file                                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Export & Output                                                 │
├─────────────────────────────────────────────────────────────────┤
│ • Assemble all slides into proposal                             │
│ • Format for readability                                        │
│ • Create summary document                                       │
│ • Write to proposal/ directory with timestamp                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Output Files                                                    │
├─────────────────────────────────────────────────────────────────┤
│ • proposals/<Client>_proposal_<timestamp>.txt                   │
│ • proposals/<Client>_session_<timestamp>.txt                    │
│ • proposals/<Client>_changes_<timestamp>.txt                    │
│ • proposals/<Client>_summary_<timestamp>.txt                    │
│ • proposal_agent_memory.json                                    │
│ • logs/app.log                                                  │
│ • proposal_generator.log                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💾 Installation & Setup

### Prerequisites

- **Python 3.7+** - Core language requirement
- **Google Gemini API Key** - For AI generation (required)
- **pip** - Python package manager
- **Optional: Neo4j** - For knowledge graph features (local or remote)

### Step 1: Clone or Extract Project

```bash
cd ai-proposal-generator
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**

```
google-generativeai==0.3.0+    # Google Gemini API
python-dotenv==1.0.0+          # Environment variable management
neo4j==5.0+                    # Neo4j driver (optional)
pydantic==2.0+                 # Data validation
requests==2.31+                # HTTP client
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.sample .env
```

Edit `.env` with your configuration:

```env
# Required - Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Optional - Output directories
OUTPUT_DIR=proposals
LOGS_DIR=logs
MEMORY_FILE=proposal_agent_memory.json

# Optional - Retry configuration
MAX_RETRIES=3
RETRY_DELAY=1

# Optional - Neo4j (for knowledge graph features)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Step 5: Verify Installation

```bash
# Quick sanity check
python main.py --check

# Run basic tests
python test_basic.py

# Generate example proposal
python main.py --example
```

---

## ⚙️ Configuration

The system uses a hierarchical configuration approach:

### Configuration Sources (Priority Order)

1. **Environment Variables** (.env file)
2. **config.py** (defaults)
3. **Runtime Arguments** (CLI flags override everything)

### Configuration File (config.py)

```python
# config.py structure

class ProposalConfig:
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Directory Configuration
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "proposals")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")
    MEMORY_FILE = os.getenv("MEMORY_FILE", "proposal_agent_memory.json")
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))
    
    # Neo4j Configuration (Optional)
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    # Validation Rules
    MIN_CLIENT_NAME_LENGTH = 2
    MIN_PROBLEM_LENGTH = 20
    MIN_SOLUTION_LENGTH = 20
```

### Key Configuration Parameters

| Parameter | Default | Description | Required |
|-----------|---------|-------------|----------|
| `GEMINI_API_KEY` | None | Google Gemini API key | ✓ Yes |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Model to use for generation | No |
| `OUTPUT_DIR` | `proposals` | Where to save proposal files | No |
| `LOGS_DIR` | `logs` | Where to save log files | No |
| `MEMORY_FILE` | `proposal_agent_memory.json` | State persistence file | No |
| `MAX_RETRIES` | 3 | API retry attempts | No |
| `RETRY_DELAY` | 1 | Seconds between retries | No |

---

## 📖 Usage Guide

### 1. Interactive Mode (Default)

The most common use case - interactive prompts guide you through the process.

```bash
python main.py
```

**What happens:**

```
1. Startup Check
   ├─ Validate API key
   ├─ Create necessary directories
   └─ Load previous state (if any)

2. Collect Client Context
   ├─ Prompt: "Enter client name (≥ 2 chars):"
   │  Input: "Acme Logistics"
   ├─ Prompt: "Describe the problem (≥ 20 chars):"
   │  Input: "Manual scheduling causes delays and cost overruns"
   ├─ Prompt: "Tentative solution (≥ 20 chars):"
   │  Input: "AI-driven route optimization and predictive dispatch"
   └─ Prompt: "Your company name:"
      Input: "AuxoAI"

3. Solution Finalization
   ├─ AI suggests improvements
   ├─ Display suggestions to user
   ├─ Prompt: "Do you want to refine the solution? (yes/no/edit):"
   │  If "edit": User can modify solution
   │  If "no": Proceed to slide generation
   └─ Loop until user confirms

4. Slide Generation Menu
   ├─ Display available commands:
   │  • "generate cover"
   │  • "generate executive_summary"
   │  • "generate full_deck"
   │  • "export proposal"
   │  • "exit"
   ├─ User issues commands
   ├─ System generates content
   └─ Display generated slides

5. Export & Completion
   ├─ User types "export proposal"
   ├─ System assembles all slides
   ├─ Writes to proposals/ directory
   └─ Displays file paths
```

**Example Interactive Session:**

```
$ python main.py

========================================
   AI Proposal Deck Generator
========================================

Starting new session...
✓ API key validated
✓ Directories created

--- Client Information ---
Enter client name (minimum 2 characters): TechCorp Industries
Enter problem statement (minimum 20 characters): Manual data processing causes errors and compliance risks
Enter tentative solution (minimum 20 characters): Automated data pipeline with AI validation
Your company name: DataSolutions Pro

--- Solution Finalization ---

AI Assistant suggests:
"Your solution could benefit from:
1. Real-time monitoring dashboard
2. Automated compliance reporting
3. Data quality metrics
"

Proceed with original solution? (yes/no/edit): edit
Modified solution: Automated data pipeline with AI validation, real-time dashboard, and compliance reporting
Finalized! Moving to slide generation...

--- Slide Generation ---
Available commands:
  > generate cover
  > generate executive_summary
  > generate problem_statement
  > generate full_deck
  > export proposal
  > help
  > exit

Command: generate cover

✓ Cover slide generated
  Title: TechCorp Industries Proposal
  Date: 2024-03-15

Command: export proposal

✓ Proposal exported successfully
Files created:
  - proposals/TechCorp_Industries_proposal_20240315_143022.txt
  - proposals/TechCorp_Industries_session_20240315_143022.txt
  - proposals/TechCorp_Industries_changes_20240315_143022.txt
  - proposals/TechCorp_Industries_summary_20240315_143022.txt

Done! Your proposal is ready.
```

### 2. Quick Start with CLI Arguments

Provide all inputs via command-line flags - no prompts:

```bash
python main.py \
  --client "Acme Logistics" \
  --problem "Manual scheduling causes delays and cost overruns" \
  --solution "AI-driven route optimization and predictive dispatch" \
  --company "AuxoAI"
```

**Parameters:**
- `--client` - Client name (≥ 2 chars)
- `--problem` - Problem statement (≥ 20 chars)
- `--solution` - Proposed solution (≥ 20 chars)
- `--company` - Your company name
- `--auto-export` (optional) - Skip menu, export automatically

**With auto-export:**

```bash
python main.py \
  --client "TechCorp" \
  --problem "Manual data processing issues" \
  --solution "Automated AI pipeline" \
  --company "DataSolutions" \
  --auto-export
```

This runs the entire pipeline without user interaction.

### 3. Batch Mode

Process multiple proposals from a JSON file:

```bash
python main.py --batch proposals.json
```

**Batch file format (proposals.json):**

```json
[
  {
    "client_name": "TechCorp",
    "problem_statement": "Manual data processing causes errors and delays",
    "tentative_solution": "Automated data pipeline with AI validation",
    "company_name": "DataSolutions Pro"
  },
  {
    "client_name": "Acme Logistics",
    "problem_statement": "Route scheduling causes delays and cost overruns",
    "tentative_solution": "AI-driven route optimization system",
    "company_name": "RouteAI Solutions"
  },
  {
    "client_name": "FinanceFlow",
    "problem_statement": "Compliance reporting takes weeks manually",
    "tentative_solution": "Real-time automated compliance dashboard",
    "company_name": "FinTech Automation"
  }
]
```

**Execution:**

```
Processing batch mode...
[1/3] TechCorp - Generating proposal...
  ✓ Generated proposal_TechCorp_20240315_143022.txt
[2/3] Acme Logistics - Generating proposal...
  ✓ Generated proposal_Acme_Logistics_20240315_143045.txt
[3/3] FinanceFlow - Generating proposal...
  ✓ Generated proposal_FinanceFlow_20240315_143101.txt

Batch complete! 3 proposals generated.
```

### 4. Example Mode (No Input Needed)

Run with hardcoded example data - useful for testing or demonstration:

```bash
python main.py --example
```

**Executes:**

```
Running example proposal generation...

Client: TechCorp Industries
Problem: Manual data processing and compliance risks
Solution: Automated pipeline + AI validation + dashboard

✓ Generating slides...
✓ Cover slide created
✓ Executive summary created
✓ Problem statement created
✓ Solution overview created
✓ Implementation timeline created
✓ Pricing details created

✓ Example proposal exported to: example_proposal.txt
```

**Output file (example_proposal.txt):**

```
================================================================================
                        PROPOSAL: TechCorp Industries
                          DataSolutions Pro
                            March 15, 2024
================================================================================

COVER SLIDE
-----------
Client: TechCorp Industries
Date: 2024-03-15
Proposed by: DataSolutions Pro

EXECUTIVE SUMMARY
-----------------
TechCorp Industries currently faces significant challenges with manual data 
processing, leading to errors and compliance risks. Our automated solution 
will streamline operations and ensure compliance.

[Additional slides follow...]
```

### 5. Testing & Validation

Generate dummy user input for testing:

```bash
python generate_user_input.py
```

**Output:**

```json
{
  "industry": "Technology",
  "problem_statement": "Legacy system integration complexities",
  "user_approach": "Cloud-based microservices architecture"
}
```

### 6. Sanity Check

Verify system health:

```bash
python main.py --check
```

**Checks:**

```
Performing sanity checks...

✓ Python version: 3.9.1
✓ Required packages installed
✓ Gemini API key: [CONFIGURED]
✓ Output directory exists: proposals/
✓ Logs directory exists: logs/
✓ Memory file accessible: proposal_agent_memory.json
✓ API connectivity: OK

All checks passed! System ready.
```

---

## 🧩 Core Components

### 1. **main.py** - Entry Point

**Responsibility:** Parse CLI arguments and route to appropriate mode

**Key Functions:**

```python
def main():
    """
    Main entry point. Routes to different modes:
    - Interactive (default)
    - Quick start (--client, --problem, --solution, --company)
    - Batch (--batch)
    - Example (--example)
    - Check (--check)
    """

def parse_arguments():
    """Parse and validate CLI arguments"""
    # Returns argparse namespace with all flags
```

**CLI Arguments:**

```
Positional:
  None (modes are determined by flags)

Optional:
  --client TEXT          Client name
  --problem TEXT         Problem statement
  --solution TEXT        Proposed solution
  --company TEXT         Company name
  --batch FILE           Batch JSON file path
  --example              Run with hardcoded example
  --auto-export          Skip menu, auto-export
  --check                Sanity check
  --help                 Show help message
```

### 2. **cli_interface.py** - User Interaction Layer

**Responsibility:** Handle all user prompts, validation, and menu displays

**Key Classes:**

```python
class ProposalDeckCLI:
    def __init__(self):
        """Initialize CLI interface"""
    
    def display_welcome(self):
        """Show welcome banner"""
    
    def collect_client_info(self):
        """
        Prompt user for:
        - Client name (validated ≥ 2 chars)
        - Problem statement (validated ≥ 20 chars)
        - Tentative solution (validated ≥ 20 chars)
        - Company name
        """
        return client_info_dict
    
    def display_ai_suggestions(self, suggestions):
        """Display AI-generated suggestions for solution"""
    
    def get_user_choice(self, options):
        """Get user choice from options"""
    
    def display_menu(self):
        """Show main command menu"""
    
    def display_slide(self, slide_content):
        """Pretty-print generated slide content"""
    
    def run_example(self):
        """Execute example proposal with hardcoded data"""
```

**Input Validation:**

```python
def validate_input(text, min_length):
    """
    Validate user input:
    - Check minimum length
    - Strip whitespace
    - Check for valid characters
    - Return validated or None
    """
```

### 3. **conversational_agent.py** - Session Orchestrator

**Responsibility:** Manage the entire session workflow

**Key Classes:**

```python
class ConversationalAgent:
    def __init__(self):
        """
        Initialize all sub-components:
        - CLI interface
        - Proposal agent
        - Command parser
        - Output manager
        - Memory manager
        """
    
    def run_session(self, client_info):
        """
        Main session orchestrator:
        1. Initialize session
        2. Finalize solution
        3. Start command loop
        4. Handle user commands
        5. Export on exit
        """
    
    def finalize_solution(self, initial_solution):
        """
        Iterative solution refinement:
        1. Generate AI suggestions
        2. Display to user
        3. Get user feedback
        4. Update solution if needed
        5. Repeat until confirmed
        """
    
    def command_loop(self):
        """
        Main interactive loop:
        - Display menu
        - Get user command
        - Route to appropriate handler
        - Display results
        - Repeat until exit
        """
```

**Session Workflow:**

```
ConversationalAgent
├─ Initialize components
├─ Validate prerequisites
├─ Check API connectivity
├─ Load/create session
├─ Enter finalize_solution loop
│  ├─ Generate improvements
│  ├─ Display suggestions
│  ├─ Get feedback
│  └─ Loop until confirmed
├─ Enter command_loop
│  ├─ Parse command
│  ├─ Route to module
│  ├─ Generate content
│  ├─ Display result
│  └─ Log action
└─ Export on completion
```

### 4. **proposal_agent.py** - Core Logic

**Responsibility:** Generate proposal content using AI

**Key Classes:**

```python
class ProposalAgent:
    def __init__(self):
        """
        Initialize with:
        - AIGenerator (for Gemini calls)
        - MemoryManager (for state)
        - OutputManager (for logging)
        """
    
    def generate_slide(self, slide_type, context):
        """
        Generate specific slide type:
        
        slide_type options:
        - "cover" -> Title, date, client info
        - "executive_summary" -> High-level overview
        - "problem_statement" -> Problem details
        - "solution_overview" -> Solution approach
        - "key_benefits" -> Value proposition
        - "implementation_timeline" -> Phases
        - "pricing" -> Cost structure
        - "case_studies" -> Examples
        - "risk_mitigation" -> Contingencies
        - "technical_architecture" -> Design
        - "roi_analysis" -> Return on investment
        - "closing_slide" -> Call to action
        """
    
    def generate_full_deck(self):
        """Generate all slide types in sequence"""
    
    def suggest_solution_improvements(self, solution):
        """AI-generated suggestions for solution refinement"""
    
    def save_state(self):
        """Persist current state to memory"""
    
    def load_state(self):
        """Load previous session state"""
```

**Slide Generation Process:**

```
generate_slide("cover", context)
├─ Build prompt:
│  ├─ System message: "You are a proposal writer"
│  ├─ Context: client name, company, date
│  └─ Instruction: "Create a professional cover slide"
├─ Call AIGenerator.generate()
├─ Parse response
├─ Validate structure
├─ Store in memory
├─ Log generation
└─ Return formatted slide
```

### 5. **command_parser.py** - Input Interpretation

**Responsibility:** Parse and route user commands

**Key Classes:**

```python
class FlexibleCommandParser:
    def __init__(self):
        """Define all recognized commands"""
    
    def parse(self, user_input):
        """
        Parse user input and return:
        {
            "command": "generate",
            "slide_type": "executive_summary",
            "parameters": {...}
        }
        """
    
    def get_available_commands(self):
        """Return list of valid commands"""
    
    def suggest_command(self, partial_input):
        """Fuzzy match and suggest similar commands"""
```

**Recognized Commands:**

```
generate <slide_type>
  - generate cover
  - generate executive_summary
  - generate problem_statement
  - generate solution_overview
  - generate implementation_timeline
  - generate pricing
  - generate full_deck

manage
  - list slides
  - delete slide <name>
  - edit slide <name>
  - show slide <name>

export
  - export proposal
  - export summary
  - export session_log

session
  - status
  - reset
  - load <session_id>

help/exit
```

### 6. **ai_generator.py** - LLM Interface

**Responsibility:** Interface with Google Gemini API

**Key Classes:**

```python
class AIGenerator:
    def __init__(self, api_key, model):
        """Initialize Gemini client"""
    
    def generate(self, prompt, max_tokens=2000):
        """
        Call Gemini API with retry logic:
        
        Steps:
        1. Check API key availability
        2. Call Gemini API
        3. Parse response
        4. Handle errors with retries
        5. Return formatted result
        
        Returns: Generated text or fallback
        """
    
    def generate_with_fallback(self, prompt):
        """
        Generate with fallback if API fails:
        
        Try order:
        1. Gemini API call
        2. Retry with backoff (MAX_RETRIES)
        3. Return placeholder content
        """
    
    def estimate_tokens(self, text):
        """Rough token count estimation"""
```

**Error Handling:**

```
APIError
├─ Retry logic
│  ├─ Wait RETRY_DELAY seconds
│  ├─ Increment attempt counter
│  └─ Retry up to MAX_RETRIES times
├─ If all retries fail
│  └─ Return fallback placeholder content
└─ Log error for debugging
```

### 7. **memory_manager.py** - State Persistence

**Responsibility:** Save and load session state

**Key Classes:**

```python
class MemoryManager:
    def __init__(self, memory_file):
        """Initialize with JSON memory file path"""
    
    def save(self, proposal_data):
        """
        Persist state to JSON:
        {
            "session_id": "20240315_143022",
            "client_name": "TechCorp",
            "problem": "...",
            "solution": "...",
            "slides": {
                "cover": {...},
                "executive_summary": {...}
            },
            "timestamp": "2024-03-15T14:30:22",
            "version": 1
        }
        """
    
    def load(self):
        """Load most recent state from JSON"""
    
    def load_by_session_id(self, session_id):
        """Load specific session by ID"""
    
    def get_all_sessions(self):
        """List all saved sessions"""
```

**Memory File Structure:**

```json
{
  "sessions": [
    {
      "session_id": "20240315_143022",
      "client_name": "TechCorp",
      "company_name": "DataSolutions",
      "problem_statement": "Manual data processing causes errors",
      "initial_solution": "Automated pipeline",
      "final_solution": "Automated pipeline with AI validation",
      "slides": {
        "cover": {
          "title": "TechCorp Industries Proposal",
          "date": "2024-03-15",
          "company": "DataSolutions Pro"
        },
        "executive_summary": {
          "content": "..."
        }
      },
      "changes": [
        {
          "timestamp": "2024-03-15T14:30:25",
          "action": "generated slide: cover",
          "details": "..."
        }
      ],
      "created_at": "2024-03-15T14:30:22",
      "updated_at": "2024-03-15T14:31:45"
    }
  ]
}
```

### 8. **output_manager.py** - File & Log Management

**Responsibility:** Write files, manage logs, format output

**Key Classes:**

```python
class OutputManager:
    def __init__(self, output_dir, logs_dir):
        """Initialize with directory paths"""
    
    def export_proposal(self, proposal_data, client_name):
        """
        Export complete proposal:
        - Assemble all slides
        - Format with separators
        - Write to proposals/ directory
        - Return file path
        """
    
    def export_session_log(self, session_data, client_name):
        """Export detailed session log"""
    
    def export_change_log(self, changes, client_name):
        """Export change history"""
    
    def export_summary(self, summary_data, client_name):
        """Export executive summary"""
    
    def write_log(self, level, message):
        """
        Write to log file:
        - logs/app.log (general)
        - logs/proposal_generator.log (specific)
        """
```

**File Organization:**

```
proposals/
├── Client_Name_proposal_20240315_143022.txt       (Full proposal)
├── Client_Name_session_20240315_143022.txt         (Session log)
├── Client_Name_changes_20240315_143022.txt         (Change log)
├── Client_Name_summary_20240315_143022.txt         (Summary)
├── example_proposal.txt                            (Example output)
├── Auxo Proposals/                                 (Secondary storage)
└── ...

logs/
├── app.log                                         (General logs)
├── proposal_generator.log                          (Specific logs)
└── ...
```

### 9. **data_models.py** - Data Structures

**Responsibility:** Define data classes with validation

**Key Classes:**

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ClientInfo:
    """Validated client information"""
    name: str              # ≥ 2 chars
    problem: str           # ≥ 20 chars
    solution: str          # ≥ 20 chars
    company: str           # Any length
    
    def __post_init__(self):
        """Validate on creation"""

@dataclass
class Slide:
    """Individual slide representation"""
    slide_type: str        # e.g., "cover", "executive_summary"
    content: str           # Slide text
    generated_at: str      # ISO timestamp
    version: int           # Version number

@dataclass
class ProposalData:
    """Complete proposal state"""
    session_id: str
    client: ClientInfo
    slides: Dict[str, Slide]
    changes: List[Dict]    # Change history
    created_at: str
    updated_at: str
```

### 10. **config.py** - Configuration Management

**Responsibility:** Centralized configuration

```python
# Environment-based configuration
class ProposalConfig:
    # API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Paths
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "proposals")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")
    MEMORY_FILE = os.getenv("MEMORY_FILE", "proposal_agent_memory.json")
    
    # Retry
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))
    
    # Validation
    MIN_CLIENT_NAME_LENGTH = 2
    MIN_PROBLEM_LENGTH = 20
    MIN_SOLUTION_LENGTH = 20
    MAX_RETRIES_SOLUTION = 5
```

---

## 📊 Data Models

### Client Information Flow

```
User Input (Raw)
    ↓
Validation Layer
├─ Check length requirements
├─ Strip whitespace
├─ Check character encoding
└─ Normalize data
    ↓
ClientInfo Data Class
├─ name: str
├─ problem: str
├─ solution: str
└─ company: str
    ↓
Storage (Memory Manager)
└─ Save to JSON
    ↓
Generation (Proposal Agent)
└─ Use for prompts
```

### Slide Generation Data Model

```
Slide Request
├─ slide_type: str
├─ client_info: ClientInfo
├─ solution: str
└─ context: Dict

    ↓

AIGenerator.generate()
├─ Build prompt
├─ Call Gemini API
├─ Parse response
└─ Validate structure

    ↓

Slide Object
├─ slide_type: str
├─ content: str (generated)
├─ generated_at: timestamp
└─ version: int

    ↓

Storage
├─ Memory Manager (JSON)
├─ Output Manager (Files)
└─ Change Tracking
```

### Session State Structure

```json
{
  "session_id": "timestamp_based_id",
  "client": {
    "name": "TechCorp",
    "problem": "...",
    "solution": "...",
    "company": "DataSolutions"
  },
  "slides": {
    "cover": {
      "content": "...",
      "generated_at": "2024-03-15T14:30:25",
      "version": 1
    },
    "executive_summary": {
      "content": "...",
      "generated_at": "2024-03-15T14:30:40",
      "version": 1
    }
  },
  "changes": [
    {
      "timestamp": "2024-03-15T14:30:25",
      "action": "generated_slide",
      "slide_type": "cover"
    }
  ],
  "created_at": "2024-03-15T14:30:22",
  "updated_at": "2024-03-15T14:31:45"
}
```

---

## 💼 Workflow Examples

### Example 1: Complete Interactive Workflow

```bash
$ python main.py
```

**Step 1: Initialization**
```
Checking prerequisites...
✓ API key found
✓ Directories exist
✓ Memory loaded
Starting new session: 20240315_143022
```

**Step 2: Information Collection**
```
--- Client Information ---
Client name: Acme Logistics
Problem: Manual route scheduling causes delays and cost overruns
Solution: AI-driven route optimization system
Company: AuxoAI Solutions
```

**Step 3: Solution Refinement**
```
AI suggests improvements:

Your solution would benefit from:
1. Real-time tracking integration
2. Driver communication system
3. Predictive maintenance alerts
4. Integration with existing dispatch software

Accept these suggestions? (yes/no/edit): yes
✓ Solution finalized
```

**Step 4: Slide Generation**
```
Available commands:
> generate cover
> generate executive_summary
> generate problem_statement
> generate solution_overview
> generate implementation_timeline
> generate pricing
> generate full_deck
> export proposal
> help
> exit

Command: generate cover
✓ Cover slide created

Command: generate executive_summary
✓ Executive summary created

Command: generate full_deck
✓ Generating all slides...
  ✓ Problem statement
  ✓ Solution overview
  ✓ Key benefits
  ✓ Implementation timeline
  ✓ Pricing
  ✓ Case studies
  ✓ Risk mitigation
  ✓ Technical architecture
  ✓ ROI analysis
  ✓ Closing slide

Command: export proposal
✓ Proposal exported successfully
  - proposals/Acme_Logistics_proposal_20240315_143022.txt
  - proposals/Acme_Logistics_session_20240315_143022.txt
  - proposals/Acme_Logistics_changes_20240315_143022.txt

Command: exit
Session ended. Goodbye!
```

### Example 2: Command-Line Quick Start

```bash
python main.py \
  --client "FinanceFlow Inc" \
  --problem "Compliance reporting manually takes 3 weeks per month" \
  --solution "Automated compliance dashboard with real-time reporting" \
  --company "FinTech Automation" \
  --auto-export
```

**Output:**

```
Processing proposal for FinanceFlow Inc...

✓ Session created: 20240315_144532
✓ Client info validated
✓ Solution finalized with AI suggestions
✓ Generating full proposal deck...
  ✓ Cover slide
  ✓ Executive summary
  ✓ Problem statement
  ✓ Solution overview
  ✓ Key benefits
  ✓ Implementation timeline
  ✓ Pricing
  ✓ Case studies
  ✓ Risk mitigation
  ✓ Technical architecture
  ✓ ROI analysis
  ✓ Closing slide

✓ Proposal exported successfully!

Files created:
  - proposals/FinanceFlow_Inc_proposal_20240315_144532.txt
  - proposals/FinanceFlow_Inc_session_20240315_144532.txt
  - proposals/FinanceFlow_Inc_changes_20240315_144532.txt
  - proposals/FinanceFlow_Inc_summary_20240315_144532.txt
```

### Example 3: Batch Processing

```bash
python main.py --batch clients.json
```

**Input (clients.json):**

```json
[
  {
    "client_name": "TechCorp",
    "problem_statement": "Legacy systems integration",
    "tentative_solution": "Cloud migration",
    "company_name": "CloudFirst"
  },
  {
    "client_name": "RetailChain",
    "problem_statement": "Inventory management inefficiencies",
    "tentative_solution": "AI-powered supply chain optimization",
    "company_name": "SupplyChainAI"
  }
]
```

**Output:**

```
Processing batch mode...

[1/2] TechCorp
  ✓ Session: 20240315_145001
  ✓ Proposal generated
  ✓ Files: proposals/TechCorp_*

[2/2] RetailChain
  ✓ Session: 20240315_145032
  ✓ Proposal generated
  ✓ Files: proposals/RetailChain_*

Batch complete! 2 proposals generated in 2 minutes 15 seconds.
```

---

## 🎁 Advanced Features

### Feature 1: Solution Iterative Refinement

The system doesn't just accept the initial solution - it iteratively improves it:

```python
def finalize_solution(solution):
    """
    Loop until user confirms:
    
    Iteration 1:
    - AI suggests: "Add real-time monitoring"
    - User: "edit"
    - Solution updated
    
    Iteration 2:
    - AI suggests: "Include compliance reporting"
    - User: "yes"
    - Solution finalized
    """
```

### Feature 2: Flexible Command Parsing

Commands are parsed intelligently with fuzzy matching:

```
User types: "gen cover"
System recognizes: "generate cover"

User types: "exp prop"
System recognizes: "export proposal"

User types: "gimme timeline"
System suggests: "Did you mean 'generate implementation_timeline'?"
```

### Feature 3: Version Control

Every change is tracked with timestamps:

```
Session: 20240315_143022
├─ 14:30:22 - Session started
├─ 14:30:25 - Cover slide generated (v1)
├─ 14:30:40 - Executive summary generated (v1)
├─ 14:31:02 - Problem statement generated (v1)
├─ 14:31:15 - Solution overview generated (v1) [EDITED]
├─ 14:31:45 - Proposal exported (v2)
└─ 14:32:00 - Session ended
```

### Feature 4: Session Recovery

If interrupted, sessions can be resumed:

```bash
# List previous sessions
python main.py --list-sessions

# Resume a specific session
python main.py --resume 20240315_143022
```

### Feature 5: Content Editing

After generation, slides can be edited:

```
Command: edit slide executive_summary
Current content:
[Displays current content]

Edit? (y/n): y
Enter new content: [User types]
✓ Slide updated

Command: show slide executive_summary
[Displays updated version]
```

---

## 🗄️ Knowledge Graph Pipeline (Optional)

For organizations wanting to store and query proposals, three utilities exist:

### 1. **deck-structurer.py** - Convert to JSON

**Purpose:** Convert raw deck text to structured JSON

```bash
python deck-structurer.py < deck_texts.txt > output.json
```

**Process:**

```
Raw Text Input (deck_texts.txt)
    ↓
Parse sections
├─ Identify headers (COVER, EXECUTIVE SUMMARY, etc.)
├─ Extract content between headers
├─ Clean formatting
└─ Structure as JSON
    ↓
JSON Output (output.json)
```

**Input Format:**

```
COVER SLIDE
Client: TechCorp
Date: 2024-03-15

EXECUTIVE SUMMARY
TechCorp faces significant challenges...

PROBLEM STATEMENT
Manual data processing causes errors...
```

**Output Format:**

```json
[
  {
    "section": "COVER",
    "content": {
      "client": "TechCorp",
      "date": "2024-03-15"
    }
  },
  {
    "section": "EXECUTIVE_SUMMARY",
    "content": "TechCorp faces significant challenges..."
  },
  {
    "section": "PROBLEM_STATEMENT",
    "content": "Manual data processing causes errors..."
  }
]
```

### 2. **storing.py** - Persist to Neo4j

**Purpose:** Store structured proposals in Neo4j

```bash
python storing.py < output.json
```

**Database Schema:**

```
Nodes:
├─ Client
│  ├─ properties: name, industry, contact
│  └─ relationships: [HAS] Proposal
├─ Proposal
│  ├─ properties: title, date, version
│  └─ relationships: [CONTAINS] Section
└─ Section
   ├─ properties: name, content, order
   └─ relationships: [HAS] Phase

Relationships:
├─ Client -[HAS]-> Proposal
├─ Proposal -[CONTAINS]-> Section
└─ Section -[BELONGS_TO]-> Phase
```

**Example Cypher:**

```cypher
// Create client and proposal
CREATE (client:Client {name: "TechCorp"})
CREATE (proposal:Proposal {title: "TechCorp Proposal", date: "2024-03-15"})
CREATE (client)-[:HAS]->(proposal)

// Create sections
CREATE (section:Section {name: "Executive Summary", order: 1})
CREATE (proposal)-[:CONTAINS]->(section)
```

### 3. **fetching.py** - Query with Natural Language

**Purpose:** Query proposals using natural language

```bash
python fetching.py
```

**Interaction:**

```
Natural Language Query: "What proposals do we have for TechCorp?"

System Flow:
1. Send to Gemini: Generate Cypher for this query
2. Generated Cypher:
   MATCH (c:Client {name: "TechCorp"})-[:HAS]->(p:Proposal)
   RETURN p

3. Execute in Neo4j
4. Return results
5. Format for user
```

**Example Queries:**

```
"Show all proposals for fintech companies"
"List proposals from the last 30 days"
"Find proposals with AI solutions"
"Show problem statements for TechCorp"
"Which proposals have been exported?"
```

### 4. **delete_data.py** - Database Cleanup

**Purpose:** Clear Neo4j database (use with caution!)

```bash
python delete_data.py
```

**Warning:**
```
⚠️  This will DELETE ALL data in Neo4j!
Continue? (yes/NO): yes

Deleting all nodes and relationships...
✓ Deleted 15 nodes
✓ Deleted 23 relationships
✓ Database cleared
```

---

## 🛡️ Error Handling & Fallbacks

### Error Handling Strategy

```
Error Type              Handling Strategy
─────────────────────────────────────────────────────────────────
API Connection Error    → Retry with exponential backoff (3x)
                        → If fails, use fallback placeholder
                        → Log error for debugging

Invalid Input           → Display validation error
                        → Re-prompt user
                        → Log invalid attempt

Missing API Key         → Display configuration error
                        → Suggest environment setup
                        → Exit gracefully

File Write Error        → Check directory permissions
                        → Try alternative directory
                        → Log and notify user

JSON Parse Error        → Display parse error
                        → Use default state
                        → Log for debugging

Neo4j Connection Error  → Skip KG features
                        → Continue with main pipeline
                        → Log warning
```

### Retry Logic

```python
def generate_with_retries(prompt, max_retries=3):
    """
    Attempt generation with exponential backoff:
    
    Attempt 1: Immediate
    Attempt 2: Wait 1 second
    Attempt 3: Wait 2 seconds (max_retries reached)
    
    If all fail: Return placeholder content
    """
    for attempt in range(max_retries):
        try:
            return api_call(prompt)
        except APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error("All retries exhausted, using fallback")
                return generate_placeholder(prompt)
```

### Fallback Mechanisms

1. **Missing Gemini API Key:**
   ```
   ⚠️  Warning: GEMINI_API_KEY not configured
   Using placeholder content instead of AI generation
   ```

2. **API Failure:**
   ```
   Placeholder slide generated for: [Slide Type]
   (AI generation unavailable - using template)
   ```

3. **Network Error:**
   ```
   ✓ Retrying API call (1/3)...
   ✓ Retrying API call (2/3)...
   ✗ API unavailable - using fallback content
   ```

---

## 📁 File Structure

```
ai-proposal-generator/
│
├── Core Files
│   ├── main.py                      # CLI entry point
│   ├── cli_interface.py             # User interaction layer
│   ├── conversational_agent.py      # Session orchestrator
│   ├── proposal_agent.py            # Core proposal generation
│   ├── command_parser.py            # Command parsing
│   ├── ai_generator.py              # Gemini API interface
│   ├── memory_manager.py            # State persistence
│   ├── output_manager.py            # File/log management
│   ├── data_models.py               # Data structures
│   └── config.py                    # Configuration
│
├── Knowledge Graph Pipeline (Optional)
│   ├── deck-structurer.py           # Convert deck to JSON
│   ├── storing.py                   # Store in Neo4j
│   ├── fetching.py                  # Query Neo4j
│   ├── delete_data.py               # Clear database
│   └── local_connector.py           # Neo4j connector
│
├── Testing & Utilities
│   ├── test_basic.py                # Basic tests
│   └── generate_user_input.py       # Generate test data
│
├── Configuration
│   ├── .env.sample                  # Environment template
│   ├── requirements.txt             # Python dependencies
│   ├── setup.py                     # Setup assistant
│   └── config.py                    # Config management
│
├── Output Directories (Created)
│   ├── proposals/                   # Generated proposals
│   │   ├── <Client>_proposal_*.txt  # Full proposals
│   │   ├── <Client>_session_*.txt   # Session logs
│   │   ├── <Client>_changes_*.txt   # Change logs
│   │   ├── <Client>_summary_*.txt   # Summaries
│   │   ├── Auxo Proposals/          # Secondary storage
│   │   └── example_proposal.txt     # Example output
│   │
│   └── logs/                        # Application logs
│       ├── app.log                  # General logs
│       └── proposal_generator.log   # Specific logs
│
├── Data & Documentation
│   ├── proposal_agent_memory.json   # Session memory
│   ├── deck_texts.txt               # Sample deck text
│   ├── deck_example.json            # Example JSON
│   ├── demo_deck.json               # Demo data
│   ├── output1.txt                  # KG pipeline output
│   ├── output2.txt                  # KG pipeline output
│   ├── proposals.json               # Batch input example
│   ├── README.md                    # This file
│   └── LICENSE                      # License (if applicable)
│
└── Root Files
    ├── main.py                      # Main entry point
    └── .gitignore                   # Git ignore rules
```

**Key Directories:**

| Directory | Purpose | Created By |
|-----------|---------|-----------|
| `proposals/` | All generated proposal files | OutputManager |
| `logs/` | Application logs | OutputManager |
| `Auxo Proposals/` | Alternative storage location | OutputManager |

**Key Files:**

| File | Purpose | Purpose |
|------|---------|---------|
| `proposal_agent_memory.json` | Session persistence | MemoryManager |
| `app.log` | General application logs | OutputManager |
| `proposal_generator.log` | Proposal-specific logs | OutputManager |

---

## 🧪 Testing & Validation

### 1. Basic Sanity Checks

```bash
# Check system health
python main.py --check
```

**Output:**

```
Performing sanity checks...

✓ Python version: 3.9+
✓ Required packages: google-generativeai, python-dotenv
✓ Gemini API key: CONFIGURED
✓ Output directory: proposals/ (exists)
✓ Logs directory: logs/ (exists)
✓ Memory file: proposal_agent_memory.json (accessible)
✓ File permissions: OK

All checks passed! Ready to use.
```

### 2. Unit Tests

```bash
# Run basic tests
python test_basic.py
```

**Test Coverage:**

```
Testing data models...
✓ ClientInfo validation
✓ Slide creation
✓ ProposalData structure

Testing command parsing...
✓ Valid command recognition
✓ Fuzzy matching
✓ Invalid command handling

Testing memory management...
✓ Save state
✓ Load state
✓ Session recovery

Testing output management...
✓ File writing
✓ Log rotation
✓ Directory creation

Tests complete: 15/15 passed ✓
```

### 3. Example Run

```bash
# Run with hardcoded example
python main.py --example
```

**Generates:**

```
Running example proposal generation...

Proposal: example_proposal.txt

✓ Proposal exported successfully
Files:
  - proposals/TechCorp_Industries_proposal_<timestamp>.txt
  - proposals/TechCorp_Industries_session_<timestamp>.txt
```

### 4. Manual Testing

**Test Case 1: Interactive Mode**
```bash
python main.py
# Follow prompts, test each command
```

**Test Case 2: CLI Arguments**
```bash
python main.py \
  --client "TestCorp" \
  --problem "Test problem statement for validation" \
  --solution "Test solution statement for validation" \
  --company "TestCompany"
```

**Test Case 3: Batch Mode**
```bash
# Create test_batch.json with sample data
python main.py --batch test_batch.json
```

---

## 🔧 Troubleshooting

### Issue 1: "GEMINI_API_KEY not configured"

**Problem:** API key is missing

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Add your API key
echo "GEMINI_API_KEY=your_key_here" >> .env

# Verify
python main.py --check
```

### Issue 2: "ModuleNotFoundError: No module named 'google.generativeai'"

**Problem:** Dependencies not installed

**Solution:**
```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import google.generativeai; print('OK')"
```

### Issue 3: "Permission denied" when writing files

**Problem:** Directory permissions issue

**Solution:**
```bash
# Check directory permissions
ls -ld proposals/ logs/

# Fix permissions
chmod 755 proposals/
chmod 755 logs/

# Verify
python main.py --check
```

### Issue 4: "Neo4j connection failed" (KG pipeline)

**Problem:** Neo4j database not accessible

**Solution:**
```bash
# Verify Neo4j running (if using KG features)
neo4j start

# Check credentials in storing.py, fetching.py
# Update connection details if needed

# The main pipeline works without Neo4j
# KG features are optional
```

### Issue 5: "JSON decode error" in memory file

**Problem:** Corrupted proposal_agent_memory.json

**Solution:**
```bash
# Backup corrupted file
cp proposal_agent_memory.json proposal_agent_memory.json.bak

# Restore from backup or delete
rm proposal_agent_memory.json

# System will recreate on next run
python main.py
```

### Issue 6: "API rate limit exceeded"

**Problem:** Too many API calls to Gemini

**Solution:**
```
# Increase RETRY_DELAY in .env
RETRY_DELAY=5

# Reduce GEMINI_MODEL to cheaper model
GEMINI_MODEL=gemini-1.5-flash

# Or use batch mode with longer intervals
```

### Debugging Tips

```bash
# Run with verbose logging
python main.py --verbose

# Check logs
tail -f logs/app.log
tail -f logs/proposal_generator.log

# Test API connectivity
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('API OK')
"

# List previous sessions
python -c "
from memory_manager import MemoryManager
mm = MemoryManager('proposal_agent_memory.json')
sessions = mm.get_all_sessions()
for s in sessions:
    print(f\"{s['session_id']} - {s['client_name']}\")
"
```

---

## 📚 Advanced Usage Examples

### Example 1: Batch Processing 100 Leads

```bash
# Create leads.json with 100 client entries
python main.py --batch leads.json --parallel 4

# Processes 4 proposals simultaneously
# Generates 100 proposals in ~25 minutes (vs 100 minutes serial)
```

### Example 2: Resume and Update Proposal

```bash
# Resume session
python main.py --resume 20240315_143022

# List current slides
> list slides

# Edit a slide
> edit slide pricing

# Add new slides
> generate roi_analysis

# Export updated version
> export proposal

# Final version includes both original and new slides
```

### Example 3: Generate for Specific Verticals

```bash
# Create vertical-specific batch file
cat > fintech_prospects.json << 'EOF'
[
  {
    "client_name": "FinanceFlow",
    "problem_statement": "Compliance reporting takes 3 weeks",
    "tentative_solution": "Automated compliance dashboard",
    "company_name": "FinTech Solutions"
  },
  {
    "client_name": "CryptoVault",
    "problem_statement": "Security audit trails manual",
    "tentative_solution": "Automated blockchain audit system",
    "company_name": "FinTech Solutions"
  }
]
EOF

# Process with vertical context
python main.py --batch fintech_prospects.json --vertical fintech
```

### Example 4: Query Proposals via Knowledge Graph

```bash
# Store proposals
python storing.py < output.json

# Query proposals
python fetching.py

Natural Language Query: "Show me all proposals with AI solutions"

System generates Cypher, queries Neo4j, returns:
- TechCorp: "AI-driven automation"
- Acme: "Machine learning pipeline"
- FinanceFlow: "AI compliance monitoring"
```

---

## 🎓 Summary

The **AI Client Proposal Deck Generator** provides:

✅ **Automated proposal creation** - From client context to complete deck in minutes

✅ **AI-powered content** - Uses Gemini to generate professional proposal slides

✅ **Iterative refinement** - Improves solutions before finalizing

✅ **Multiple input modes** - Interactive, CLI, batch, and example

✅ **Comprehensive tracking** - Sessions, changes, versions, and audit logs

✅ **Flexible output** - Text files, logs, summaries with timestamps

✅ **Optional knowledge graph** - Store and query proposals with natural language

✅ **Robust error handling** - Fallbacks, retries, and graceful degradation

✅ **Production-ready** - Logging, configuration, validation, and testing

This documentation provides a complete understanding of the system's architecture, usage patterns, and advanced features. Start with interactive mode, then explore CLI arguments and batch processing as you become more familiar with the system.

---

**Version:** 1.0  
**Last Updated:** March 2024  
**Status:** Production-Ready
