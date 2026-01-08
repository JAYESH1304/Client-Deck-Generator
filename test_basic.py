#!/usr/bin/env python3
"""
Basic functionality test for AI Proposal Deck Generator.
Tests core functionality without requiring full initialization.
"""

import os
import sys

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        'config',
        'data_models', 
        'memory_manager',
        'ai_generator',
        'output_manager',
        'command_parser',
        'proposal_agent',
        'conversational_agent',
        'cli_interface'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            failed_imports.append((module, str(e)))
    
    return failed_imports

def test_basic_functionality():
    """Test basic functionality without full initialization."""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test data models
        from data_models import ProposalMemory, Slide, PROPOSAL_COMPONENTS
        
        memory = ProposalMemory(
            client_name="Test Client",
            problem_statement="Test problem",
            current_solution="Test solution"
        )
        print("✅ Data models working")
        
        # Test command parser
        from command_parser import FlexibleCommandParser
        
        parser = FlexibleCommandParser()
        command = parser.parse_command("generate full deck")
        print(f"✅ Command parser working: {command['action']}")
        
        # Test AI generator (will use fallback)
        from ai_generator import AIGenerator
        
        generator = AIGenerator()  # Should work even without API key
        status = generator.get_status()
        print(f"✅ AI generator initialized: {'Ready' if status['ready'] else 'Fallback mode'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_proposal_agent():
    """Test proposal agent creation."""
    print("\n🤖 Testing proposal agent...")
    
    try:
        from proposal_agent import ProposalAgent
        
        agent = ProposalAgent(
            client_name="Test Corp",
            problem_statement="Testing the proposal system functionality",
            tentative_solution="Create a comprehensive test suite for validation",
            company_name="Test Solutions"
        )
        
        print("✅ Proposal agent created")
        
        # Test basic methods
        status = agent.get_proposal_status()
        print(f"✅ Status method working: {status['client_name']}")
        
        # Test solution finalization
        agent.finalize_solution()
        print("✅ Solution finalized")
        
        # Test component addition
        agent.add_component("risk_management")
        print("✅ Component addition working")
        
        return True
        
    except Exception as e:
        print(f"❌ Proposal agent test failed: {e}")
        return False

def test_file_operations():
    """Test file operations."""
    print("\n📁 Testing file operations...")
    
    try:
        # Create test directories
        os.makedirs("test_proposals", exist_ok=True)
        os.makedirs("test_logs", exist_ok=True)
        print("✅ Directory creation working")
        
        # Test file writing
        test_content = "This is a test file for the proposal generator."
        
        with open("test_proposals/test.txt", "w") as f:
            f.write(test_content)
        print("✅ File writing working")
        
        # Test file reading
        with open("test_proposals/test.txt", "r") as f:
            content = f.read()
        
        if content == test_content:
            print("✅ File reading working")
        else:
            print("❌ File reading failed")
            return False
        
        # Cleanup
        os.remove("test_proposals/test.txt")
        os.rmdir("test_proposals")
        os.rmdir("test_logs")
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_conversational_agent():
    """Test conversational agent creation."""
    print("\n💬 Testing conversational agent...")
    
    try:
        from conversational_agent import ConversationalAgent
        
        agent = ConversationalAgent(
            client_name="Test Client",
            problem_statement="Test problem for conversational agent",
            tentative_solution="Test solution approach",
            company_name="Test Company"
        )
        
        print("✅ Conversational agent created")
        
        # Check if it has required methods
        required_methods = ['process_comment', 'run_conversation', 'get_session_summary']
        
        for method in required_methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Conversational agent test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI Proposal Deck Generator - Basic Tests")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    failed_imports = test_imports()
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} import failures detected")
        for module, error in failed_imports:
            print(f"  • {module}: {error}")
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    # Test file operations
    if not test_file_operations():
        all_passed = False
    
    # Test proposal agent
    if not test_proposal_agent():
        all_passed = False
    
    # Test conversational agent
    if not test_conversational_agent():
        all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! The system should work correctly.")
        print("\n💡 Try running:")
        print("  python main.py --example")
        print("  python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("  • Run: python setup.py")
        print("  • Check file permissions")
        print("  • Install dependencies: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)