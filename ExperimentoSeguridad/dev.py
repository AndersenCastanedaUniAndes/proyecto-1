#!/usr/bin/env python3
"""
Development script for Experimento Seguridad.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def setup_development():
    """Set up development environment."""
    print("🚀 Setting up development environment...")
    
    # Install dependencies
    if not run_command("pip install -e .[dev]", "Installing dependencies"):
        return False
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    print("✅ Development environment ready!")
    return True


def run_tests():
    """Run test suite."""
    print("🧪 Running tests...")
    
    # Run pytest
    if not run_command("pytest -v", "Running pytest"):
        return False
    
    print("✅ All tests passed!")
    return True


def run_quality_checks():
    """Run code quality checks."""
    print("🔍 Running quality checks...")
    
    # Black formatting
    if not run_command("black app/ tests/ --check", "Checking Black formatting"):
        print("💡 Run 'black app/ tests/' to fix formatting issues")
        return False
    
    # Ruff linting
    if not run_command("ruff check app/ tests/", "Running Ruff linting"):
        print("💡 Run 'ruff check app/ tests/ --fix' to fix linting issues")
        return False
    
    print("✅ All quality checks passed!")
    return True


def run_application():
    """Run the application locally."""
    print("🚀 Starting application...")
    
    # Set environment variables
    env = {
        "DATABASE_URL": "sqlite:///./users.db",
        "REDIS_URL": "redis://localhost:6379/0",
        "PROMETHEUS_ENABLED": "true",
        "WEB_CONCURRENCY": "1"
    }
    
    # Start uvicorn
    cmd = "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    print(f"Running: {cmd}")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run(cmd, shell=True, env={**env, **dict(os.environ)})
    except KeyboardInterrupt:
        print("\n👋 Application stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Experimento Seguridad Development Script")
    parser.add_argument("command", choices=["setup", "test", "quality", "run"], 
                       help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        success = setup_development()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "quality":
        success = run_quality_checks()
    elif args.command == "run":
        run_application()
        return
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import os
    main()
