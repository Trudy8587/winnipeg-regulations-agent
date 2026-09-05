"""Quick start script for Winnipeg Regulations Agent"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}\n")


def check_python():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor} OK\n")
        return True
    else:
        print(f"✗ Python 3.9+ required (found {version.major}.{version.minor})\n")
        return False


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✓ .env file found\n")
        return True
    else:
        print("✗ .env file not found")
        env_example = Path(".env.example")
        if env_example.exists():
            print("  Creating .env from .env.example...")
            env_path.write_text(env_example.read_text())
            print("✓ .env file created (please edit with your API keys)\n")
            return False
        else:
            print("✗ .env.example not found\n")
            return False


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
        capture_output=True
    )
    if result.returncode == 0:
        print("✓ Dependencies installed\n")
        return True
    else:
        print("✗ Failed to install dependencies")
        print(result.stderr.decode())
        return False


def validate_config():
    """Validate configuration"""
    print("Validating configuration...")
    
    result = subprocess.run(
        [sys.executable, "scripts/validate_config.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    return result.returncode == 0


def start_server():
    """Start the API server"""
    print_header("Starting API Server")
    
    print("API Server starting on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs\n")
    print("Press CTRL+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")


def main():
    """Main setup flow"""
    print_header("Winnipeg Regulations Agent - Quick Start")
    
    # Check Python
    if not check_python():
        return 1
    
    # Check .env file
    env_exists = check_env_file()
    if not env_exists:
        print("⚠️  Please edit .env file with your API keys before proceeding:")
        print("  - OPENAI_API_KEY")
        print("  - PINECONE_API_KEY")
        print("  - PINECONE_ENVIRONMENT")
        print("  - PINECONE_INDEX_NAME\n")
        print("Then run this script again.\n")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Validate configuration
    if not validate_config():
        print("\n⚠️  Configuration validation failed.")
        print("Please check your .env file and try again.\n")
        return 1
    
    # Start server
    start_server()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
