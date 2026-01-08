#!/usr/bin/env python3
"""
Main entry point for the AI Proposal Deck Generator.
Handles command line arguments and application modes.
"""

import sys
import argparse
import logging
from typing import Optional

# Import application modules
from cli_interface import ProposalDeckCLI, run_example
from config import check_system_requirements, config_manager

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('proposal_generator.log', mode='a')
        ]
    )

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='AI Proposal Deck Generator - Create professional business proposals with AI assistance',
        epilog="""
Examples:
  python main.py                              # Interactive mode (default)
  python main.py --client "Acme Corp" --problem "High costs" --solution "AI automation"
  python main.py --batch proposals.json      # Batch processing
  python main.py --example                   # Run example generation
  python main.py --check                     # Check system requirements
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main operation modes
    parser.add_argument(
        '--client', 
        help='Client name for quick start mode'
    )
    parser.add_argument(
        '--problem', 
        help='Problem statement for quick start mode'
    )
    parser.add_argument(
        '--solution', 
        help='Tentative solution for quick start mode'
    )
    parser.add_argument(
        '--company', 
        default='Your Company', 
        help='Your company name (default: Your Company)'
    )
    
    # Alternative modes
    parser.add_argument(
        '--batch', 
        metavar='FILE',
        help='JSON file with multiple proposals for batch processing'
    )
    parser.add_argument(
        '--example', 
        action='store_true',
        help='Run example proposal generation for testing'
    )
    
    # System utilities
    parser.add_argument(
        '--check', 
        action='store_true',
        help='Check system requirements and configuration'
    )
    parser.add_argument(
        '--config', 
        action='store_true',
        help='Show current configuration'
    )
    
    # Options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip banner display in interactive mode'
    )
    
    return parser

def show_config():
    """Display current configuration."""
    config = config_manager.get_config()
    is_valid, issues = config_manager.validate()
    
    print("🔧 CONFIGURATION STATUS")
    print("=" * 40)
    print(f"Status: {'✅ Valid' if is_valid else '❌ Issues Found'}")
    print(f"API Key: {'✅ Configured' if config.api_key else '❌ Missing'}")
    print(f"Model: {config.model}")
    print(f"Memory File: {config.memory_file}")
    print(f"Max Retries: {config.max_retries}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Logs Directory: {config.logs_dir}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
        
        print(f"\n💡 SOLUTIONS:")
        if "GEMINI_API_KEY" in str(issues):
            print("  • Set GEMINI_API_KEY environment variable")
            print("  • Get API key from: https://makersuite.google.com/app/apikey")
        
        if "google.generativeai" in str(issues):
            print("  • Install: pip install google-generativeai")

def validate_quick_start_args(args) -> bool:
    """Validate arguments for quick start mode."""
    if args.client and not args.problem:
        print("❌ Error: --problem is required when using --client")
        return False
    
    if args.client and not args.solution:
        print("❌ Error: --solution is required when using --client")
        return False
    
    return True

def run_interactive_mode(no_banner: bool = False):
    """Run interactive mode."""
    cli = ProposalDeckCLI()
    
    if not no_banner:
        cli.display_banner()
    
    cli.run_interactive_mode()

def run_quick_start_mode(client: str, problem: str, solution: str, company: str):
    """Run quick start mode with provided parameters."""
    print(f"🚀 Quick Start Mode: {client}")
    print("-" * 50)
    
    cli = ProposalDeckCLI()
    cli.run_quick_start(client, problem, solution, company)

def run_batch_mode(batch_file: str):
    """Run batch processing mode."""
    cli = ProposalDeckCLI()
    cli.run_batch_mode(batch_file)

def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Handle utility commands first
        if args.check:
            print("🔍 SYSTEM REQUIREMENTS CHECK")
            print("=" * 40)
            if check_system_requirements():
                print("\n✅ All requirements satisfied!")
            else:
                print("\n❌ Please address the issues above.")
            return
        
        if args.config:
            show_config()
            return
        
        if args.example:
            run_example()
            return
        
        # Handle main operation modes
        if args.batch:
            run_batch_mode(args.batch)
            return
        
        if args.client:
            if not validate_quick_start_args(args):
                return
            
            run_quick_start_mode(args.client, args.problem, args.solution, args.company)
            return
        
        # Default to interactive mode
        run_interactive_mode(args.no_banner)
    
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Unexpected error: {e}")
        
        if args.verbose:
            import traceback
            traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    main()