"""
Enhanced CLI interface for the AI Proposal Deck Generator.
Provides user-friendly command line interaction and error handling.
"""

import os
import sys
import json
import logging
from typing import Tuple, List, Dict, Any
from datetime import datetime

from conversational_agent import ConversationalAgent
from config import check_system_requirements, config_manager
from data_models import ProposalMemory

logger = logging.getLogger(__name__)

class ProposalDeckCLI:
    """Enhanced CLI interface for proposal deck generation."""
    
    def __init__(self):
        self.agent = None
        self.output_manager = None
    
    def display_banner(self):
        """Display application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                  🚀 AI PROPOSAL DECK GENERATOR                   ║
║                                                                  ║
║  Create professional business proposals with AI assistance       ║
║  Features: Natural language commands, solution refinement,       ║
║           flexible slide structure, automatic file output       ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def get_user_inputs(self) -> Tuple[str, str, str, str]:
        """Get initial user inputs with validation and guidance."""
        print("Let's create a professional proposal deck for your client!")
        print("I'll guide you through the setup process.\n")
        
        # Get client name
        print("📋 STEP 1: Client Information")
        while True:
            client_name = input("Enter your client's name: ").strip()
            if client_name and len(client_name) >= 2:
                break
            print("❌ Please enter a valid client name (at least 2 characters).")
        
        # Get problem statement
        print(f"\n🎯 STEP 2: Problem Statement")
        print("Describe the main challenge or problem your client faces.")
        print("Example: 'High operational costs due to manual processes'")
        
        while True:
            problem_statement = input("Problem statement: ").strip()
            if problem_statement and len(problem_statement) >= 20:
                break
            print("❌ Please provide a more detailed problem statement (at least 20 characters).")
            print("Tip: Include the business impact and scope of the problem.")
        
        # Get tentative solution
        print(f"\n💡 STEP 3: Solution Approach")
        print("Describe your proposed solution or approach.")
        print("Example: 'Automated workflow system with AI-powered optimization'")
        print("Note: We'll refine this together using AI suggestions.")
        
        while True:
            tentative_solution = input("Your solution approach: ").strip()
            if tentative_solution and len(tentative_solution) >= 20:
                break
            print("❌ Please provide a more detailed solution description (at least 20 characters).")
            print("Tip: Include key technologies, methods, or approaches you plan to use.")
        
        # Get company name
        print(f"\n🏢 STEP 4: Your Company")
        company_name = input("Your company name (press Enter for 'Your Company'): ").strip()
        if not company_name:
            company_name = "Your Company"
        
        return client_name, problem_statement, tentative_solution, company_name
    
    def display_setup_summary(self, client_name: str, problem_statement: str, 
                             tentative_solution: str, company_name: str):
        """Display setup summary for user confirmation."""
        print("\n" + "="*80)
        print("📋 PROPOSAL SETUP SUMMARY")
        print("="*80)
        print(f"Client:    {client_name}")
        print(f"Company:   {company_name}")
        print(f"Problem:   {problem_statement}")
        print(f"Solution:  {tentative_solution}")
        print("="*80)
        
        confirm = input("\n✅ Does this look correct? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '']:
            print("\n🔄 Let's start over...")
            return False
        
        return True
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites and configuration."""
        print("\n🔍 Checking system requirements...")
        
        if not check_system_requirements():
            print("\n❌ System requirements not met. Please address the issues above.")
            
            # Show setup instructions
            self._show_setup_instructions()
            return False
        
        # Check configuration
        is_valid, issues = config_manager.validate()
        
        if not is_valid:
            print("\n⚠️  Configuration issues detected:")
            for issue in issues:
                print(f"  • {issue}")
            
            if "GEMINI_API_KEY" in str(issues):
                print("\n💡 The application will run in fallback mode without AI generation.")
                print("   To enable AI features, set your GEMINI_API_KEY environment variable.")
                
                continue_anyway = input("\nContinue without AI generation? (y/n): ").strip().lower()
                if continue_anyway not in ['y', 'yes']:
                    self._show_setup_instructions()
                    return False
        
        # Setup directories
        config_manager.setup_directories()
        print("✅ System check completed!")
        return True
    
    def _show_setup_instructions(self):
        """Show setup instructions for prerequisites."""
        print("""
🛠️  SETUP INSTRUCTIONS

1. Install Python 3.7+
2. Install required packages:
   pip install google-generativeai

3. Get Gemini API Key:
   - Visit: https://makersuite.google.com/app/apikey
   - Create new API key
   - Set environment variable:
     
     Windows: set GEMINI_API_KEY=your_api_key_here
     Mac/Linux: export GEMINI_API_KEY=your_api_key_here

4. Run the application again

For detailed setup guide, visit: https://github.com/your-repo/setup-guide
""")
    
    def handle_initialization_error(self, error: Exception):
        """Handle agent initialization errors gracefully."""
        error_str = str(error).lower()
        
        if "api" in error_str or "key" in error_str:
            print("\n❌ AI API Error: Please check your GEMINI_API_KEY environment variable.")
            print("The application will run in fallback mode with limited AI capabilities.")
        elif "network" in error_str or "connection" in error_str:
            print("\n❌ Network Error: Please check your internet connection and try again.")
        elif "permission" in error_str:
            print("\n❌ Permission Error: Please check write permissions in current directory.")
        else:
            print(f"\n❌ Initialization Error: {error}")
            print("The agent will run in fallback mode with limited capabilities.")
        
        print("\n💡 You can still:")
        print("  • Create proposal structure")
        print("  • Generate placeholder content")
        print("  • Export proposal templates")
    
    def run_interactive_mode(self):
        """Run the main interactive mode."""
        self.display_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        try:
            # Get user inputs with confirmation loop
            while True:
                client_name, problem_statement, tentative_solution, company_name = self.get_user_inputs()
                
                if self.display_setup_summary(client_name, problem_statement, tentative_solution, company_name):
                    break
            
            # Initialize conversational agent
            print("\n⏳ Initializing AI Agent...")
            
            try:
                conv_agent = ConversationalAgent(
                    client_name=client_name,
                    problem_statement=problem_statement, 
                    tentative_solution=tentative_solution,
                    company_name=company_name
                )
                
                # Verify the agent is properly initialized
                if not hasattr(conv_agent, 'run_conversation'):
                    print("⚠️  Agent initialization incomplete, but continuing...")
                    self._run_basic_mode(conv_agent)
                    return
                
                print("✅ AI Agent initialized successfully!")
                
                # Run conversation
                conv_agent.run_conversation()
                
                # Show final summary
                self.show_session_summary(conv_agent)
                
            except Exception as e:
                self.handle_initialization_error(e)
                
                # Try to create a basic agent for fallback
                try:
                    print("\n🔧 Attempting fallback mode...")
                    from proposal_agent import ProposalAgent
                    
                    basic_agent = ProposalAgent(client_name, problem_statement, tentative_solution, company_name)
                    print("✅ Basic agent created. Limited functionality available.")
                    
                    # Simple interaction loop
                    while True:
                        cmd = input("\nCommands: 'finalize', 'generate', 'export', 'exit': ").strip().lower()
                        if cmd == 'exit':
                            break
                        elif cmd == 'finalize':
                            basic_agent.finalize_solution()
                            print("✅ Solution finalized")
                        elif cmd == 'generate':
                            try:
                                slides = basic_agent.generate_proposal_deck()
                                print(f"✅ Generated {len(slides)} slides")
                            except Exception as e:
                                print(f"❌ Error: {e}")
                        elif cmd == 'export':
                            try:
                                content = basic_agent.export_deck_content()
                                with open(f"{client_name.replace(' ', '_')}_fallback.txt", 'w') as f:
                                    f.write(content)
                                print("✅ Exported to file")
                            except Exception as e:
                                print(f"❌ Export error: {e}")
                
                except Exception as e2:
                    print(f"❌ Fallback mode also failed: {e2}")
                    return
                
        except KeyboardInterrupt:
            print("\n\n👋 Application interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logger.error(f"CLI application error: {e}")
    
    def run_batch_mode(self, batch_file: str):
        """Run batch processing mode."""
        try:
            print(f"📦 Running batch mode with file: {batch_file}")
            
            if not os.path.exists(batch_file):
                print(f"❌ Batch file not found: {batch_file}")
                return
            
            with open(batch_file, 'r', encoding='utf-8') as f:
                proposals = json.load(f)
            
            if not isinstance(proposals, list):
                print("❌ Batch file must contain a list of proposal objects.")
                return
            
            print(f"Found {len(proposals)} proposals to process...")
            
            results = []
            for i, proposal_data in enumerate(proposals, 1):
                try:
                    self._process_batch_proposal(i, proposal_data, results)
                except Exception as e:
                    error_msg = f"❌ Failed to process proposal {i}: {e}"
                    print(error_msg)
                    results.append({"proposal": i, "status": "failed", "error": str(e)})
            
            # Summary
            successful = sum(1 for r in results if r.get("status") == "success")
            print(f"\n📊 Batch processing complete: {successful}/{len(proposals)} successful")
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
    
    def _process_batch_proposal(self, index: int, proposal_data: dict, results: list):
        """Process single proposal in batch mode."""
        required_fields = ['client_name', 'problem_statement', 'tentative_solution']
        
        # Validate proposal data
        for field in required_fields:
            if field not in proposal_data:
                raise ValueError(f"Missing required field: {field}")
        
        print(f"\n{index}. Processing: {proposal_data['client_name']}")
        
        # Initialize agent
        from proposal_agent import ProposalAgent
        
        agent = ProposalAgent(
            client_name=proposal_data['client_name'],
            problem_statement=proposal_data['problem_statement'],
            tentative_solution=proposal_data['tentative_solution'],
            company_name=proposal_data.get('company_name', 'Your Company')
        )
        
        # Auto-finalize solution for batch mode
        agent.finalize_solution()
        
        # Generate deck
        slides = agent.generate_proposal_deck()
        
        # Export
        content = agent.export_deck_content()
        filename = f"batch_{index}_{proposal_data['client_name'].replace(' ', '_')}_proposal.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated: {filename}")
        
        results.append({
            "proposal": index,
            "status": "success",
            "client": proposal_data['client_name'],
            "file": filename,
            "slides": len(slides)
        })
    
    def run_quick_start(self, client: str, problem: str, solution: str, company: str = "Your Company"):
        """Run quick start mode with provided parameters."""
        try:
            print(f"🚀 Quick start mode for {client}")
            
            conv_agent = ConversationalAgent(client, problem, solution, company)
            conv_agent.run_conversation()
            
        except Exception as e:
            print(f"❌ Quick start failed: {e}")
    
    def show_session_summary(self, conv_agent: ConversationalAgent):
        """Show final session summary."""
        try:
            summary = conv_agent.get_session_summary()
            
            print("\n" + "="*80)
            print("🎉 SESSION COMPLETED SUCCESSFULLY!")
            print("="*80)
            print(summary)
            
            # Show file locations
            stats = conv_agent.output_manager.get_session_stats()
            print("📁 FILES CREATED:")
            print(f"  • Session log: {stats['session_file']}")
            if stats['changes_exists']:
                print(f"  • Changes log: {stats['changes_file']}")
            
            print("\n🎯 NEXT STEPS:")
            status = conv_agent.agent.get_proposal_status()
            
            if status['completion_rate'] < 100:
                print("  • Complete remaining sections")
                print("  • Review and refine existing content")
            else:
                print("  • Review the complete proposal")
                print("  • Customize formatting for client presentation")
                print("  • Add company branding and visuals")
            
            print("\n💡 TIP: You can restart the session anytime to continue editing!")
            print("👋 Thank you for using AI Proposal Deck Generator!")
            
        except Exception as e:
            print(f"❌ Error creating session summary: {e}")

def run_example():
    """Run example proposal generation for testing."""
    print("🧪 Running example proposal generation...")
    
    example_data = {
        'client_name': 'TechCorp Industries',
        'problem_statement': 'Manual data processing causing delays and errors in financial reporting, leading to compliance risks and operational inefficiencies',
        'tentative_solution': 'Automated data pipeline with AI-powered validation, real-time reporting dashboard, and integrated compliance monitoring',
        'company_name': 'DataSolutions Pro'
    }
    
    try:
        from conversational_agent import ConversationalAgent
        
        agent = ConversationalAgent(**example_data)
        print("✅ Example agent created successfully!")
        
        # Auto-generate a few key slides for demo
        test_components = ['executive_summary', 'solution_approach', 'value_proposition']
        
        for component in test_components:
            try:
                slide, _ = agent.agent.generate_slide(component)
                print(f"✅ Generated {slide.title} ({slide.get_word_count()} words)")
            except Exception as e:
                print(f"❌ Failed to generate {component}: {e}")
        
        # Export example
        content = agent.agent.export_deck_content()
        with open("example_proposal.txt", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Example proposal saved to: example_proposal.txt")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")