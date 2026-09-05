#!/usr/bin/env python3
"""
Configuration validation script for Winnipeg Regulations Agent.

Run this script to verify all environment variables are properly configured.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    """Print formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_check(status, message, details=""):
    """Print formatted check result"""
    if status:
        icon = f"{GREEN}✓{RESET}"
    else:
        icon = f"{RED}✗{RESET}"
    
    print(f"{icon} {message}")
    if details:
        print(f"  {details}")


def check_env_file():
    """Check if .env file exists"""
    print_header("Environment File Check")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print_check(True, ".env file exists")
        return True
    else:
        print_check(False, ".env file not found")
        if env_example_path.exists():
            print(f"\n  {YELLOW}To fix this, run:{RESET}")
            print(f"  cp .env.example .env")
        return False


def check_openai_config():
    """Check OpenAI configuration"""
    print_header("OpenAI Configuration")
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    temperature = os.getenv("OPENAI_TEMPERATURE", "0.1")
    
    if not api_key:
        print_check(False, "OPENAI_API_KEY not set")
        return False
    
    if not api_key.startswith("sk-"):
        print_check(False, "OPENAI_API_KEY invalid format (should start with 'sk-')")
        return False
    
    # Show masked key
    masked_key = api_key[:20] + "..." + api_key[-4:]
    print_check(True, f"OPENAI_API_KEY configured", f"Key: {masked_key}")
    print_check(True, f"OPENAI_MODEL: {model}")
    print_check(True, f"OPENAI_TEMPERATURE: {temperature}")
    
    return True


def check_pinecone_config():
    """Check Pinecone configuration"""
    print_header("Pinecone Configuration")
    
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    all_set = True
    
    if not api_key:
        print_check(False, "PINECONE_API_KEY not set")
        all_set = False
    else:
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print_check(True, f"PINECONE_API_KEY configured", f"Key: {masked_key}")
    
    if not environment:
        print_check(False, "PINECONE_ENVIRONMENT not set")
        all_set = False
    else:
        print_check(True, f"PINECONE_ENVIRONMENT: {environment}")
    
    if not index_name:
        print_check(False, "PINECONE_INDEX_NAME not set")
        all_set = False
    else:
        print_check(True, f"PINECONE_INDEX_NAME: {index_name}")
    
    return all_set


def check_database_config():
    """Check database configuration"""
    print_header("Database Configuration")
    
    db_url = os.getenv("DATABASE_URL", "sqlite:///./winnipeg_agent.db")
    print_check(True, f"DATABASE_URL configured", f"URL: {db_url}")
    
    return True


def check_api_config():
    """Check API configuration"""
    print_header("API Configuration")
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", "8000")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print_check(True, f"API_HOST: {host}")
    print_check(True, f"API_PORT: {port}")
    print_check(True, f"DEBUG: {debug}")
    
    return True


def check_agent_config():
    """Check agent configuration"""
    print_header("Agent Configuration")
    
    agent_name = os.getenv("AGENT_NAME", "Winnipeg Regulations Assistant")
    agent_desc = os.getenv("AGENT_DESCRIPTION", "AI-powered assistant")
    
    print_check(True, f"AGENT_NAME: {agent_name}")
    print_check(True, f"AGENT_DESCRIPTION: {agent_desc[:50]}...")
    
    return True


def test_imports():
    """Test if required packages can be imported"""
    print_header("Package Dependencies")
    
    packages = [
        ("langchain", "LangChain"),
        ("openai", "OpenAI"),
        ("pinecone", "Pinecone"),
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("dotenv", "python-dotenv"),
    ]
    
    all_ok = True
    for package, name in packages:
        try:
            __import__(package)
            print_check(True, f"{name} is installed")
        except ImportError:
            print_check(False, f"{name} is NOT installed")
            all_ok = False
    
    if not all_ok:
        print(f"\n  {YELLOW}To fix this, run:{RESET}")
        print(f"  pip install -r requirements.txt\n")
    
    return all_ok


def test_connections():
    """Test actual API connections"""
    print_header("API Connection Tests")
    
    # Test OpenAI
    print(f"{BOLD}Testing OpenAI Connection...{RESET}")
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print_check(False, "OpenAI API key not configured")
        else:
            client = OpenAI(api_key=api_key)
            # Simple test call
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "Say 'test'"}
                ],
                max_tokens=10
            )
            print_check(True, "OpenAI connection successful")
    except Exception as e:
        print_check(False, f"OpenAI connection failed: {str(e)[:50]}")
    
    # Test Pinecone
    print(f"\n{BOLD}Testing Pinecone Connection...{RESET}")
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print_check(False, "Pinecone API key not configured")
        else:
            pc = Pinecone(api_key=api_key)
            indexes = pc.list_indexes()
            print_check(True, f"Pinecone connection successful ({len(indexes)} indexes found)")
    except Exception as e:
        print_check(False, f"Pinecone connection failed: {str(e)[:50]}")


def main():
    """Run all configuration checks"""
    print(f"\n{BOLD}{BLUE}Winnipeg Regulations Agent - Configuration Validator{RESET}\n")
    
    results = []
    
    # Basic checks
    results.append(("Environment File", check_env_file()))
    
    if results[0][1]:  # Only proceed if .env exists
        results.append(("OpenAI Config", check_openai_config()))
        results.append(("Pinecone Config", check_pinecone_config()))
        results.append(("Database Config", check_database_config()))
        results.append(("API Config", check_api_config()))
        results.append(("Agent Config", check_agent_config()))
        results.append(("Dependencies", test_imports()))
        
        # Optional connection tests
        try:
            test_connections()
        except Exception as e:
            print(f"\n{YELLOW}Skipping connection tests (some packages not installed){RESET}")
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status}: {check_name}")
    
    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{BOLD}✓ All configurations are correct!{RESET}")
        print(f"\n{BOLD}Next steps:{RESET}")
        print(f"  1. Start the API server:")
        print(f"     python -m uvicorn src.api.main:app --reload")
        print(f"  2. Open http://localhost:8000/docs for interactive API docs")
        print(f"  3. Load regulation data:")
        print(f"     python scripts/load_regulations.py\n")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some configurations are missing!{RESET}")
        print(f"\n{BOLD}Please fix the issues above and try again.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
