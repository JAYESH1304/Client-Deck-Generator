#!/usr/bin/env python3
"""
Setup script for AI Proposal Deck Generator.
Creates necessary directories and validates environment.
"""

import os
import sys
import logging

def create_directories():
    """Create necessary directories."""
    directories = ['proposals', 'logs']
    
    print("🔧 Setting up directories...")
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required, found {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = ['google.generativeai']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Package installed: {package}")
        except ImportError:
            print(f"❌ Package missing: {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"pip install google-generativeai")
        return False
    
    return True

def check_api_key():
    """Check if API key is configured."""
    print("🔑 Checking API key...")
    
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("⚠️  GEMINI_API_KEY environment variable not set")
        print("💡 Set it with:")
        print("   Windows: set GEMINI_API_KEY=your_api_key_here")
        print("   Mac/Linux: export GEMINI_API_KEY=your_api_key_here")
        print("   Get API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ API key is configured")
    return True

def test_logging():
    """Test logging functionality."""
    print("📝 Testing logging...")
    
    try:
        # Clear any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/setup_test.log', mode='w')
            ],
            force=True
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Logging test successful")
        
        print("✅ Logging system working")
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def create_sample_config():
    """Create a sample configuration file."""
    print("⚙️  Creating sample configuration...")
    
    sample_config = '''# Sample environment configuration for AI Proposal Deck Generator

# Required: Get your API key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Optional configurations
GEMINI_MODEL=gemini-1.5-flash
OUTPUT_DIR=proposals
LOGS_DIR=logs
LOG_LEVEL=INFO
MAX_RETRIES=3
RETRY_DELAY=1

# Usage:
# 1. Replace 'your_api_key_here' with your actual Gemini API key
# 2. On Windows: Copy these lines to a .bat file and run it
#    set GEMINI_API_KEY=your_actual_api_key
#    python main.py
# 3. On Mac/Linux: Copy these lines to your .bashrc or .zshrc
#    export GEMINI_API_KEY=your_actual_api_key
'''
    
    try:
        with open('.env.sample', 'w') as f:
            f.write(sample_config)
        print("✅ Created .env.sample with configuration template")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample config: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 AI Proposal Deck Generator - Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Test logging
    if not test_logging():
        success = False
    
    # Check dependencies
    if not check_dependencies():
        success = False
    
    # Check API key
    api_key_ok = check_api_key()
    
    # Create sample config
    create_sample_config()
    
    print("\n" + "=" * 50)
    
    if success and api_key_ok:
        print("🎉 Setup completed successfully!")
        print("You can now run: python main.py")
    elif success:
        print("⚠️  Setup mostly completed, but API key needs configuration")
        print("The application will run in fallback mode without AI features")
        print("You can still run: python main.py")
    else:
        print("❌ Setup encountered issues. Please resolve them before running.")
    
    print("\n💡 Quick commands to try:")
    print("  python main.py --check     # Check system status")
    print("  python main.py --example   # Run example generation")
    print("  python main.py             # Start interactive mode")

if __name__ == "__main__":
    main()